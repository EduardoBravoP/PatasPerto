"""
Carrega o modelo treinado (modelo.pkl) uma única vez e expõe `prever`.

Este módulo é a parte de IA em tempo de execução: recebe as features de um
cliente/pet e devolve a especialidade prevista com as probabilidades por classe.
Não acessa o banco — quem junta perfil + histórico de compras é a API (app.py).
"""
import json
import os

import joblib
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_MODELO = os.path.join(AQUI, "modelo.pkl")
CAMINHO_METRICAS = os.path.join(AQUI, "metricas.json")

_modelo = None
_metricas = None

NOMES_ESPECIALIDADE = {
    "emergencia": "Emergência / pronto atendimento",
    "dermatologia": "Dermatologia",
    "odontologia": "Odontologia",
    "ortopedia": "Ortopedia",
    "nutricao": "Nutrição",
    "clinico_geral": "Clínico geral (consulta de rotina)",
}


def carregar():
    global _modelo, _metricas
    if _modelo is None:
        if not os.path.exists(CAMINHO_MODELO):
            raise FileNotFoundError("modelo.pkl não encontrado — rode: python ml/gerar_dataset.py && python ml/treinar_modelo.py")
        _modelo = joblib.load(CAMINHO_MODELO)
        with open(CAMINHO_METRICAS, encoding="utf-8") as f:
            _metricas = json.load(f)
    return _modelo, _metricas


def metricas():
    return carregar()[1]


def prever(features: dict) -> dict:
    """
    features: dict com as colunas do treino (especie, idade_anos, porte, compras_mes,
              gasto_*, situacao). Colunas ausentes entram como 0 / valor padrão.
    Retorna a especialidade prevista, a confiança e a probabilidade de cada classe.
    """
    modelo, met = carregar()
    linha = {}
    for col in met["features"]:
        if col in met["categoricas"]:
            linha[col] = str(features.get(col, "checkup" if col == "situacao" else "cao" if col == "especie" else "medio"))
        else:
            linha[col] = float(features.get(col, 0.0) or 0.0)
    X = pd.DataFrame([linha])
    probas = modelo.predict_proba(X)[0]
    classes = list(modelo.classes_)
    ranking = sorted(zip(classes, probas), key=lambda cp: -cp[1])
    especialidade = ranking[0][0]
    return {
        "especialidade": especialidade,
        "especialidade_nome": NOMES_ESPECIALIDADE.get(especialidade, especialidade),
        "confianca": round(float(ranking[0][1]), 3),
        "probabilidades": [{"classe": c, "nome": NOMES_ESPECIALIDADE.get(c, c), "p": round(float(p), 3)} for c, p in ranking],
        "features_usadas": linha,
    }
