# -*- coding: utf-8 -*-
"""
copiloto.py — PROGRAMA PRINCIPAL
================================
Copiloto Inteligente de Viagem — sistema ÚNICO e integrado.

Fica em execução contínua, espera a palavra de ativação ("Guidão") e, a cada
comando, dispara a sequência completa:

    Ativação → Localização → Imagem → Emoção → Decisão → Registro

NÃO são programas separados: os módulos de voz, imagem, localização e decisão
trabalham juntos, em um só fluxo, neste arquivo.

Como rodar:
    python copiloto.py              # modo REAL (microfone + webcam)
    python copiloto.py --simular    # modo SIMULADO (teclado, sem hardware)
    python copiloto.py --demo       # cenário roteirizado para a apresentação
"""
import argparse
import os
import sys

import config as cfg
from modulos import decisao, diario, imagem, localizacao, resumo, voz

# ações que contam como "parada" (zeram o cronômetro de tempo sem parar)
ACOES_DE_PARADA = {"FAZER_UMA_PARADA", "ABASTECER", "ALIMENTAR-SE"}


def _status_modelos():
    """Diz o que está REAL (modelo treinado) e o que está SIMULADO (sorteado).
    Evita confundir uma emoção/cena aleatória com detecção de verdade."""
    def marca(caminho):
        return "REAL (treinado)" if os.path.exists(caminho) else "SIMULADO (sorteado — treine para ativar)"

    # emoção pode ser real por 2 caminhos: modelo pré-treinado OU o nosso
    try:
        from modulos import emocao_pretreinada
        emo_pronta = emocao_pretreinada.disponivel()
    except Exception:
        emo_pronta = False
    if emo_pronta:
        status_emo = "REAL (modelo pré-treinado wav2vec2)"
    elif os.path.exists(cfg.CAMINHO_MODELO_EMOCAO):
        status_emo = "REAL (nosso modelo treinado)"
    else:
        status_emo = "SIMULADO (instale torch+transformers ou treine para ativar)"

    print("  Status dos modelos:")
    print(f"    Decisão (Random Forest): {marca(cfg.CAMINHO_MODELO_DECISAO)}")
    print(f"    Emoção da voz..........: {status_emo}")
    print(f"    Imagem (cena)..........: {marca(cfg.CAMINHO_MODELO_IMAGEM)}")


def banner():
    print("=" * 64)
    print("  COPILOTO INTELIGENTE DE VIAGEM")
    print(f"  Palavra de ativação: \"{cfg.PALAVRA_ATIVACAO_EXIBICAO}\"")
    print(f"  Comandos: {', '.join(cfg.COMANDOS.keys())}")
    print("=" * 64)
    _status_modelos()
    print("=" * 64)


def processar_comando(chave_comando, texto_falado, caminho_wav,
                      loc, diario_bordo, simular, cenario_demo=None, inject_loc=None):
    """A SEQUÊNCIA COORDENADA (passos 2 a 6). Recebe o comando já reconhecido
    e executa localização → imagem → emoção → decisão → registro.

    inject_loc: usado pelo comando "simular viagem longa" na apresentação —
    injeta um contexto de tempo/distância (ex.: 160 min) MANTENDO voz e câmera
    reais, para demonstrar ao vivo o Random Forest reagindo à variável tempo."""

    # comando de encerramento tem tratamento próprio (gera o resumo)
    if chave_comando == "encerrar_viagem":
        resumo.gerar(diario_bordo, loc)
        return "ENCERRAR"

    n_registro = len(diario_bordo.registros) + 1

    # PASSO 2 — LOCALIZAÇÃO e contexto da viagem
    if cenario_demo:
        contexto = localizacao.simular_contexto(loc, **cenario_demo.get("loc", {}))
    elif inject_loc:
        contexto = localizacao.simular_contexto(loc, **inject_loc)
        print(f"   [cenário de viagem longa: {inject_loc.get('tempo_min')} min sem parar]")
    else:
        contexto = loc.registrar()

    # PASSO 3 — IMAGEM (captura + classifica a cena)
    foto = None if cenario_demo else imagem.capturar_foto(n_registro)
    if cenario_demo and "classe_imagem" in cenario_demo:
        classe_img, conf_img = cenario_demo["classe_imagem"], 92.0
    else:
        classe_img, conf_img = imagem.classificar(foto)
    contexto["classe_imagem"] = classe_img

    # PASSO 4 — EMOÇÃO (analisa o mesmo áudio do comando)
    if cenario_demo and "estado_emocional" in cenario_demo:
        emocao, conf_emo = cenario_demo["estado_emocional"], 84.0
    else:
        emocao, conf_emo = voz.analisar_emocao(caminho_wav)
    contexto["estado_emocional"] = emocao

    # PASSO 5 — DECISÃO (Random Forest recomenda a ação + explica)
    acao, conf_dec, justificativa, probs = decisao.decidir(contexto)

    # PASSO 6 — REGISTRO (diário de bordo)
    diario_bordo.adicionar(
        contexto, texto_falado or chave_comando, emocao, conf_emo,
        classe_img, conf_img, acao, conf_dec, justificativa, foto,
    )

    # se a ação foi de parada, atualiza o estado da viagem
    if acao in ACOES_DE_PARADA:
        loc.marcar_parada()

    return acao


