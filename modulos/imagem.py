# -*- coding: utf-8 -*-
"""
modulos/imagem.py
=================
Tira uma foto pela webcam e classifica o CONTEXTO da cena em uma das classes
definidas no config (estrada, posto, restaurante, ponto_turistico, area_urbana).

Modo REAL: usa `opencv` para a webcam e o modelo treinado em PyTorch
           (treino/treinar_imagem.py) para classificar.
Modo SIMULADO: sorteia a classe e não abre a câmera — para rodar sem hardware.

Usa PyTorch (o mesmo torch da emoção) — NÃO precisa de TensorFlow.
"""
import os
import random
import time

import config as cfg

# webcam (opcional)
try:
    import cv2
    _TEM_CV2 = True
except Exception:
    _TEM_CV2 = False

# torch (opcional) — se não houver, a imagem cai no modo simulado
try:
    import torch  # noqa: F401
    _TEM_TORCH = True
except Exception:
    _TEM_TORCH = False

_img_modelo = None
_img_classes = None
_img_transform = None
TAMANHO = 224  # entrada do MobileNetV2


def _construir_transform():
    from torchvision import transforms
    return transforms.Compose([
        transforms.Resize((TAMANHO, TAMANHO)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])


def _carregar_modelo():
    """Carrega o modelo torch salvo (uma vez). Retorna (modelo, classes) ou None."""
    global _img_modelo, _img_classes, _img_transform
    if not _TEM_TORCH or not os.path.exists(cfg.CAMINHO_MODELO_IMAGEM):
        return None
    if _img_modelo is None:
        import torch
        from torchvision import models
        ckpt = torch.load(cfg.CAMINHO_MODELO_IMAGEM, map_location="cpu")
        classes = ckpt["classes"]
        modelo = models.mobilenet_v2(weights=None)
        modelo.classifier[1] = torch.nn.Linear(
            modelo.classifier[1].in_features, len(classes))
        modelo.load_state_dict(ckpt["state_dict"])
        modelo.eval()
        _img_modelo, _img_classes = modelo, classes
        _img_transform = _construir_transform()
    return _img_modelo, _img_classes


def capturar_foto(id_registro):
    """Captura um frame da webcam e salva. Retorna o caminho (ou None simulado)."""
    os.makedirs(cfg.CAMINHO_FOTOS_REGISTRO, exist_ok=True)
    caminho = os.path.join(cfg.CAMINHO_FOTOS_REGISTRO, f"registro_{id_registro:03d}.jpg")
    if not _TEM_CV2:
        return None
    cam = cv2.VideoCapture(cfg.CAMERA_INDICE)
    # "aquece" a câmera: descarta os primeiros quadros (o DroidCam mostra uma
    # tela inicial antes de o vídeo engatar) e usa um quadro já estável.
    frame = None
    for _ in range(30):
        ok, frame = cam.read()
        time.sleep(0.05)
    cam.release()
    if frame is not None:
        cv2.imwrite(caminho, frame)
        return caminho
    return None


def classificar(caminho_foto=None):
    """Retorna (classe, confianca_%). Usa o modelo treinado se houver foto e
    modelo; senão sorteia (simulado)."""
    carregado = _carregar_modelo()
    if caminho_foto and carregado and os.path.exists(caminho_foto):
        import torch
        from PIL import Image
        modelo, classes = carregado
        img = Image.open(caminho_foto).convert("RGB")
        x = _img_transform(img).unsqueeze(0)
        with torch.inference_mode():
            logits = modelo(x)
            probs = torch.softmax(logits, dim=1)[0]
            idx = int(torch.argmax(probs))
        return classes[idx], round(100 * float(probs[idx]), 1)
    # simulado
    classe = random.choice(cfg.CLASSES_IMAGEM)
    return classe, round(random.uniform(70, 96), 1)
