# -*- coding: utf-8 -*-
"""
config.py
=========
Todas as PERSONALIZAÇÕES do grupo em um só lugar.
Este arquivo é, ao mesmo tempo, código e documentação do entregável
"Registro das personalizações".

Grupo: (preencham os nomes aqui)
Disciplina: Inteligência Artificial - Unimax Indaiatuba
Professor: Rogerio Morandi
Projeto 2: Copiloto Inteligente de Viagem
"""

# ---------------------------------------------------------------------------
# 1) PALAVRA DE ATIVAÇÃO (wake word) — única do grupo
# ---------------------------------------------------------------------------
PALAVRA_ATIVACAO = "guidao"          # o sistema compara sem acento e em minúsculo
PALAVRA_ATIVACAO_EXIBICAO = "Guidão"  # como aparece na tela / diário

# ---------------------------------------------------------------------------
# 2) COMANDOS DE VOZ (mínimo 4 — temos 5)
#    chave interna -> lista de formas de falar que disparam o comando
# ---------------------------------------------------------------------------
COMANDOS = {
    "registrar_parada":       ["registrar parada", "registra parada", "marcar parada"],
    "marcar_ponto_turistico": ["marcar ponto turistico", "registrar ponto turistico", "ponto turistico"],
    "abastecer":              ["preciso abastecer", "abastecer", "vou abastecer"],
    "status_trecho":          ["como esta o trecho", "status do trecho", "como esta a viagem"],
    "encerrar_viagem":        ["encerrar viagem", "finalizar viagem", "terminar viagem"],
    # comando de apresentação: injeta contexto de viagem longa (160 min) para
    # demonstrar ao vivo o Random Forest recomendando parada.
    "simular_viagem_longa":   ["simular viagem longa", "simula viagem longa", "viagem longa"],
}

# ---------------------------------------------------------------------------
# 3) CLASSES DE IMAGEM (mínimo 4 — temos 5)
#    O modelo de imagem é treinado para reconhecer estas classes.
#    As fotos de treino ficam em: dados/fotos/<classe>/*.jpg
# ---------------------------------------------------------------------------
CLASSES_IMAGEM = [
    "estrada",          # rodovia / pista
    "posto",            # posto de combustível
    "restaurante",      # restaurante / lanchonete
    "ponto_turistico",  # mirante / paisagem / atração
    "area_urbana",      # cidade / prédios
]

# ---------------------------------------------------------------------------
# 4) ESTADOS EMOCIONAIS DA VOZ
#    Reaproveitados do trabalho anterior do grupo (mesmas gravações).
#    Os áudios de treino ficam em: dados/audios/<emocao>/*.(wav|mp3|m4a|ogg)
#    Significado na direção:
#      normal   -> baseline, sem sinal crítico
#      alegre   -> disposto/animado (bom para registrar pontos turísticos)
#      triste   -> baixo ânimo/atenção (sinal de descanso em viagem longa)
#      irritado -> tensão/estresse (sinal de pausa por segurança)
# ---------------------------------------------------------------------------
EMOCOES = ["normal", "alegre", "triste", "irritado"]

# ---------------------------------------------------------------------------
# 5) VARIÁVEIS DE ENTRADA DO RANDOM FOREST (mínimo 5 — temos 6)
#    A ordem aqui é a MESMA usada no treino e na decisão.
# ---------------------------------------------------------------------------
VARIAVEIS_RF = [
    "hora_do_dia",                    # 0..23
    "tempo_desde_ultima_parada_min",  # minutos desde a última parada
    "distancia_total_km",             # km acumulados na viagem
    "classe_imagem",                  # categórica (ver CLASSES_IMAGEM)
    "estado_emocional",               # categórica (ver EMOCOES)
    "paradas_feitas",                 # quantas paradas já foram feitas
]

# ---------------------------------------------------------------------------
# 6) DECISÕES POSSÍVEIS DO RANDOM FOREST (mínimo 3 — temos 5)
# ---------------------------------------------------------------------------
DECISOES = [
    "CONTINUAR",
    "FAZER_UMA_PARADA",
    "ABASTECER",
    "ALIMENTAR-SE",
    "REGISTRAR_PONTO_TURISTICO",
]

# ---------------------------------------------------------------------------
# Codificação das variáveis categóricas em números (o Random Forest só
# entende números). Mesmo mapa no treino e na hora de decidir.
# ---------------------------------------------------------------------------
COD_CLASSE_IMAGEM = {c: i for i, c in enumerate(CLASSES_IMAGEM)}
COD_EMOCAO = {e: i for i, e in enumerate(EMOCOES)}

# Faixas de horário consideradas "de refeição" (usado nas regras de decisão)
HORARIO_ALMOCO = range(11, 15)   # 11h às 14h
HORARIO_JANTAR = range(19, 22)   # 19h às 21h

# Caminhos usados pelo projeto
CAMINHO_DATASET_DECISAO = "dados/decisao_dataset.csv"
CAMINHO_MODELO_DECISAO = "modelos/random_forest.joblib"
CAMINHO_MODELO_IMAGEM = "modelos/imagem_mobilenet.pt"
CAMINHO_MODELO_EMOCAO = "modelos/emocao.joblib"
CAMINHO_DIARIO = "dados/diario_de_bordo.json"
CAMINHO_FOTOS_REGISTRO = "dados/registros"  # fotos salvas a cada comando
CAMERA_INDICE = 0