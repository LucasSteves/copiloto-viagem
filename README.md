# Copiloto Inteligente de Viagem

Projeto 2 — Inteligência Artificial · Unimax Indaiatuba · Prof. Rogerio Morandi

Sistema **único e integrado** que fica em execução contínua, espera a palavra de
ativação **"Guidão"** e, a cada comando de voz, dispara a sequência:

> **Ativação → Localização → Imagem → Emoção → Decisão → Registro**

O núcleo da decisão é um **Random Forest** que recebe 6 variáveis e recomenda
uma de 5 ações, sempre com uma justificativa explicável.

---

## Como rodar - Fala professor, achou o easteregg do trabalho, não se esqueça de rodar os comandos no python 3.12 para não dar erro. Tenha um ótimo dia com uma xicara de café!!

```bash
pip install -r requirements.txt

python copiloto.py           # modo REAL (microfone + webcam)
python copiloto.py --simular # modo SIMULADO (comandos pelo teclado, sem hardware)
python copiloto.py --demo    # cenários roteirizados para a apresentação
```

O sistema **funciona mesmo sem as bibliotecas de voz/imagem**: nesse caso ele
cai no modo simulado automaticamente. Isso permite testar o fluxo inteiro em
qualquer máquina.

### Treinar os modelos

```bash
python treino/gerar_dataset_decisao.py   # gera o dataset de decisão (sintético)
python treino/treinar_decisao.py         # treina o Random Forest  ✅ já pronto
python treino/baixar_imagens.py          # baixa imagens de licença aberta (Openverse)
python treino/capturar_pela_webcam.py posto   # tira fotos pela própria webcam
py -3.12 treino/treinar_imagem.py     # treina o classificador de cena (PyTorch)
python treino/treinar_emocao.py          # treina a emoção (áudios do trabalho anterior)
```

---

## Estrutura

```
copiloto_viagem/
├── copiloto.py              # PROGRAMA PRINCIPAL — loop contínuo + integração
├── config.py               # todas as personalizações do grupo (documentadas)
├── modulos/
│   ├── voz.py              # comando falado + emoção da voz
│   ├── imagem.py           # webcam + classificação da cena
│   ├── localizacao.py      # cidade simulada + horário + contexto
│   ├── decisao.py          # Random Forest + justificativa
│   ├── diario.py           # diário de bordo
│   └── resumo.py           # resumo da viagem
├── treino/                 # geração de dataset e treino dos 3 modelos
├── dados/                  # dataset, fotos, áudios, diário, registros
└── modelos/                # modelos treinados (.joblib / .pt)
```

---

## Personalizações do grupo (entregável 3)

Tudo isto está definido em `config.py`.

| Item | Definição |
|---|---|
| **Palavra de ativação** | `Guidão` |
| **Comandos de voz (5)** | registrar parada · marcar ponto turístico · preciso abastecer · como está o trecho · encerrar viagem |
| **Classes de imagem (5)** | estrada · posto · restaurante · ponto_turistico · area_urbana |
| **Variáveis do RF (6)** | hora do dia · tempo desde a última parada · distância total · classe da imagem · estado emocional (normal·alegre·triste·irritado) · paradas feitas |
| **Decisões (5)** | CONTINUAR · FAZER_UMA_PARADA · ABASTECER · ALIMENTAR-SE · REGISTRAR_PONTO_TURISTICO |

---

## Documentação do dataset (entregável 2)

**Três modelos, três datasets:**

### 1. Decisão — Random Forest (dataset sintético, construído pelo grupo)
- Gerado por `treino/gerar_dataset_decisao.py`: 4000 cenários de viagem sorteados.
- Cada cenário é rotulado pela função `regra_decisao()`, que codifica a nossa
  definição de "bom copiloto" (segurança em primeiro lugar).
- **Por que sintético?** Porque conhecemos as regras, sabemos explicar qualquer
  decisão do modelo — e é reprodutível (semente fixa, todo mundo gera o mesmo).
- **Resultado do treino:** ~99% de acurácia no conjunto de teste. Variáveis mais
  influentes: *tempo sem parar* (0,42), *classe da imagem* (0,27), *emoção* (0,14).

### 2. Imagem — classificador de cena (licença aberta + fotos próprias)
- **Imagens de licença aberta:** `python treino/baixar_imagens.py` baixa ~40 por
  classe da Openverse (Creative Commons / domínio público) e grava a atribuição
  de cada foto em `dados/fotos/LICENCAS.csv`. Nada é copiado do Google — é uso legal.
- **Fotos próprias:** `python treino/capturar_pela_webcam.py <classe>` tira fotos
  com a MESMA webcam da apresentação (ex.: cena aberta no celular mostrada à câmera).
  Isso garante o "coletamos nós mesmos" e treina o modelo parecido com o que ele
  verá no dia.
- Treino por transfer learning (MobileNetV2 em PyTorch) em `treino/treinar_imagem.py` — sem TensorFlow, reaproveita o torch da emoção.
- As imagens **não precisam ser de Indaiatuba**: o modelo aprende o tipo de cena
  (posto, estrada...), que é parecido em qualquer lugar.

### 3. Emoção da voz — DOIS caminhos

**Caminho A — modelo pré-treinado (recomendado, sem treino):**
- Usa `Aniemore/wav2vec2-emotion-v1-crosslingual` (o mesmo do utilitário do professor).
- Não precisa coletar nem treinar áudio: o modelo já vem pronto.
- Instale `pip install -r requirements-emocao.txt` (pesado; baixa ~360 MB na 1ª vez).
- As 7 emoções do modelo são traduzidas para as nossas 4 (normal, alegre, triste,
  irritado) em `modulos/emocao_pretreinada.py`.

**Caminho B — nosso modelo próprio (reuso do trabalho anterior):**
- Emoções: normal, alegre, triste, irritado, a partir das gravações do grupo.
- Organize os áudios em `dados/audios/<emocao>/` e rode `treino/treinar_emocao.py`.
- Leve (só scikit-learn), mas exige os áudios.

O sistema tenta o Caminho A; se não estiver instalado, usa o B; se nenhum, simula.
Em qualquer caso, o modelo que **nós treinamos** e documentamos é o Random Forest
da decisão — os módulos de percepção podem usar modelos prontos.

---

## Diário de bordo (entregável 4)

Cada comando bem-sucedido gera uma entrada completa, impressa na tela e salva em
`dados/diario_de_bordo.json`. Exemplo real produzido pelo sistema:

```
DIÁRIO DE BORDO  ·  Registro 01
Horário: 16/09/2026 - 22:43     Local: Indaiatuba - SP
Coordenadas: -23.09, -47.21
Comando reconhecido:  "registrar_parada"
Estado da voz:  IRRITADO — 84.0%
Imagem classificada:  posto — 92.0%
Decisão do Random Forest:  FAZER_UMA_PARADA — 93.5%
  ↳ O motorista deve descansar: a voz indica irritado e já são 160 min sem parar.
```

## Resumo da viagem (entregável 5)

O comando **"encerrar viagem"** (ou Ctrl+C) consolida distância, paradas, locais,
emoção predominante, maior trecho sem parar e a lista de fotos em ordem.
