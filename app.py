"""
PatasPerto — back-end (API Flask).

Uso:  python app.py   →  http://127.0.0.1:5000

Camadas:
  static/            front-end (HTML/CSS/JS) servido por esta mesma app (mesma origem, sem CORS)
  banco/consultas.py acesso ao SQLite      → rotas marcadas [banco]
  ml/recomendador.py modelo Random Forest  → rotas marcadas [IA]
"""
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "banco"))
sys.path.insert(0, os.path.join(AQUI, "ml"))

import clinicas_osm  # noqa: E402
import consultas  # noqa: E402
import recomendador  # noqa: E402

app = Flask(__name__, static_folder=os.path.join(AQUI, "static"), static_url_path="/static")

ESPECIES = {"cao", "gato"}
PORTES = {"pequeno", "medio", "grande"}


# ------------------------------------------------------------ front-end
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


# ------------------------------------------------------------ [banco] loja
@app.get("/api/ofertas")
def api_ofertas():
    return jsonify(consultas.listar_ofertas())


def _posicao(fonte):
    """lat/lon/raio_km vindos da query string ou do corpo JSON; None se ausentes."""
    try:
        lat, lon = float(fonte.get("lat")), float(fonte.get("lon"))
    except (TypeError, ValueError):
        return None
    try:
        raio = min(max(float(fonte.get("raio_km") or 5), 0.5), 30)
    except (TypeError, ValueError):
        raio = 5.0
    return {"lat": lat, "lon": lon, "raio_km": raio}


def clinicas_para(pos, especialidade=None, hora=None, so_abertas=False, tolerante=False):
    """
    Duas fontes, mesmo formato:
      - pos informado  → clínicas REAIS do OpenStreetMap ao redor de lat/lon (banco/clinicas_osm.py)
      - sem pos        → clínicas fictícias de demonstração (tabela clinicas)
    Retorna (lista, meta). `tolerante=True` relaxa o filtro de especialidade quando ele zera a lista.
    """
    meta = {"fonte": "demo", "aviso": None}
    if pos:
        try:
            lista = clinicas_osm.buscar_clinicas(pos["lat"], pos["lon"], pos["raio_km"])
            meta.update(fonte="osm", raio_km=pos["raio_km"], total_no_raio=len(lista))
        except Exception as e:  # sem internet / Overpass fora → cai para demonstração
            lista = consultas.listar_clinicas()
            meta["aviso"] = f"Não foi possível consultar o OpenStreetMap ({type(e).__name__}); mostrando dados de demonstração."
        if hora:
            clinicas_osm.anotar_abertas(lista, hora)
    else:
        lista = consultas.listar_clinicas()
        for c in lista:
            c.update(fonte="demo", horario_conhecido=True, especialidade_inferida=False, site="", osm_url="",
                     horario_texto="24h" if c["aberto_24h"] else f'{c["abre"]}–{c["fecha"]}')
            if hora:
                c["aberta_agora"] = consultas.clinica_aberta(c, hora)
    if meta["fonte"] == "osm" and not lista:
        meta["aviso"] = "Nenhuma clínica veterinária mapeada no OpenStreetMap nesse raio. Aumente o raio."
    if especialidade:
        filtrada = [c for c in lista if especialidade in c["especialidades"]]
        if not filtrada and tolerante and lista:
            meta["aviso"] = (meta["aviso"] or "") + f" Nenhuma clínica próxima indica '{especialidade}' no nome; mostrando todas as clínicas próximas — confirme a especialidade por telefone."
            meta["aviso"] = meta["aviso"].strip()
        else:
            lista = filtrada
    if hora and so_abertas:
        # aberta_agora None = horário desconhecido: mantemos na lista, sinalizado no app
        lista = [c for c in lista if c.get("aberta_agora") is not False]
    lista.sort(key=lambda c: c["distancia_km"])
    return lista, meta


@app.get("/api/clinicas")
def api_clinicas():
    """
    Sem lat/lon: clínicas de demonstração (compatível com a versão anterior: `hora` filtra).
    Com lat/lon (+ raio_km): clínicas reais do OpenStreetMap. `hora` anota aberta_agora;
    `so_abertas=1` filtra. `meta=1` devolve {"clinicas": [...], "meta": {...}}.
    """
    especialidade = request.args.get("especialidade") or None
    hora = request.args.get("hora") or None
    pos = _posicao(request.args)
    so_abertas = request.args.get("so_abertas") == "1" or (pos is None and hora is not None)
    lista, meta = clinicas_para(pos, especialidade, hora, so_abertas)
    if request.args.get("meta") == "1":
        return jsonify({"clinicas": lista, "meta": meta})
    return jsonify(lista)


