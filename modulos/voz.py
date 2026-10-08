# -*- coding: utf-8 -*-
"""
modulos/voz.py
==============
Dois papéis a partir do MESMO áudio:
  1. Reconhecimento do comando falado (fala -> texto -> comando).
  2. Análise emocional da voz (cansado / neutro / animado / tenso + confiança).

Funciona em dois modos:
  - REAL (padrão): usa o microfone. Precisa de `speechrecognition` e `pyaudio`
    para a fala, e `librosa` + modelo treinado para a emoção.
  - SIMULADO: se o hardware/bibliotecas não estiverem disponíveis (ou com a
    flag --simular), lê comandos do teclado e sorteia a emoção. Assim o fluxo
    inteiro roda em qualquer máquina, inclusive para testes.
"""
import os
import random
import unicodedata

import config as cfg

# ---- imports opcionais (só carregam se existirem) -------------------------
try:
    import speech_recognition as sr
    _TEM_SR = True
except Exception:
    _TEM_SR = False

try:
    import joblib
    import numpy as np
    _emo_modelo = None
    try:
        import librosa  # noqa: F401
        _TEM_LIBROSA = True
    except Exception:
        _TEM_LIBROSA = False
except Exception:
    _TEM_LIBROSA = False


def _normalizar(texto):
    """minúsculo, sem acento — para comparar comandos de forma robusta."""
    texto = texto.lower().strip()
    texto = "".join(c for c in unicodedata.normalize("NFD", texto)
                     if unicodedata.category(c) != "Mn")
    return texto


def _palavras_significativas(texto):
    """Palavras do texto ignorando conectivos curtos (a, o, de, do, da...)."""
    return {p for p in _normalizar(texto).split() if len(p) > 2}


def identificar_comando(texto):
    """Casa o texto reconhecido com um dos comandos definidos no config.

    Tolerante: um comando é reconhecido se TODAS as palavras importantes de
    alguma de suas frases aparecerem no texto ouvido, mesmo fora de ordem ou
    com palavras a mais. Assim "registrar a parada" ainda casa com
    "registrar parada".
    """
    palavras_texto = _palavras_significativas(texto)
    for chave, formas in cfg.COMANDOS.items():
        for forma in formas:
            palavras_comando = _palavras_significativas(forma)
            if palavras_comando and palavras_comando.issubset(palavras_texto):
                return chave
    return None


def contem_palavra_ativacao(texto):
    return _normalizar(cfg.PALAVRA_ATIVACAO) in _normalizar(texto)


# ---------------------------------------------------------------------------
# EMOÇÃO DA VOZ
# ---------------------------------------------------------------------------
def _extrair_features(caminho_wav):
    """Extrai características acústicas (MFCC + energia + tom) de um .wav.
    É a MESMA função usada no treino (treino/treinar_emocao.py)."""
    import librosa
    y, sr_ = librosa.load(caminho_wav, sr=22050, duration=3.0)
    mfcc = librosa.feature.mfcc(y=y, sr=sr_, n_mfcc=20)
    rms = librosa.feature.rms(y=y)
    zcr = librosa.feature.zero_crossing_rate(y)
    features = np.concatenate([
        mfcc.mean(axis=1), mfcc.std(axis=1),
        [rms.mean(), rms.std(), zcr.mean()],
    ])
    return features


def analisar_emocao(caminho_wav=None):
    """Retorna (emocao, confianca_%). Ordem de preferência:
       1) modelo PRÉ-TREINADO (wav2vec2) — não exige treino nosso;
       2) nosso modelo próprio treinado (treino/treinar_emocao.py);
       3) simulado (sorteio) — só para o fluxo não travar sem modelo."""
    # 1) modelo pré-treinado (o do professor)
    if caminho_wav:
        try:
            from modulos import emocao_pretreinada
            if emocao_pretreinada.disponivel():
                return emocao_pretreinada.analisar(caminho_wav)
        except Exception:
            pass  # se falhar (sem internet/lib), tenta as próximas opções

    # 2) nosso modelo próprio treinado
    global _emo_modelo
    if caminho_wav and _TEM_LIBROSA and os.path.exists(cfg.CAMINHO_MODELO_EMOCAO):
        if _emo_modelo is None:
            _emo_modelo = joblib.load(cfg.CAMINHO_MODELO_EMOCAO)
        feats = _extrair_features(caminho_wav).reshape(1, -1)
        emocao = _emo_modelo.predict(feats)[0]
        conf = round(100 * float(max(_emo_modelo.predict_proba(feats)[0])), 1)
        return emocao, conf

    # 3) simulado
    emocao = random.choice(cfg.EMOCOES)
    return emocao, round(random.uniform(70, 95), 1)


# ---------------------------------------------------------------------------
# CAPTURA DE ÁUDIO / COMANDO
# ---------------------------------------------------------------------------
def escutar(simular=False, timeout=5):
    """Escuta o microfone (ou o teclado, no modo simulado) e devolve:
       (texto_reconhecido, caminho_do_wav ou None).
    O .wav é guardado para a análise emocional usar o MESMO áudio."""
    if simular or not _TEM_SR:
        texto = input("[SIMULADO] Fale (digite o comando): ")
        return texto, None

    r = sr.Recognizer()
    with sr.Microphone() as fonte:
        r.adjust_for_ambient_noise(fonte, duration=0.5)
        try:
            audio = r.listen(fonte, timeout=timeout, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            return "", None

    # salva o áudio para a emoção analisar o mesmo trecho
    os.makedirs(cfg.CAMINHO_FOTOS_REGISTRO, exist_ok=True)
    caminho_wav = os.path.join(cfg.CAMINHO_FOTOS_REGISTRO, "ultimo_comando.wav")
    with open(caminho_wav, "wb") as f:
        f.write(audio.get_wav_data())

    try:
        texto = r.recognize_google(audio, language="pt-BR")
    except Exception:
        texto = ""
    return texto, caminho_wav