def loop_principal(simular=False, demo=False):
    banner()
    loc = localizacao.Localizacao()
    diario_bordo = diario.Diario()

    # cenários roteirizados para uma demonstração convincente na banca
    roteiro_demo = [
        {"comando": "registrar_parada",
         "loc": {"tempo_min": 160, "distancia": 190, "hora": 12},
         "classe_imagem": "posto", "estado_emocional": "irritado"},
        {"comando": "marcar_ponto_turistico",
         "loc": {"tempo_min": 20, "hora": 15},
         "classe_imagem": "ponto_turistico", "estado_emocional": "alegre"},
        {"comando": "status_trecho",
         "loc": {"tempo_min": 40, "hora": 16},
         "classe_imagem": "estrada", "estado_emocional": "normal"},
    ]

    if demo:
        print("\n[MODO DEMONSTRAÇÃO — cenários roteirizados]\n")
        for passo in roteiro_demo:
            print(f"\n>>> Comando de voz: \"{passo['comando']}\" "
                  f"(cena: {passo['classe_imagem']}, voz: {passo['estado_emocional']})")
            processar_comando(passo["comando"], passo["comando"], None,
                              loc, diario_bordo, simular, cenario_demo=passo)
        resumo.gerar(diario_bordo, loc)
        return

    print(f"\nAguardando a palavra \"{cfg.PALAVRA_ATIVACAO_EXIBICAO}\"... "
          f"(Ctrl+C para sair)\n")
    try:
        while True:  # EXECUÇÃO CONTÍNUA
            texto, caminho_wav = voz.escutar(simular=simular)
            if not texto:
                continue

            # PASSO 1 — ATIVAÇÃO: só age depois da palavra de ativação
            if not voz.contem_palavra_ativacao(texto):
                if simular:
                    print(f"   (ignorado — falta a palavra \"{cfg.PALAVRA_ATIVACAO_EXIBICAO}\")")
                continue

            chave = voz.identificar_comando(texto)
            if chave is None:
                print(f"   Ouvi: \"{texto}\" — palavra de ativação reconhecida, "
                      f"mas nenhum comando. Tente: \"{cfg.PALAVRA_ATIVACAO_EXIBICAO}, registrar parada\".")
                continue

            print(f"\n>>> Ativado! Comando: {chave}")
            # comando de apresentação: injeta 160 min de viagem (voz e câmera reais)
            inj = {"tempo_min": 160, "distancia": 180} if chave == "simular_viagem_longa" else None
            resultado = processar_comando(chave, texto, caminho_wav,
                                          loc, diario_bordo, simular, inject_loc=inj)
            if resultado == "ENCERRAR":
                break
    except KeyboardInterrupt:
        print("\n\nEncerrando por Ctrl+C — gerando resumo...")
        resumo.gerar(diario_bordo, loc)


def main():
    p = argparse.ArgumentParser(description="Copiloto Inteligente de Viagem")
    p.add_argument("--simular", action="store_true",
                   help="modo sem hardware: comandos pelo teclado, emoção/imagem sorteadas")
    p.add_argument("--demo", action="store_true",
                   help="roda cenários roteirizados para a apresentação")
    args = p.parse_args()
    loop_principal(simular=args.simular, demo=args.demo)


if __name__ == "__main__":
    main()
