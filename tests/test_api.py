"""Smoke tests da API. Rode: pytest tests/  (requer banco criado e modelo treinado)."""
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from app import app  # noqa: E402


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    return app.test_client()


def test_ofertas(cliente):
    r = cliente.get("/api/ofertas")
    assert r.status_code == 200
    ofertas = r.get_json()
    assert len(ofertas) >= 27
    assert {"produto", "loja", "preco"} <= set(ofertas[0])


def test_clinicas_filtro_horario(cliente):
    nomes = [c["nome"] for c in cliente.get("/api/clinicas?especialidade=odontologia&hora=23:00").get_json()]
    assert nomes == ["Hosp. Vet. Bicho Feliz"]          # única 24h com odontologia
    noturno = [c["nome"] for c in cliente.get("/api/clinicas?especialidade=emergencia&hora=03:00").get_json()]
    assert "Plantão Vet Noturno" in noturno              # faixa 19:00–07:00 cruza a meia-noite


def test_recomendar_emergencia(cliente):
    r = cliente.post("/api/recomendar", json={"tutor_id": 1, "especie": "cao", "idade_anos": 4,
                                              "porte": "medio", "situacao": "convulsao", "hora": "22:00"})
    assert r.status_code == 200
    corpo = r.get_json()
    assert corpo["ia"]["especialidade"] == "emergencia"
    assert corpo["ia"]["confianca"] > 0.5
    assert all("emergencia" in c["especialidades"] for c in corpo["banco"]["clinicas"])


def test_recomendar_valida_entrada(cliente):
    assert cliente.post("/api/recomendar", json={"especie": "peixe"}).status_code == 400


def test_compra_incrementa_historico(cliente):
    antes = cliente.get("/api/tutores/1/historico").get_json()["total_compras_janela"]
    r = cliente.post("/api/compras", json={"tutor_id": 1, "oferta_id": 25})
    assert r.status_code == 201
    assert r.get_json()["historico"]["total_compras_janela"] == antes + 1
    assert cliente.post("/api/compras", json={"oferta_id": 9999}).status_code == 400


def test_metricas(cliente):
    m = cliente.get("/api/modelo/metricas").get_json()
    assert m["acuracia"] > 0.85
    assert "situacao" in m["importancias"]


def test_coordenadas_para_o_mapa(cliente):
    tutor = cliente.get("/api/tutores/1").get_json()
    assert tutor["lat"] and tutor["lon"]
    clinicas = cliente.get("/api/clinicas").get_json()
    assert all(c["lat"] and c["lon"] for c in clinicas)
    # posição no mapa coerente com a distância exibida (erro < 50 m)
    import math
    for c in clinicas:
        d = math.hypot((c["lat"] - tutor["lat"]) * 111.32, (c["lon"] - tutor["lon"]) * 111.32 * math.cos(math.radians(tutor["lat"])))
        assert abs(d - c["distancia_km"]) < 0.05
