# -*- coding: utf-8 -*-
"""
treinar_decisao.py
==================
Treina o Random Forest que toma a decisão do copiloto e salva o modelo.

Mostra na tela, para vocês usarem na apresentação:
  - acurácia no conjunto de teste (dados que o modelo NÃO viu no treino);
  - matriz de confusão (onde acerta / erra);
  - importância de cada variável (quais fatores mais pesam na decisão).
"""
import os
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg


def codificar(df):
    """Transforma as colunas categóricas em números (mesma regra do config)."""
    df = df.copy()
    df["classe_imagem"] = df["classe_imagem"].map(cfg.COD_CLASSE_IMAGEM)
    df["estado_emocional"] = df["estado_emocional"].map(cfg.COD_EMOCAO)
    return df


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dataset = os.path.join(raiz, cfg.CAMINHO_DATASET_DECISAO)
    if not os.path.exists(dataset):
        print("Dataset não encontrado. Rode antes: python treino/gerar_dataset_decisao.py")
        sys.exit(1)

    df = pd.read_csv(dataset)
    df = codificar(df)

    X = df[cfg.VARIAVEIS_RF]
    y = df["decisao"]

    # 80% treino / 20% teste, mantendo a proporção das classes
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modelo = RandomForestClassifier(
        n_estimators=200,   # 200 árvores
        max_depth=None,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",  # compensa a classe mais rara (ALIMENTAR-SE)
    )
    modelo.fit(X_tr, y_tr)

    y_pred = modelo.predict(X_te)

    print("=" * 60)
    print("RESULTADO DO TREINO — Random Forest da decisão")
    print("=" * 60)
    print(classification_report(y_te, y_pred, zero_division=0))

    print("Matriz de confusão (linhas = verdadeiro, colunas = previsto):")
    labels = sorted(y.unique())
    cm = confusion_matrix(y_te, y_pred, labels=labels)
    print("     " + " ".join(f"{l[:6]:>6s}" for l in labels))
    for l, linha in zip(labels, cm):
        print(f"{l[:6]:>6s} " + " ".join(f"{v:6d}" for v in linha))

    print("\nImportância das variáveis (o que mais pesa na decisão):")
    importancias = sorted(
        zip(cfg.VARIAVEIS_RF, modelo.feature_importances_),
        key=lambda x: x[1], reverse=True,
    )
    for nome, imp in importancias:
        barra = "#" * int(imp * 50)
        print(f"  {nome:32s} {imp:5.3f} {barra}")

    destino = os.path.join(raiz, cfg.CAMINHO_MODELO_DECISAO)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    joblib.dump(modelo, destino)
    print(f"\nModelo salvo em: {destino}")


if __name__ == "__main__":
    main()
