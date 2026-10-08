# Roteiro da apresentação (entregável 6)

A avaliação foca no **processo** e na **capacidade de explicar**. Não basta rodar.

## Roteiro sugerido (≈ 8 min)

1. **Abertura (30s).** "Sistema único que combina voz, imagem e localização, e
   um Random Forest que decide a ação. Palavra de ativação: *Guidão*."
2. **Mostrar a integração (1 min).** Abrir `copiloto.py` e mostrar a sequência
   Ativação → Localização → Imagem → Emoção → Decisão → Registro em UM arquivo.
3. **Demonstração ao vivo (3 min).** Rodar `python copiloto.py`, falar
   *"Guidão, registrar parada"* em tom irritado, mostrar a câmera para uma cena de
   posto. O sistema registra e o RF recomenda **FAZER_UMA_PARADA**.
   - Ter o `--demo` como plano B se o mic/câmera falhar (mas o vivo é obrigatório).
4. **Explicar UMA decisão (2 min).** Ver seção abaixo.
5. **Resumo da viagem (1 min).** Comando *"Guidão, encerrar viagem"* → mostra
   números e fotos em ordem.
6. **Fechar (30s).** Dataset próprio, 3 modelos treinados, tudo integrado.

## Como responder "por que o modelo recomendou isso?"

O modelo **não** decide por acaso. Três pilares:

1. **As variáveis de entrada.** Mostrar o contexto daquele registro (ex.: 160 min
   sem parar, voz cansada, posto na cena).
2. **A importância das variáveis** (sai no treino):
   - tempo sem parar → 0,42 (o que mais pesa)
   - classe da imagem → 0,27
   - emoção da voz → 0,14
   Ou seja, o modelo aprendeu que **cansaço + tempo na estrada** é o fator central
   de segurança — exatamente o que esperamos de um copiloto.
3. **A justificativa em texto** que o próprio sistema imprime ("O motorista deve
   descansar: a voz indica irritado e já são 160 min sem parar").

Frase pronta para a banca:
> "O Random Forest recomendou FAZER_UMA_PARADA porque as variáveis de maior peso
> — tempo sem parar e estado emocional (irritado) — indicavam risco de fadiga. Treinamos o
> modelo com 4000 cenários rotulados pela nossa regra de bom copiloto, e ele
> atingiu 99% de acurácia no teste, reproduzindo essa lógica de segurança."

## Perguntas prováveis e respostas

- **"O dataset é copiado?"** Não. A decisão usa cenários gerados pela nossa
  função de regras (com semente fixa, documentada). As imagens são de **licença
  aberta** (com atribuição registrada em `LICENCAS.csv`) mais fotos tiradas pela
  nossa própria webcam. Os áudios são gravações nossas (do trabalho anterior).
- **"O Random Forest é decorativo?"** Não: ele é o único ponto que escolhe a ação;
  trocar as variáveis muda a recomendação (dá para demonstrar ao vivo).
- **"E se a câmera errar a classe?"** A confiança aparece no diário; a decisão
  ainda considera as outras 5 variáveis, então não depende só da imagem.
- **"Onde está a fusão multimodal?"** Em `copiloto.py`: voz, imagem e localização
  viram um único vetor de contexto que alimenta o RF.

## Checklist final (slide 18 do enunciado)

- [x] Sistema em execução contínua esperando a palavra de ativação
- [x] Pelo menos 4 comandos de voz (temos 5)
- [x] Análise emocional da voz registrada (com % de confiança)
- [x] Localização (cidade simulada) + horário gravados
- [x] Câmera captura e classifica em uma das classes
- [x] Random Forest com 6 variáveis recomenda 1 de 5 ações
- [x] Cada comando gera entrada completa no diário
- [x] Resumo final com fotos em ordem cronológica
- [x] Grupo consegue explicar as decisões
- [x] **Personalização diferente dos outros grupos** — confirmar a palavra "Guidão"
- [x] **Imagens**: baixar de licença aberta + tirar fotos pela webcam, e treinar
- [x] **Emoção**: instalar requirements-emocao.txt (modelo pré-treinado) OU treinar com os áudios do trabalho anterior
