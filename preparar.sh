#!/usr/bin/env bash
# Prepara e executa o PatasPerto do zero: ambiente → banco → dataset → modelo → app.
# Uso: bash preparar.sh          (ou: bash preparar.sh --sem-app para só preparar)
set -e
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "▶ Criando ambiente virtual (.venv) com Python 3.12 via uv…"
  if command -v uv >/dev/null 2>&1; then
    uv venv --python 3.12 .venv
    uv pip install --python .venv/bin/python -r requirements.txt
  else
    python3 -m venv .venv
    .venv/bin/python -m pip install -q -r requirements.txt
  fi
fi
PY=.venv/bin/python

echo "▶ 1/3 Criando o banco SQLite (banco/patasperto.db)…";   $PY banco/criar_banco.py
echo; echo "▶ 2/3 Gerando o dataset sintético (ml/dataset.csv)…"; $PY ml/gerar_dataset.py
echo; echo "▶ 3/3 Treinando o Random Forest (ml/modelo.pkl)…";  $PY ml/treinar_modelo.py

if [ "$1" != "--sem-app" ]; then
  echo; echo "▶ Subindo a API + app em http://127.0.0.1:5000"
  $PY app.py
fi
