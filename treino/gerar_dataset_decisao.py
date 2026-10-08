# -*- coding: utf-8 -*-
"""
gerar_dataset_decisao.py
========================
Gera o conjunto de dados SINTÉTICO que treina o Random Forest da decisão.

Como funciona (e como explicar na apresentação):
  1. Sorteamos milhares de "cenários de viagem" aleatórios (combinações de
     hora, tempo dirigindo, distância, imagem detectada, emoção e nº de paradas).
  2. Uma função de REGRAS (regra_decisao) diz qual é a ação CORRETA em cada
     cenário. Essas regras são a nossa definição de "bom copiloto".
  3. O Random Forest aprende essas regras a partir dos exemplos. Depois de
     treinado, ele generaliza para cenários que nunca viu.

=> O dataset é NOSSO (construído pelo grupo) e 100% documentado, que é
   exatamente o que o enunciado exige. E como conhecemos as regras, sabemos
   explicar QUALQUER decisão do modelo.
"""
import csv
import os
import random
import sys

# permite rodar de dentro da pasta treino/ ou da raiz do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as cfg

N_AMOSTRAS = 4000
random.seed(42)  # reprodutível: todo mundo gera o mesmo dataset


def regra_decisao(hora, tempo_parada, distancia, classe_img, emocao, paradas):
    """A LÓGICA DO BOM COPILOTO. Primeira regra que casar decide (prioridade
    de cima para baixo). Segurança do motorista vem primeiro.

    Retorna uma das ações de cfg.DECISOES.
    """
    # 1) Irritação (tensão) com bastante tempo dirigindo -> parar por segurança
    if emocao == "irritado" and tempo_parada >= 90:
        return "FAZER_UMA_PARADA"

    # 2) Tristeza (baixo ânimo/atenção) + muito tempo na estrada -> descansar
    if emocao == "triste" and tempo_parada >= 120:
        return "FAZER_UMA_PARADA"

    # 3) Passou por um posto e já faz tempo/distância -> abastecer
    if classe_img == "posto" and (tempo_parada >= 90 or distancia >= 200):
        return "ABASTECER"

    # 4) Restaurante em horário de refeição -> comer
    if classe_img == "restaurante" and (hora in cfg.HORARIO_ALMOCO or hora in cfg.HORARIO_JANTAR):
        return "ALIMENTAR-SE"

    # 5) Ponto turístico e motorista disposto -> registrar o ponto
    if classe_img == "ponto_turistico" and emocao in ("alegre", "normal"):
        return "REGISTRAR_PONTO_TURISTICO"

    # 6) Cansaço acumulado (muito tempo sem parar), independente da emoção
    if tempo_parada >= 150:
        return "FAZER_UMA_PARADA"

    # 7) Nada disso -> seguir viagem
    return "CONTINUAR"


def sortear_cenario():
    return {
        "hora_do_dia": random.randint(0, 23),
        "tempo_desde_ultima_parada_min": random.randint(0, 240),
        "distancia_total_km": random.randint(0, 500),
        "classe_imagem": random.choice(cfg.CLASSES_IMAGEM),
        "estado_emocional": random.choice(cfg.EMOCOES),
        "paradas_feitas": random.randint(0, 10),
    }


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    destino = os.path.join(raiz, cfg.CAMINHO_DATASET_DECISAO)
    os.makedirs(os.path.dirname(destino), exist_ok=True)

    colunas = cfg.VARIAVEIS_RF + ["decisao"]
    contagem = {d: 0 for d in cfg.DECISOES}

    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=colunas)
        w.writeheader()
        for _ in range(N_AMOSTRAS):
            c = sortear_cenario()
            c["decisao"] = regra_decisao(
                c["hora_do_dia"],
                c["tempo_desde_ultima_parada_min"],
                c["distancia_total_km"],
                c["classe_imagem"],
                c["estado_emocional"],
                c["paradas_feitas"],
            )
            contagem[c["decisao"]] += 1
            w.writerow(c)

    print(f"Dataset gerado: {destino}  ({N_AMOSTRAS} linhas)")
    print("Distribuição das decisões:")
    for d, n in contagem.items():
        print(f"  {d:28s} {n:5d}  ({100*n/N_AMOSTRAS:.1f}%)")


if __name__ == "__main__":
    main()
