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


@app.get("/api/clinicas")
def api_clinicas():
    especialidade = request.args.get("especialidade") or None
    hora = request.args.get("hora") or None
    return jsonify(consultas.listar_clinicas(especialidade, hora))


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
    clinicas = consultas.listar_clinicas(ia["especialidade"], hora)
    return jsonify({
        "ia": ia | {"origem": "Random Forest treinado em ml/treinar_modelo.py",
                    "historico_compras": {"total_compras_janela": historico["total_compras_janela"],
                                          "janela_dias": historico["janela_dias"]}},
        "banco": {"hora_consultada": hora, "especialidade_filtrada": ia["especialidade"],
                  "clinicas": clinicas, "origem": "consulta SQL em banco/consultas.py"},
    })


if __name__ == "__main__":
    print("PatasPerto rodando em http://127.0.0.1:5000  (Ctrl+C para parar)")
    app.run(host="127.0.0.1", port=5000, debug=True)
