# -*- coding: utf-8 -*-
"""
modulos/decisao.py
==================
O CÉREBRO. Recebe o contexto coletado (localização, imagem, emoção...) e usa
o Random Forest treinado para recomendar UMA ação. Também devolve uma
justificativa em português — é o que responde a pergunta da banca:
"por que o modelo recomendou isso?".
"""
import os

import joblib
import numpy as np
import pandas as pd

import config as cfg

_modelo = None


def carregar_modelo():
    global _modelo
    if _modelo is None:
        if not os.path.exists(cfg.CAMINHO_MODELO_DECISAO):
            raise FileNotFoundError(
                "Modelo de decisão não treinado. Rode: python treino/treinar_decisao.py"
            )
        _modelo = joblib.load(cfg.CAMINHO_MODELO_DECISAO)
    return _modelo


def _justificar(contexto, decisao):
    """Frase explicando a decisão, com base nos mesmos fatores que o modelo
    aprendeu. Serve de apoio para a apresentação ao vivo."""
    t = contexto["tempo_desde_ultima_parada_min"]
    emo = contexto["estado_emocional"]
    img = contexto["classe_imagem"]
    dist = contexto["distancia_total_km"]

    if decisao == "FAZER_UMA_PARADA":
        motivos = []
        if emo in ("irritado", "triste"):
            motivos.append(f"a voz indica {emo}")
        if t >= 120:
            motivos.append(f"já são {t} min sem parar")
        motivo = " e ".join(motivos) if motivos else "o tempo acumulado na estrada"
        return f"O motorista deve descansar: {motivo}."
    if decisao == "ABASTECER":
        return (f"Há um posto na cena e a viagem já soma {dist} km / "
                f"{t} min desde a última parada — bom momento para abastecer.")
    if decisao == "ALIMENTAR-SE":
        return f"Restaurante detectado em horário de refeição ({contexto['hora_do_dia']}h)."
    if decisao == "REGISTRAR_PONTO_TURISTICO":
        return f"Ponto turístico detectado e o motorista está {emo} — vale registrar."
    return "Nenhum fator crítico: seguir viagem com segurança."


def decidir(contexto):
    """contexto: dict com as chaves de cfg.VARIAVEIS_RF.
    Retorna: (decisao, confianca_%, justificativa, probabilidades_por_classe)."""
    modelo = carregar_modelo()

    # monta o vetor de entrada na MESMA ordem do treino, codificando categóricas
    entrada = {
        "hora_do_dia": contexto["hora_do_dia"],
        "tempo_desde_ultima_parada_min": contexto["tempo_desde_ultima_parada_min"],
        "distancia_total_km": contexto["distancia_total_km"],
        "classe_imagem": cfg.COD_CLASSE_IMAGEM[contexto["classe_imagem"]],
        "estado_emocional": cfg.COD_EMOCAO[contexto["estado_emocional"]],
        "paradas_feitas": contexto["paradas_feitas"],
    }
    X = pd.DataFrame([entrada], columns=cfg.VARIAVEIS_RF)

    decisao = modelo.predict(X)[0]
    probs = modelo.predict_proba(X)[0]
    classes = modelo.classes_
    confianca = round(100 * float(np.max(probs)), 1)

    probabilidades = {c: round(100 * float(p), 1) for c, p in zip(classes, probs)}
    justificativa = _justificar(contexto, decisao)
    return decisao, confianca, justificativa, probabilidades
