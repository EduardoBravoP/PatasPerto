Param(
    [switch]$SemApp
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$VenvPython = ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "▶ Criando ambiente virtual (.venv) com Python 3.12 via uv…"
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        uv venv --python 3.12 .venv
        uv pip install --python $VenvPython -r requirements.txt
    }
    else {
        if (Get-Command py -ErrorAction SilentlyContinue) {
            py -3.12 -m venv .venv
        }
        else {
            python -m venv .venv
        }
        & $VenvPython -m pip install -q -r requirements.txt
    }
}

Write-Host "▶ 1/3 Criando o banco SQLite (banco/patasperto.db)…"
& $VenvPython banco/criar_banco.py

Write-Host ""
Write-Host "▶ 2/3 Gerando o dataset sintético (ml/dataset.csv)…"
& $VenvPython ml/gerar_dataset.py

Write-Host ""
Write-Host "▶ 3/3 Treinando o Random Forest (ml/modelo.pkl)…"
& $VenvPython ml/treinar_modelo.py

if (-not $SemApp) {
    Write-Host ""
    Write-Host "▶ Subindo a API + app em http://127.0.0.1:5000"
    & $VenvPython app.py
}
