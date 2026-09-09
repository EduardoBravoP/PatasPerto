"""
Treina o modelo de recomendação (Random Forest) e salva modelo.pkl + metricas.json.

Uso:   python ml/treinar_modelo.py
Lê:    ml/dataset.csv          (gerado por gerar_dataset.py)
Salva: ml/modelo.pkl           (Pipeline completo: pré-processamento + Random Forest)
       ml/metricas.json        (acurácia, relatório por classe, matriz de confusão, importâncias)

Por que Random Forest?
  - lida bem com variáveis categóricas (após one-hot) e numéricas juntas;
  - robusto a ruído e a escalas diferentes (R$ x anos x compras/mês), sem normalização;
  - fornece importância das variáveis, que ajuda a explicar as decisões para a banca;
  - fornece probabilidades por classe (predict_proba), usadas como "confiança" no app.
"""
import json
import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

AQUI = os.path.dirname(os.path.abspath(__file__))
CAMINHO_CSV = os.path.join(AQUI, "dataset.csv")
CAMINHO_MODELO = os.path.join(AQUI, "modelo.pkl")
CAMINHO_METRICAS = os.path.join(AQUI, "metricas.json")

ALVO = "especialidade"
CATEGORICAS = ["especie", "porte", "situacao"]
NUMERICAS = ["idade_anos", "compras_mes", "gasto_alimentacao", "gasto_petisco", "gasto_higiene",
             "gasto_brinquedo", "gasto_pele", "gasto_bucal", "gasto_articular"]
FEATURES = CATEGORICAS + NUMERICAS


def montar_pipeline():
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ("num", "passthrough", NUMERICAS),
    ])
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    return Pipeline([("pre", pre), ("rf", rf)])


def importancias_por_coluna(pipeline):
    """Soma as importâncias das colunas one-hot de volta para a coluna original."""
    nomes = pipeline.named_steps["pre"].get_feature_names_out()   # ex.: cat__situacao_coceira, num__idade_anos
    imps = pipeline.named_steps["rf"].feature_importances_
    total = {}
    for nome, imp in zip(nomes, imps):
        nome = nome.split("__", 1)[1]
        original = next((c for c in CATEGORICAS if nome.startswith(c + "_")), nome)
        total[original] = total.get(original, 0.0) + float(imp)
    return dict(sorted(total.items(), key=lambda kv: -kv[1]))


def treinar():
    df = pd.read_csv(CAMINHO_CSV)
    X, y = df[FEATURES], df[ALVO]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    modelo = montar_pipeline()
    modelo.fit(X_tr, y_tr)
    pred = modelo.predict(X_te)

    classes = sorted(y.unique())
    acuracia = accuracy_score(y_te, pred)
    relatorio = classification_report(y_te, pred, output_dict=True, zero_division=0)
    matriz = confusion_matrix(y_te, pred, labels=classes)
    cv = cross_val_score(montar_pipeline(), X, y, cv=5)
    importancias = importancias_por_coluna(modelo)

    # ---- saída no terminal (o que a banca vê na demonstração do treino)
    print(f"Linhas: {len(df)}  |  treino: {len(X_tr)}  |  teste: {len(X_te)}")
    print(f"\nAcurácia no teste: {acuracia:.4f}   (validação cruzada 5 folds: {cv.mean():.4f} ± {cv.std():.4f})")
    print("\nRelatório por classe:")
    print(classification_report(y_te, pred, zero_division=0))
    print("Matriz de confusão (linhas = real, colunas = previsto):")
    print(pd.DataFrame(matriz, index=classes, columns=classes).to_string())
    print("\nImportância das variáveis (agregada por coluna original):")
    for k, v in importancias.items():
        print(f"  {k:18s} {v:.3f}  {'█' * int(v * 60)}")
    print("\nObs.: o ruído de 8% no rótulo limita a acurácia máxima teórica a ~92%.")

    joblib.dump(modelo, CAMINHO_MODELO)
    with open(CAMINHO_METRICAS, "w", encoding="utf-8") as f:
        json.dump({
            "algoritmo": "RandomForestClassifier (200 árvores) + OneHotEncoder",
            "n_linhas": int(len(df)), "n_treino": int(len(X_tr)), "n_teste": int(len(X_te)),
            "acuracia": round(float(acuracia), 4),
            "cv_media": round(float(cv.mean()), 4), "cv_desvio": round(float(cv.std()), 4),
            "classes": classes, "relatorio": relatorio, "matriz_confusao": matriz.tolist(),
            "importancias": {k: round(v, 4) for k, v in importancias.items()},
            "features": FEATURES, "categoricas": CATEGORICAS, "numericas": NUMERICAS,
        }, f, ensure_ascii=False, indent=2)
    print(f"\nModelo salvo em {CAMINHO_MODELO}\nMétricas salvas em {CAMINHO_METRICAS}")


if __name__ == "__main__":
    treinar()
