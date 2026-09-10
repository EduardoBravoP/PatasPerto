"""
Clínicas veterinárias REAIS a partir do OpenStreetMap (Overpass API) e
geocodificação de endereços (Nominatim). Resultados ficam em cache no SQLite.

Isto continua sendo CONSULTA A DADOS (não é IA): buscamos pontos com
amenity=veterinary num raio, calculamos a distância e organizamos os campos.

Limitações declaradas:
  - O OSM não informa especialidade. Inferimos pelo nome/horário (ex.: "odonto",
    "hospital", "24h") e marcamos `especialidade_inferida = True`. Confirme por telefone.
  - Muitas clínicas não têm `opening_hours` no OSM → `horario_conhecido = False`.
  - Cobertura depende do que voluntários mapearam na sua região.
"""
import json
import math
import os
import re
import sqlite3
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DB = os.path.join(AQUI, "patasperto.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "PatasPerto/1.0 (projeto academico; contato via GitHub)"
VALIDADE_CACHE = timedelta(hours=24)
DIAS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


# ------------------------------------------------------------------ cache
def _cache_get(chave):
    with sqlite3.connect(CAMINHO_DB) as con:
        r = con.execute("SELECT conteudo, criado_em FROM cache_externo WHERE chave=?", (chave,)).fetchone()
    if not r:
        return None
    if datetime.now() - datetime.fromisoformat(r[1]) > VALIDADE_CACHE:
        return None
    return json.loads(r[0])


def _cache_set(chave, valor):
    with sqlite3.connect(CAMINHO_DB) as con:
        con.execute("INSERT OR REPLACE INTO cache_externo VALUES (?,?,?)",
                    (chave, json.dumps(valor, ensure_ascii=False), datetime.now().isoformat(timespec="seconds")))


def _http_json(url, data=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


# --------------------------------------------------------------- utilidades
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def _normalizar(txt):
    txt = unicodedata.normalize("NFD", txt or "").lower()
    return "".join(c for c in txt if unicodedata.category(c) != "Mn")


def inferir_especialidades(nome, opening_hours, tags):
    """Heurística pelo nome/horário. Sempre inclui clinico_geral. Marcada como inferida."""
    n = _normalizar(nome) + " " + _normalizar(tags.get("description", ""))
    esp = set()
    if re.search(r"hospital|24 ?h|emergen|pronto[- ]?socorro|plant", n) or (opening_hours or "").strip() == "24/7":
        esp.add("emergencia")
    if re.search(r"odont|dent", n):
        esp.add("odontologia")
    if re.search(r"derma|pele|pelo", n):
        esp.add("dermatologia")
    if re.search(r"ortop|articul|fisio", n):
        esp.add("ortopedia")
    if re.search(r"nutri", n):
        esp.add("nutricao")
    esp.add("clinico_geral")
    return sorted(esp)


# ------------------------------------------------------- opening_hours (OSM)
def _minutos(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def _expandir_dias(spec):
    """'Mo-Fr' → {0..4}; 'Mo,We' → {0,2}; '' → todos."""
    if not spec:
        return set(range(7))
    dias = set()
    for parte in spec.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-")
            if a in DIAS and b in DIAS:
                ia, ib = DIAS.index(a), DIAS.index(b)
                dias |= set(range(ia, ib + 1)) if ia <= ib else set(range(ia, 7)) | set(range(0, ib + 1))
        elif parte in DIAS:
            dias.add(DIAS.index(parte))
    return dias


def aberta_em(opening_hours, quando):
    """
    Interpreta o subconjunto mais comum da sintaxe opening_hours do OSM.
    Retorna True/False, ou None quando não há horário ou o formato não é reconhecido.
    Ex.: '24/7', 'Mo-Fr 08:00-18:00; Sa 08:00-12:00', 'Mo-Sa 08:00-20:00; Su off'
    """
    if not opening_hours:
        return None
    oh = opening_hours.strip()
    if oh == "24/7":
        return True
    dia, agora = quando.weekday(), quando.hour * 60 + quando.minute
    reconheceu = False
    aberta = False
    for regra in oh.split(";"):
        regra = regra.strip()
        if not regra or regra.startswith("PH"):
            continue
        m = re.match(r"^((?:(?:Mo|Tu|We|Th|Fr|Sa|Su)(?:-(?:Mo|Tu|We|Th|Fr|Sa|Su))?,?\s*)*)\s*(.*)$", regra)
        if not m:
            return None
        dias, resto = _expandir_dias(m.group(1).replace(" ", "")), m.group(2).strip()
        if resto == "off" or resto == "closed":
            reconheceu = True
            if dia in dias:
                aberta = False
            continue
        faixas = re.findall(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", resto)
        if not faixas:
            return None
        reconheceu = True
        if dia in dias:
            for ini, fim in faixas:
                a, b = _minutos(ini), _minutos(fim)
                if (a <= agora < b) if a <= b else (agora >= a or agora < b):
                    aberta = True
    return aberta if reconheceu else None


# --------------------------------------------------------------- Overpass
def _consultar_overpass(lat, lon, raio_m):
    q = f"""[out:json][timeout:25];
(node["amenity"="veterinary"](around:{raio_m},{lat},{lon});
 way["amenity"="veterinary"](around:{raio_m},{lat},{lon});
 node["healthcare"="veterinary"](around:{raio_m},{lat},{lon}););
out center tags;"""
    return _http_json(OVERPASS_URL, data=urllib.parse.urlencode({"data": q}).encode())


def _normalizar_elemento(e, lat, lon):
    t = e.get("tags", {})
    clat, clon = (e.get("lat"), e.get("lon")) if "lat" in e else (e["center"]["lat"], e["center"]["lon"])
    nome = t.get("name") or "Clínica veterinária (sem nome no OSM)"
    rua = " ".join(x for x in [t.get("addr:street"), t.get("addr:housenumber")] if x)
    bairro = t.get("addr:suburb") or t.get("addr:city") or ""
    endereco = " · ".join(x for x in [rua, bairro] if x) or "Endereço não informado no OpenStreetMap"
    oh = t.get("opening_hours")
    return {
        "id": f"osm:{e['type']}/{e['id']}",
        "nome": nome, "endereco": endereco,
        "telefone": t.get("phone") or t.get("contact:phone") or t.get("mobile") or "",
        "site": t.get("website") or t.get("contact:website") or "",
        "horario_texto": oh or "", "horario_conhecido": bool(oh), "aberto_24h": (oh or "").strip() == "24/7",
        "abre": None, "fecha": None,
        "especialidades": inferir_especialidades(nome, oh, t), "especialidade_inferida": True,
        "lat": clat, "lon": clon, "distancia_km": round(haversine_km(lat, lon, clat, clon), 2),
        "fonte": "osm", "osm_url": f"https://www.openstreetmap.org/{e['type']}/{e['id']}",
    }


def buscar_clinicas(lat, lon, raio_km=5.0, consultar=None):
    """Clínicas reais num raio, ordenadas por distância. Usa cache de 24h."""
    chave = f"overpass:{round(lat, 3)},{round(lon, 3)},{raio_km}"
    bruto = _cache_get(chave)
    if bruto is None:
        bruto = (consultar or _consultar_overpass)(lat, lon, int(raio_km * 1000))
        _cache_set(chave, bruto)
    vistos, lista = set(), []
    for e in bruto.get("elements", []):
        c = _normalizar_elemento(e, lat, lon)
        chave_dup = (c["nome"].lower(), round(c["lat"], 4), round(c["lon"], 4))
        if chave_dup in vistos:
            continue
        vistos.add(chave_dup)
        lista.append(c)
    lista.sort(key=lambda c: c["distancia_km"])
    return lista


def anotar_abertas(clinicas, hora_hhmm):
    """Preenche aberta_agora (True/False/None) para o horário de hoje."""
    agora = datetime.now()
    h, m = hora_hhmm.split(":")
    quando = agora.replace(hour=int(h), minute=int(m))
    for c in clinicas:
        c["aberta_agora"] = aberta_em(c["horario_texto"], quando)
    return clinicas


# -------------------------------------------------------------- Nominatim
def geocodificar(consulta, consultar=None):
    """Endereço/cidade → (lat, lon, rótulo). Cache de 24h. None se não achar."""
    chave = "nominatim:" + _normalizar(consulta)
    r = _cache_get(chave)
    if r is None:
        if consultar is None:
            url = NOMINATIM_URL + "?" + urllib.parse.urlencode({"q": consulta, "format": "json", "limit": 1, "countrycodes": "br", "accept-language": "pt-BR"})
            r = _http_json(url)
        else:
            r = consultar(consulta)
        _cache_set(chave, r)
    if not r:
        return None
    x = r[0]
    return {"lat": float(x["lat"]), "lon": float(x["lon"]), "rotulo": x.get("display_name", consulta)}
