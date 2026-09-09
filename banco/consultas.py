"""
Funções de acesso ao banco SQLite usadas pela API (app.py).

Tudo aqui é CONSULTA A BANCO (filtros, agregações) — não é IA.
A única ponte com a IA é `historico_tutor`, que transforma as compras
registradas na loja nas features de comportamento que o modelo consome.
"""
import os
import sqlite3
from datetime import date, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.join(AQUI, "patasperto.db")

GRUPOS_IA = ["alimentacao", "petisco", "higiene", "brinquedo", "pele", "bucal", "articular"]
JANELA_DIAS = 90  # janela de histórico usada para calcular o comportamento de compra


def conectar():
    con = sqlite3.connect(CAMINHO_DB)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


# ------------------------------------------------------------------ loja
def listar_ofertas():
    """Todas as ofertas com produto (características, avaliações) e loja embutidos."""
    with conectar() as con:
        produtos = {}
        for r in con.execute("SELECT * FROM produtos"):
            produtos[r["id"]] = dict(r) | {"caracteristicas": [], "comentarios": []}
        for r in con.execute("SELECT * FROM caracteristicas"):
            produtos[r["produto_id"]]["caracteristicas"].append([r["rotulo"], r["valor"]])
        for r in con.execute("SELECT * FROM avaliacoes"):
            produtos[r["produto_id"]]["comentarios"].append(
                {"autor": r["autor"], "nota": r["nota"], "texto": r["texto"]})
        lojas = {r["id"]: dict(r) for r in con.execute("SELECT * FROM lojas")}
        ofertas = []
        for r in con.execute("SELECT * FROM ofertas ORDER BY id"):
            ofertas.append({
                "id": r["id"], "preco": r["preco"], "entrega": r["entrega"],
                "produto": produtos[r["produto_id"]], "loja": lojas[r["loja_id"]],
            })
        return ofertas


def obter_oferta(oferta_id):
    with conectar() as con:
        r = con.execute("SELECT * FROM ofertas WHERE id=?", (oferta_id,)).fetchone()
        return dict(r) if r else None


# -------------------------------------------------------------- clínicas
def _minutos(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def clinica_aberta(clinica, hora):
    """Regra de horário: trata 24h e faixas que cruzam a meia-noite (ex.: 19:00–07:00)."""
    if clinica["aberto_24h"]:
        return True
    agora, abre, fecha = _minutos(hora), _minutos(clinica["abre"]), _minutos(clinica["fecha"])
    if abre <= fecha:
        return abre <= agora < fecha
    return agora >= abre or agora < fecha  # cruza a meia-noite


def listar_clinicas(especialidade=None, hora=None):
    """Filtra clínicas por especialidade e por 'aberta no horário'. Ordena por distância."""
    with conectar() as con:
        clinicas = {r["id"]: dict(r) | {"especialidades": []} for r in con.execute("SELECT * FROM clinicas")}
        for r in con.execute("SELECT * FROM clinica_especialidades"):
            clinicas[r["clinica_id"]]["especialidades"].append(r["especialidade"])
    lista = list(clinicas.values())
    if especialidade:
        lista = [c for c in lista if especialidade in c["especialidades"]]
    if hora:
        for c in lista:
            c["aberta_agora"] = clinica_aberta(c, hora)
        lista = [c for c in lista if c["aberta_agora"]]
    lista.sort(key=lambda c: c["distancia_km"])
    return lista


# --------------------------------------------------------- tutor / compras
def obter_tutor(tutor_id):
    with conectar() as con:
        t = con.execute("SELECT * FROM tutores WHERE id=?", (tutor_id,)).fetchone()
        if not t:
            return None
        pet = con.execute("SELECT * FROM pets WHERE tutor_id=? ORDER BY id LIMIT 1", (tutor_id,)).fetchone()
        return dict(t) | {"pet": dict(pet) if pet else None}


def registrar_compra(tutor_id, oferta_id, quantidade=1):
    """Grava uma compra feita no marketplace. É o dado que depois alimenta a IA."""
    oferta = obter_oferta(oferta_id)
    if oferta is None:
        raise ValueError(f"oferta {oferta_id} não existe")
    with conectar() as con:
        cur = con.execute(
            "INSERT INTO compras (tutor_id, oferta_id, data, quantidade, valor) VALUES (?,?,?,?,?)",
            (tutor_id, oferta_id, date.today().isoformat(), quantidade, oferta["preco"] * quantidade))
        return cur.lastrowid


def historico_tutor(tutor_id, janela_dias=JANELA_DIAS):
    """
    Resume as compras do tutor nos últimos `janela_dias` em features de comportamento:
      compras_mes         = número de compras / meses da janela
      gasto_<grupo_ia>    = R$ por mês em cada grupo de produto
    Essas chaves têm exatamente os nomes das colunas do dataset de treino.
    """
    inicio = (date.today() - timedelta(days=janela_dias)).isoformat()
    meses = janela_dias / 30.0
    feats = {"compras_mes": 0.0} | {f"gasto_{g}": 0.0 for g in GRUPOS_IA}
    with conectar() as con:
        linhas = con.execute("""
            SELECT p.grupo_ia, COUNT(*) AS n, SUM(c.valor) AS total
              FROM compras c
              JOIN ofertas  o ON o.id = c.oferta_id
              JOIN produtos p ON p.id = o.produto_id
             WHERE c.tutor_id = ? AND c.data >= ?
             GROUP BY p.grupo_ia""", (tutor_id, inicio)).fetchall()
        recentes = con.execute("""
            SELECT c.data, c.valor, p.nome, p.grupo_ia
              FROM compras c JOIN ofertas o ON o.id = c.oferta_id JOIN produtos p ON p.id = o.produto_id
             WHERE c.tutor_id = ? ORDER BY c.data DESC, c.id DESC LIMIT 8""", (tutor_id,)).fetchall()
    total_compras = 0
    for r in linhas:
        total_compras += r["n"]
        feats[f"gasto_{r['grupo_ia']}"] = round(r["total"] / meses, 2)
    feats["compras_mes"] = round(total_compras / meses, 2)
    return {"features": feats, "total_compras_janela": total_compras, "janela_dias": janela_dias,
            "recentes": [dict(r) for r in recentes]}
