"""
Gera o dataset SINTÉTICO usado para treinar o modelo de recomendação.

Uso:   python ml/gerar_dataset.py
Saída: ml/dataset.csv  (2.500 linhas, semente fixa 42, 8% de ruído no rótulo)

Por que sintético? Não temos dados reais de compras/consultas. Optamos por
gerar dados fictícios porém COERENTES: as regras abaixo imitam o que um
veterinário esperaria (quem compra muito produto de pele tende a ter problema
dermatológico; cão grande e idoso tende a ter problema articular etc.).
Isso é declarado abertamente como escolha consciente do projeto.

Cada linha = um cliente/pet no momento em que pede uma recomendação.

Features (entrada do modelo):
  especie            cao | gato
  idade_anos         0.5 a 15
  porte              pequeno | medio | grande  (gato é sempre pequeno)
  compras_mes        frequência de compra na loja (compras/mês)
  gasto_<grupo>      R$/mês gastos em cada grupo de produto da loja:
                     alimentacao, petisco, higiene, brinquedo, pele, bucal, articular
  situacao           motivo relatado pelo tutor (checkup, coceira, mau_halito, ...)

Alvo (saída do modelo):
  especialidade      emergencia | dermatologia | odontologia | ortopedia | nutricao | clinico_geral

O HORÁRIO NÃO É FEATURE. Ele não muda qual especialidade o pet precisa; ele só
filtra quais clínicas estão abertas — e isso é consulta ao banco, não IA.
"""
import os
import random

import numpy as np
import pandas as pd

SEMENTE = 42
N_LINHAS = 2500
RUIDO = 0.08

ESPECIALIDADES = ["emergencia", "dermatologia", "odontologia", "ortopedia", "nutricao", "clinico_geral"]
SITUACOES_EMERGENCIA = ["engasgo", "sangramento", "toxico", "convulsao", "insolacao"]
SITUACOES = ["checkup", "coceira", "mau_halito", "mancando", "ganho_peso", "vomito"] + SITUACOES_EMERGENCIA
PESOS_SITUACAO = [0.30, 0.10, 0.08, 0.08, 0.08, 0.08] + [0.056] * 5
GRUPOS = ["alimentacao", "petisco", "higiene", "brinquedo", "pele", "bucal", "articular"]

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(AQUI, "dataset.csv")


def gasto(media, desvio, rng):
    """Gasto mensal em R$, nunca negativo, arredondado a centavos."""
    return round(max(0.0, rng.normal(media, desvio)), 2)


def gerar_linha(rng):
    especie = rng.choice(["cao", "gato"], p=[0.62, 0.38])
    idade = round(float(rng.uniform(0.5, 15.0)), 1)
    porte = "pequeno" if especie == "gato" else rng.choice(["pequeno", "medio", "grande"], p=[0.35, 0.40, 0.25])
    situacao = rng.choice(SITUACOES, p=PESOS_SITUACAO)
    compras_mes = round(float(np.clip(rng.normal(2.5, 1.2), 0, 6)), 1)

    # Gastos base (perfil "normal" de quem compra na loja)
    g = {
        "alimentacao": gasto(150 if especie == "cao" else 110, 40, rng),
        "petisco":     gasto(15, 10, rng),
        "higiene":     gasto(20, 12, rng),
        "brinquedo":   gasto(12, 10, rng),
        "pele":        gasto(10, 12, rng),
        "bucal":       gasto(6, 8, rng),
        "articular":   gasto(5, 10, rng),
    }
    # Coerência: a situação relatada e o perfil do pet puxam certos gastos para cima
    if situacao == "coceira":
        g["pele"] = gasto(55, 15, rng)
    if situacao == "mau_halito":
        g["bucal"] = gasto(40, 12, rng)
    if situacao == "mancando" or (idade > 8 and porte == "grande"):
        g["articular"] = gasto(70, 25, rng)
    if situacao == "ganho_peso":
        g["petisco"] = gasto(45, 12, rng)
        compras_mes = round(float(np.clip(compras_mes + 1.5, 0, 6)), 1)
    if idade > 10:
        g["articular"] = max(g["articular"], gasto(35, 20, rng))

    # Perfil de compra: parte dos clientes concentra gastos em um grupo de produtos
    # (compra muito antipulgas, ou muito produto dental, ou suplemento articular...)
    # mesmo sem relatar sintoma. É isso que permite ao modelo aprender que o
    # COMPORTAMENTO DE COMPRA na loja, sozinho, já indica uma especialidade.
    if rng.random() < 0.30:
        foco = rng.choice(["pele", "bucal", "articular", "petisco"])
        if foco == "pele":
            g["pele"] = gasto(65, 15, rng)
        elif foco == "bucal":
            g["bucal"] = gasto(50, 12, rng)
        elif foco == "articular":
            g["articular"] = gasto(85, 20, rng)
        else:
            g["petisco"] = gasto(60, 15, rng)
            compras_mes = round(float(np.clip(compras_mes + 1.5, 0, 6)), 1)

    return {"especie": especie, "idade_anos": idade, "porte": porte, "compras_mes": compras_mes,
            **{f"gasto_{k}": v for k, v in g.items()}, "situacao": situacao}


def rotular(l):
    """Regras 'do veterinário' que definem a especialidade — a ordem é a prioridade."""
    if l["situacao"] in SITUACOES_EMERGENCIA:
        return "emergencia"
    if l["situacao"] == "coceira" or l["gasto_pele"] > 45:
        return "dermatologia"
    if l["situacao"] == "mau_halito" or l["gasto_bucal"] > 35:
        return "odontologia"
    if l["situacao"] == "mancando" or l["gasto_articular"] > 60 or (l["idade_anos"] > 8 and l["porte"] == "grande"):
        return "ortopedia"
    razao_petisco = l["gasto_petisco"] / (l["gasto_alimentacao"] + 1)
    if l["situacao"] == "ganho_peso" or (razao_petisco > 0.4 and l["compras_mes"] > 3):
        return "nutricao"
    return "clinico_geral"


def gerar(n=N_LINHAS, semente=SEMENTE, ruido=RUIDO):
    random.seed(semente)
    rng = np.random.default_rng(semente)
    linhas = []
    for _ in range(n):
        l = gerar_linha(rng)
        l["especialidade"] = rotular(l)
        linhas.append(l)
    df = pd.DataFrame(linhas)

    # Ruído: em 8% das linhas o rótulo é trocado por outro qualquer.
    # Simula erros/variação do mundo real e impede acurácia artificial de 100%.
    idx = rng.choice(len(df), size=int(n * ruido), replace=False)
    for i in idx:
        outras = [e for e in ESPECIALIDADES if e != df.at[i, "especialidade"]]
        df.at[i, "especialidade"] = rng.choice(outras)
    return df


if __name__ == "__main__":
    df = gerar()
    df.to_csv(CAMINHO_CSV, index=False)
    print(f"Dataset salvo em {CAMINHO_CSV}: {len(df)} linhas x {len(df.columns)} colunas")
    print("\nDistribuição do alvo (especialidade):")
    print(df["especialidade"].value_counts().to_string())
    print("\nPrimeiras linhas:")
    print(df.head(5).to_string(index=False))
