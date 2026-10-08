# Copiloto Inteligente de Viagem

Projeto 2 de IA (Unimax Indaiatuba). Assistente de voz que espera a palavra "Guidão" e roda o fluxo:
Ativação → Localização → Imagem → Emoção → Decisão (Random Forest) → Registro no diário.

## Rodar
- Use **Python 3.12** (outras versões quebram as libs de voz/imagem).
- `pip install -r requirements.txt` (extras: `requirements-imagem.txt`, `requirements-emocao.txt`)
- `python copiloto.py --simular` — sem microfone/webcam (comandos pelo teclado)
- `python copiloto.py --demo` — cenários roteirizados; `python copiloto.py` — modo real

## Estrutura
- `copiloto.py` — loop principal e integração; `config.py` — personalizações do grupo
- `modulos/` — voz, imagem, localização, decisão, diário, resumo
- `treino/` — gera datasets e treina os modelos (salvos em `modelos/`)
- `dados/` — dataset, fotos de treino, diário de bordo (`diario_de_bordo.json`)

## Convenções
- Código e comentários em português.
- Sem libs de voz/imagem o sistema cai sozinho no modo simulado; preserve esse fallback.
