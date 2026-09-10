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


# ---------------- clínicas reais (OpenStreetMap) — sem rede: Overpass simulado
OVERPASS_FAKE = {"elements": [
    {"type": "node", "id": 1, "lat": -22.9100, "lon": -47.0600,
     "tags": {"amenity": "veterinary", "name": "Hospital Veterinário Central 24h", "opening_hours": "24/7",
              "phone": "+55 19 3333-0000", "addr:street": "Rua A", "addr:housenumber": "10", "addr:suburb": "Centro"}},
    {"type": "way", "id": 2, "center": {"lat": -22.9200, "lon": -47.0700},
     "tags": {"amenity": "veterinary", "name": "OdontoVet Sorriso", "opening_hours": "Mo-Fr 08:00-18:00"}},
    {"type": "node", "id": 3, "lat": -22.9000, "lon": -47.0500, "tags": {"amenity": "veterinary", "name": "Clínica do Bairro"}},
]}


@pytest.fixture
def overpass_falso(monkeypatch):
    import clinicas_osm
    monkeypatch.setattr(clinicas_osm, "_consultar_overpass", lambda lat, lon, r: OVERPASS_FAKE)
    monkeypatch.setattr(clinicas_osm, "_cache_get", lambda chave: None)
    monkeypatch.setattr(clinicas_osm, "_cache_set", lambda chave, v: None)


def test_clinicas_reais_por_posicao(cliente, overpass_falso):
    r = cliente.get("/api/clinicas?meta=1&lat=-22.9056&lon=-47.0608&raio_km=5&hora=23:00").get_json()
    assert r["meta"]["fonte"] == "osm" and r["meta"]["total_no_raio"] == 3
    por_nome = {c["nome"]: c for c in r["clinicas"]}
    hosp = por_nome["Hospital Veterinário Central 24h"]
    assert hosp["fonte"] == "osm" and hosp["aberto_24h"] and hosp["aberta_agora"] is True
    assert "emergencia" in hosp["especialidades"] and hosp["especialidade_inferida"]
    assert "odontologia" in por_nome["OdontoVet Sorriso"]["especialidades"]
    assert por_nome["OdontoVet Sorriso"]["aberta_agora"] is False          # 23:00 fora de Mo-Fr 08-18
    assert por_nome["Clínica do Bairro"]["aberta_agora"] is None            # sem horário no OSM
    assert 0 < hosp["distancia_km"] < 1.0
    assert [c["distancia_km"] for c in r["clinicas"]] == sorted(c["distancia_km"] for c in r["clinicas"])


def test_recomendar_com_posicao_usa_osm_e_relaxa_filtro(cliente, overpass_falso):
    corpo = {"especie": "gato", "idade_anos": 3, "porte": "pequeno", "situacao": "coceira", "hora": "10:00",
             "lat": -22.9056, "lon": -47.0608, "raio_km": 5}
    r = cliente.post("/api/recomendar", json=corpo).get_json()
    assert r["ia"]["especialidade"] == "dermatologia"
    assert r["banco"]["fonte"] == "osm"
    assert r["banco"]["aviso"] and "dermatologia" in r["banco"]["aviso"]   # ninguém tem "derma" no nome → mostra todas
    assert len(r["banco"]["clinicas"]) == 3


def test_geocodificar_valida_entrada(cliente):
    assert cliente.get("/api/geocodificar?q=ab").status_code == 400


def test_opening_hours_parser():
    from datetime import datetime
    import clinicas_osm as o
    qua10 = datetime(2026, 9, 9, 10, 0)
    assert o.aberta_em("24/7", qua10) is True
    assert o.aberta_em("Mo-Fr 08:00-17:00; Sa 08:00-12:00", qua10) is True
    assert o.aberta_em("Mo-Fr 08:00-17:00; Sa 08:00-12:00", datetime(2026, 9, 13, 10, 0)) is False   # domingo
    assert o.aberta_em("Mo-Fr 19:00-07:00", datetime(2026, 9, 9, 23, 30)) is True                     # cruza meia-noite
    assert o.aberta_em(None, qua10) is None and o.aberta_em("by appointment", qua10) is None
