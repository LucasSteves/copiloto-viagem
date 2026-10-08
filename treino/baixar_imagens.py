# -*- coding: utf-8 -*-
"""
baixar_imagens.py
=================
Baixa imagens de LICENÇA ABERTA (Creative Commons / domínio público) para cada
classe do dataset de cena, usando a API pública da Openverse — que agrega
fotos do Flickr, Wikimedia, museus etc. e informa a licença de cada uma.

Por que assim (e não do Google Imagens)?
  - Fotos do Google/Street View são protegidas por direitos autorais: usar
    cairia no "dataset copiado" que o enunciado penaliza.
  - A Openverse só devolve imagens com licença que PERMITE uso, e o script
    salva a atribuição de cada foto em dados/fotos/LICENCAS.csv — isso vira
    a documentação legal do dataset (entregável 2).

Recomendação de uso: baixem estas imagens de licença aberta PARA ENCHER cada
classe, e complementem com fotos tiradas pela própria webcam
(treino/capturar_pela_webcam.py) — assim o modelo treina parecido com o que
verá na apresentação (celular mostrado para a câmera).

Rodar:
    pip install requests
    python treino/baixar_imagens.py
"""
import csv
import os
import sys
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg

# termos de busca (em inglês retornam mais resultados) por classe
TERMOS = {
    "estrada":         "highway road asphalt",
    "posto":           "gas station fuel pump",
    "restaurante":     "restaurant interior diner",
    "ponto_turistico": "scenic viewpoint mountain landscape",
    "area_urbana":     "city street buildings",
}

POR_CLASSE = 40                     # quantas imagens por classe
LICENCAS_ACEITAS = "cc0,pdm,by,by-sa"  # todas permitem uso com atribuição
API = "https://api.openverse.org/v1/images/"
CABECALHO = {"User-Agent": "CopilotoViagem-Unimax/1.0 (trabalho academico)"}


def baixar_classe(classe, termo, destino_base):
    pasta = os.path.join(destino_base, classe)
    os.makedirs(pasta, exist_ok=True)
    registros = []
    baixadas = 0
    pagina = 1

    while baixadas < POR_CLASSE and pagina <= 10:
        params = {
            "q": termo, "license": LICENCAS_ACEITAS,
            "page_size": 20, "page": pagina, "mature": "false",
        }
        try:
            r = requests.get(API, params=params, headers=CABECALHO, timeout=30)
        except Exception as e:
            print(f"    erro de rede: {e}")
            break
        if r.status_code != 200:
            print(f"    API retornou {r.status_code} (pode ser limite de uso). "
                  f"Tente de novo mais tarde ou registre um token gratuito na Openverse.")
            break

        resultados = r.json().get("results", [])
        if not resultados:
            break

        for item in resultados:
            if baixadas >= POR_CLASSE:
                break
            url = item.get("url")
            if not url:
                continue
            try:
                img = requests.get(url, headers=CABECALHO, timeout=30)
                if img.status_code != 200 or "image" not in img.headers.get("Content-Type", ""):
                    continue
                nome = f"{classe}_{baixadas + 1:03d}.jpg"
                with open(os.path.join(pasta, nome), "wb") as f:
                    f.write(img.content)
                registros.append({
                    "arquivo": nome,
                    "classe": classe,
                    "licenca": f"{item.get('license', '')} {item.get('license_version', '')}".strip(),
                    "autor": item.get("creator", "") or "",
                    "fonte": item.get("foreign_landing_url", "") or "",
                })
                baixadas += 1
            except Exception:
                continue
        pagina += 1
        time.sleep(1)  # educado com a API

    print(f"  {classe:16s}: {baixadas} imagens baixadas")
    return registros


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino_base = os.path.join(raiz, "dados", "fotos")
    todos = []

    print("Baixando imagens de licença aberta (Openverse)...\n")
    for classe, termo in TERMOS.items():
        todos += baixar_classe(classe, termo, destino_base)

    # documentação das licenças (entregável 2)
    csv_licencas = os.path.join(destino_base, "LICENCAS.csv")
    with open(csv_licencas, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["arquivo", "classe", "licenca", "autor", "fonte"])
        w.writeheader()
        w.writerows(todos)

    print(f"\nTotal: {len(todos)} imagens.")
    print(f"Licenças documentadas em: {csv_licencas}")
    if not todos:
        print("\nNenhuma imagem baixada — verifique a internet ou tente mais tarde. "
              "Vocês também podem colocar fotos manualmente nas pastas dados/fotos/<classe>/.")


if __name__ == "__main__":
    main()
