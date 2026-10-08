# -*- coding: utf-8 -*-
"""
treinar_imagem.py
=================
Treina o classificador de CENA usando transfer learning com MobileNetV2 em
PyTorch (o mesmo torch da emoção — NÃO precisa de TensorFlow).

Coleta das fotos (feita pelo grupo — é o "dataset próprio"):
    dados/fotos/estrada/*.jpg
    dados/fotos/posto/*.jpg
    dados/fotos/restaurante/*.jpg
    dados/fotos/ponto_turistico/*.jpg
    dados/fotos/area_urbana/*.jpg
    (use treino/baixar_imagens.py e treino/capturar_pela_webcam.py para juntar)

Rodar:
    py -3.12 -m pip install -r requirements-imagem.txt
    py -3.12 treino/treinar_imagem.py

Na 1ª vez baixa os pesos pré-treinados do MobileNetV2 (~14 MB) da internet.
"""
import os
import sys

import torch
from torch import nn, optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg

TAMANHO = 224
BATCH = 16
EPOCAS = 12


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dir_fotos = os.path.join(raiz, "dados", "fotos")

    # aumento de dados no treino; validação sem aumento
    norm = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
    t_treino = transforms.Compose([
        transforms.Resize((TAMANHO, TAMANHO)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(), norm,
    ])

    dataset = datasets.ImageFolder(dir_fotos, transform=t_treino)
    if len(dataset) < 20:
        print("Poucas imagens. Junte fotos em dados/fotos/<classe>/ antes de treinar "
              "(use baixar_imagens.py e capturar_pela_webcam.py).")
        sys.exit(1)

    classes = dataset.classes  # nomes das pastas = classes
    print(f"{len(dataset)} imagens em {len(classes)} classes: {classes}")

    # 80% treino / 20% validação
    n_val = max(1, int(0.2 * len(dataset)))
    n_tr = len(dataset) - n_val
    treino_ds, val_ds = random_split(dataset, [n_tr, n_val],
                                     generator=torch.Generator().manual_seed(42))
    dl_tr = DataLoader(treino_ds, batch_size=BATCH, shuffle=True)
    dl_val = DataLoader(val_ds, batch_size=BATCH)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # base pré-treinada (ImageNet), congelada; treinamos só a "cabeça"
    modelo = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
    for p in modelo.features.parameters():
        p.requires_grad = False
    modelo.classifier[1] = nn.Linear(modelo.classifier[1].in_features, len(classes))
    modelo = modelo.to(device)

    criterio = nn.CrossEntropyLoss()
    otimizador = optim.Adam(modelo.classifier.parameters(), lr=1e-3)

    for epoca in range(1, EPOCAS + 1):
        modelo.train()
        for x, y in dl_tr:
            x, y = x.to(device), y.to(device)
            otimizador.zero_grad()
            loss = criterio(modelo(x), y)
            loss.backward()
            otimizador.step()

        # avaliação
        modelo.eval()
        acertos = total = 0
        with torch.inference_mode():
            for x, y in dl_val:
                x, y = x.to(device), y.to(device)
                pred = modelo(x).argmax(1)
                acertos += (pred == y).sum().item()
                total += y.size(0)
        acc = 100 * acertos / max(1, total)
        print(f"Época {epoca:2d}/{EPOCAS}  -  acurácia validação: {acc:.1f}%")

    destino = os.path.join(raiz, cfg.CAMINHO_MODELO_IMAGEM)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    torch.save({"state_dict": modelo.state_dict(), "classes": classes}, destino)
    print(f"\nModelo de imagem salvo em: {destino}")
    print("Classes (ordem):", classes)


if __name__ == "__main__":
    main()
