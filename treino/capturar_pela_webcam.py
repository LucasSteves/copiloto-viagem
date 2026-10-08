# -*- coding: utf-8 -*-
"""
capturar_pela_webcam.py
=======================
Tira fotos de treino usando a MESMA webcam da apresentação. Use isto para
capturar as cenas do jeito que o modelo vai vê-las no dia (ex.: a imagem
aberta no celular, mostrada para a câmera).

Como usar:
    python treino/capturar_pela_webcam.py posto
    (abre a webcam; ESPAÇO tira uma foto; Q encerra)

As fotos vão para dados/fotos/<classe>/webcam_XXX.jpg e entram no treino junto
com as imagens de licença aberta.

Precisa de: pip install opencv-python
"""
import os
import sys

import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in cfg.CLASSES_IMAGEM:
        print("Informe a classe. Opções:", ", ".join(cfg.CLASSES_IMAGEM))
        print("Ex.: python treino/capturar_pela_webcam.py posto")
        sys.exit(1)

    classe = sys.argv[1]
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta = os.path.join(raiz, "dados", "fotos", classe)
    os.makedirs(pasta, exist_ok=True)

    # continua a numeração de onde parou
    existentes = [f for f in os.listdir(pasta) if f.startswith("webcam_")]
    n = len(existentes)

    cam = cv2.VideoCapture(cfg.CAMERA_INDICE)
    if not cam.isOpened():
        print("Não consegui abrir a webcam.")
        sys.exit(1)

    print(f"Classe '{classe}'. ESPAÇO = tirar foto | Q = sair")
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        cv2.imshow(f"Capturando: {classe}  (ESPACO=foto, Q=sair)", frame)
        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord(" "):
            n += 1
            caminho = os.path.join(pasta, f"webcam_{n:03d}.jpg")
            cv2.imwrite(caminho, frame)
            print(f"  salvou {caminho}")
        elif tecla == ord("q"):
            break

    cam.release()
    cv2.destroyAllWindows()
    print(f"Fim. {n} fotos na pasta de '{classe}'.")


if __name__ == "__main__":
    main()