@app.get("/api/geocodificar")
def api_geocodificar():
    q = (request.args.get("q") or "").strip()
    if len(q) < 3:
        return jsonify({"erro": "informe um endereço ou cidade"}), 400
    try:
        r = clinicas_osm.geocodificar(q)
    except Exception as e:
        return jsonify({"erro": f"serviço de geocodificação indisponível ({type(e).__name__})"}), 502
    if not r:
        return jsonify({"erro": "endereço não encontrado"}), 404
    return jsonify(r)


@app.get("/api/tutores/<int:tutor_id>")
def api_tutor(tutor_id):
    t = consultas.obter_tutor(tutor_id)
    if t is None:
        return jsonify({"erro": "tutor não encontrado"}), 404
    return jsonify(t)


@app.get("/api/tutores/<int:tutor_id>/historico")
def api_historico(tutor_id):
    return jsonify(consultas.historico_tutor(tutor_id))


@app.post("/api/compras")
def api_compras():
    """Registra uma compra do marketplace. É este dado que depois alimenta a IA."""
    corpo = request.get_json(silent=True) or {}
    tutor_id = int(corpo.get("tutor_id", 1))
    try:
        oferta_id = int(corpo["oferta_id"])
        compra_id = consultas.registrar_compra(tutor_id, oferta_id, int(corpo.get("quantidade", 1)))
    except (KeyError, ValueError, TypeError) as e:
        return jsonify({"erro": str(e)}), 400
    return jsonify({"compra_id": compra_id, "historico": consultas.historico_tutor(tutor_id)}), 201


# ------------------------------------------------------------ [IA] modelo
@app.get("/api/modelo/metricas")
def api_metricas():
    return jsonify(recomendador.metricas())


@app.post("/api/recomendar")
def api_recomendar():
    """
    Junta duas coisas distintas — e a resposta deixa isso explícito:
      "ia":    o Random Forest prevê a especialidade a partir do perfil do pet,
               da situação relatada e do comportamento de compra (vindo do banco);
      "banco": consulta simples: clínicas com aquela especialidade abertas no horário.
    """
    corpo = request.get_json(silent=True) or {}
    tutor_id = int(corpo.get("tutor_id", 1))
    especie = str(corpo.get("especie", "cao")).lower()
    porte = str(corpo.get("porte", "medio")).lower()
    if especie not in ESPECIES or porte not in PORTES:
        return jsonify({"erro": "especie deve ser cao|gato e porte pequeno|medio|grande"}), 400
    try:
        idade = float(corpo.get("idade_anos", 5))
    except (TypeError, ValueError):
        return jsonify({"erro": "idade_anos inválida"}), 400
    situacao = str(corpo.get("situacao", "checkup"))
    hora = corpo.get("hora") or datetime.now().strftime("%H:%M")

    historico = consultas.historico_tutor(tutor_id)
    features = {"especie": especie, "idade_anos": idade, "porte": porte, "situacao": situacao,
                **historico["features"]}
    ia = recomendador.prever(features)
    pos = _posicao(corpo)
    clinicas, meta = clinicas_para(pos, ia["especialidade"], hora, so_abertas=True, tolerante=True)
    return jsonify({
        "ia": ia | {"origem": "Random Forest treinado em ml/treinar_modelo.py",
                    "historico_compras": {"total_compras_janela": historico["total_compras_janela"],
                                          "janela_dias": historico["janela_dias"]}},
        "banco": {"hora_consultada": hora, "especialidade_filtrada": ia["especialidade"],
                  "clinicas": clinicas[:12], **meta,
                  "origem": "clínicas reais do OpenStreetMap (banco/clinicas_osm.py), especialidade inferida pelo nome"
                            if meta["fonte"] == "osm" else "consulta SQL em banco/consultas.py (dados de demonstração)"},
    })


if __name__ == "__main__":
    print("PatasPerto rodando em http://127.0.0.1:5000  (Ctrl+C para parar)")
    app.run(host="127.0.0.1", port=5000, debug=True)
