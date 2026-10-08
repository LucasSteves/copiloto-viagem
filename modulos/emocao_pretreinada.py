# -*- coding: utf-8 -*-
"""
modulos/emocao_pretreinada.py
=============================
Análise de emoção da voz usando um MODELO PRÉ-TREINADO (o mesmo do professor:
Aniemore/wav2vec2-emotion-v1-crosslingual, do Hugging Face).

Vantagem: NÃO precisa treinar nem coletar áudio — o modelo já vem pronto.
Ele reconhece 7 emoções; aqui traduzimos para as 4 que o nosso Random Forest
usa (normal, alegre, triste, irritado).

Requer (instalação pesada, ver requirements-emocao.txt):
    pip install torch transformers
Na primeira execução o modelo (~360 MB) é baixado da internet e fica salvo em
cache para as próximas vezes.
"""
from functools import lru_cache

import config as cfg

MODEL_ID = "Aniemore/wav2vec2-emotion-v1-crosslingual"
TAXA_ALVO = 16000  # o modelo espera áudio a 16 kHz

# tradução das 7 emoções do modelo -> as 4 emoções do nosso Random Forest
MAPA_EMOCOES = {
    "anger": "irritado", "angry": "irritado",
    "disgust": "irritado",
    "fear": "irritado",
    "enthusiasm": "alegre",
    "happiness": "alegre", "happy": "alegre",
    "neutral": "normal",
    "sadness": "triste", "sad": "triste",
}


@lru_cache(maxsize=1)
def _carregar():
    """Carrega o modelo uma única vez (baixa na 1ª execução)."""
    import torch
    from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
    extractor = AutoFeatureExtractor.from_pretrained(MODEL_ID)
    modelo = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
    modelo.eval()
    return extractor, modelo, torch


def disponivel():
    """True se torch+transformers estão instalados (não baixa o modelo)."""
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        return True
    except Exception:
        return False


def _traduzir_probabilidades(probs_por_rotulo):
    """Recebe {rotulo_do_modelo: prob} e soma nas 4 emoções nossas."""
    agregado = {e: 0.0 for e in cfg.EMOCOES}
    for rotulo, p in probs_por_rotulo.items():
        nossa = MAPA_EMOCOES.get(rotulo.lower().strip())
        if nossa:
            agregado[nossa] += float(p)
    total = sum(agregado.values())
    if total > 0:
        agregado = {k: v / total for k, v in agregado.items()}
    return agregado


def analisar(caminho_wav):
    """Retorna (emocao_nossa, confianca_%). Precisa de um .wav do comando."""
    import librosa
    import numpy as np

    extractor, modelo, torch = _carregar()

    # carrega o áudio a 16 kHz, mono
    wav, _ = librosa.load(caminho_wav, sr=TAXA_ALVO, mono=True)

    inputs = extractor(wav, sampling_rate=TAXA_ALVO, return_tensors="pt", padding=True)
    with torch.inference_mode():
        logits = modelo(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0].detach().cpu().numpy()

    # monta {rotulo: prob} usando o dicionário do próprio modelo
    probs_por_rotulo = {}
    for i, p in enumerate(probs):
        rotulo = str(modelo.config.id2label.get(i, f"LABEL_{i}"))
        probs_por_rotulo[rotulo] = probs_por_rotulo.get(rotulo, 0.0) + float(p)

    agregado = _traduzir_probabilidades(probs_por_rotulo)
    emocao = max(agregado, key=agregado.get)
    confianca = round(100 * agregado[emocao], 1)
    return emocao, confianca
