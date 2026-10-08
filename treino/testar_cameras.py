# -*- coding: utf-8 -*-
"""Descobre qual número de câmera é o do DroidCam (celular)."""
import cv2

print("Procurando cameras... (feche cada janela com a tecla Q)\n")
encontradas = []
for indice in range(5):  # testa 0 a 4
    cam = cv2.VideoCapture(indice)
    if not cam.isOpened():
        cam.release()
        continue
    ok, frame = cam.read()
    if not ok:
        cam.release()
        continue
    encontradas.append(indice)
    print(f"Camera {indice}: ABERTA. E a do celular (DroidCam)? Aperte Q para a proxima.")
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        cv2.putText(frame, f"Camera {indice}  -  Q = proxima", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        cv2.imshow("Teste de cameras", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()

print()
if encontradas:
    print(f"Cameras encontradas nos numeros: {encontradas}")
    print("Coloque o numero da que mostrava o CELULAR em config.py: CAMERA_INDICE = <numero>")
else:
    print("Nenhuma camera encontrada. Confirme que o DroidCam esta transmitindo antes de rodar.")