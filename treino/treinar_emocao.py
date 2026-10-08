# -*- coding: utf-8 -*-
"""
treinar_emocao.py
=================
Treina o classificador de EMOÇÃO da voz. Extrai características acústicas de
cada áudio (MFCC, energia, taxa de cruzamentos por zero) e treina um
Random Forest sobre elas.

REUSO: podem usar as gravações do TRABALHO ANTERIOR do grupo (normal, alegre,
triste, irritado). Continua sendo "dataset próprio". Basta organizar assim:
    dados/audios/normal/*      dados/audios/triste/*
    dados/audios/alegre/*      dados/audios/irritado/*

Aceita vários formatos: .wav, .mp3, .m4a, .ogg, .flac.
  - .wav funciona direto.
  - .mp3/.m4a/.ogg exigem o FFmpeg instalado no sistema:
        Windows: baixar em ffmpeg.org e adicionar ao PATH (ou `winget install ffmpeg`)
        Linux:   sudo apt install ffmpeg
        Mac:     brew install ffmpeg

Rodar:
    pip install librosa scikit-learn joblib
    python treino/treinar_emocao.py

Obs.: a função de extração é a MESMA usada em modulos/voz.py, para o treino e
a previsão enxergarem o áudio do mesmo jeito.
"""
import glob
import os
import sys

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg


def extrair_features(caminho_wav):
    import librosa
    y, sr_ = librosa.load(caminho_wav, sr=22050, duration=3.0)
    mfcc = librosa.feature.mfcc(y=y, sr=sr_, n_mfcc=20)
    rms = librosa.feature.rms(y=y)
    zcr = librosa.feature.zero_crossing_rate(y)
    return np.concatenate([
        mfcc.mean(axis=1), mfcc.std(axis=1),
        [rms.mean(), rms.std(), zcr.mean()],
    ])


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_audios = os.path.join(raiz, "dados", "audios")

    X, y = [], []
    formatos = ("*.wav", "*.mp3", "*.m4a", "*.ogg", "*.flac")
    for emocao in cfg.EMOCOES:
        arquivos = []
        for fmt in formatos:
            arquivos += glob.glob(os.path.join(dir_audios, emocao, fmt))
        print(f"  {emocao:10s}: {len(arquivos)} áudios")
        for arq in arquivos:
            try:
                X.append(extrair_features(arq))
                y.append(emocao)
            except Exception as e:
                print(f"    (ignorado {arq}: {e})")

    if len(X) < 20:
        print("\nPoucos áudios. Grave mais clipes antes de treinar "
              "(recomendado 15-20 por emoção).")
        sys.exit(1)

    X = np.array(X)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    modelo = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    modelo.fit(X_tr, y_tr)

    print("\nDesempenho no teste:")
    print(classification_report(y_te, modelo.predict(X_te), zero_division=0))

    destino = os.path.join(raiz, cfg.CAMINHO_MODELO_EMOCAO)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    joblib.dump(modelo, destino)
    print(f"Modelo de emoção salvo em: {destino}")


if __name__ == "__main__":
    main()
