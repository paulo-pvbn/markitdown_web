# Sessão: Comparar Tesseract vs. rapidocr-onnxruntime em qualidade de OCR

- **Data/hora**: 2026-09-03 17:22–17:35
- **Versão resultante**: v1.00 (sem nova tag — investigação, não implementação)
- **Commit**: (ver commits desta sessão no log do `main`, feitos após este relatório)
- **Arquivos de exemplo usados**: páginas 11, 51 e 121 (índices 10, 50, 120) de `webapp/raw/InvestBot/733086206-Mercado-Financeiro-13ed.pdf` — as mesmas 3 páginas já usadas na Ordem 03, renderizadas de novo a 300 DPI.

## O que foi feito
- **Nenhuma alteração de código** (`app.py`/`watch.py` intocados) — investigação pura, conforme escopo.
- Confirmado que o Tesseract **já estava instalado** na máquina (`C:\Program Files\Tesseract-OCR`, v5.5.0.20241111), só não estava no `PATH` — não foi necessário instalar nada nem perguntar ao usuário sobre instalação (o caso de borda da ordem só se aplicaria se o binário estivesse ausente).
- Confirmado que os idiomas `por` e `eng` já estavam disponíveis no Tesseract (`--list-langs`).
- Renderizadas as mesmas 3 páginas da Ordem 03 a **300 DPI** (a Ordem 03 tinha usado uma resolução mais baixa — 144 DPI — então esta renderização é nova, especificamente pra esta comparação).
- Instalado `pytesseract` (wrapper Python, sem motor embutido) e `rapidocr-onnxruntime` no venv de teste — ambos **desinstalados ao final**, junto com as dependências transitivas que trouxeram (`opencv-python`, `pyclipper`, `shapely`, `PyYAML`).
- Rodado Tesseract (`por+eng`, PSM padrão) nas 3 páginas, com tempo medido.
- Rodado Tesseract com 3 `--psm` alternativos (4, 6, 11) especificamente na página 121 (tabela), pra ver se algum modo orientado a bloco/coluna melhorava a extração da tabela.
- Rodado `rapidocr-onnxruntime` de novo nas mesmas 3 imagens a 300 DPI, na mesma sessão — pra ter tempo comparável ao Tesseract (evitando comparar contra o tempo da Ordem 03, que usou resolução e carga de máquina diferentes).
- Textos de cada motor salvos em arquivos separados por página, fora do repositório (pasta de scratchpad da sessão).

## Comparação objetiva, por página

| Página | Critério | Tesseract (`por+eng`, PSM padrão) | rapidocr-onnxruntime |
|---|---|---|---|
| 11 (sumário) | Acentos preservados | **Sim** | Não |
| 11 | Espaçamento entre palavras | **Sim** | Não (palavras coladas) |
| 11 | Tempo | **4,0s** | 36,8s |
| 51 (texto corrido) | Acentos preservados | **Sim** | Não |
| 51 | Espaçamento entre palavras | **Sim** | Não (palavras coladas) |
| 51 | Tempo | **4,5s** | 79,1s |
| 121 (tabela de rating) | Acentos preservados | **Sim** (no texto corrido da página; a coluna gráfica de ícones saiu como ruído em ambos os motores) | Não |
| 121 | Ordem de coluna da tabela | **Parcial** — PSM padrão manteve a tabela separada do texto corrido, mas a faixa gráfica de ícones/cores à esquerda da tabela saiu como caracteres soltos (`go`, `£5`, `fc 3`...); PSM 4/6/11 pioraram, misturando tabela e texto corrido na mesma linha | Embaralhada — mesma mistura de colunas, sem separação nem no texto corrido |
| 121 | Tempo | **5,0s** (PSM padrão) | 58,9s |

**Medição quantitativa adicional (página 51, texto corrido)**:
- Caracteres acentuados preservados: **115 (Tesseract) vs. 5 (rapidocr)** — perda quase total de acentuação no rapidocr.
- Tokens com mais de 15 caracteres (indício de palavras coladas por falta de espaço): **0 (Tesseract) vs. 74 (rapidocr)**, em 277–649 tokens totais.
- Tamanho médio de token: **5,4 caracteres (Tesseract, compatível com o português)** vs. **12,6 (rapidocr, inflado por concatenação)**.

## Teste de `--psm` alternativo (página 121, tabela)
- **PSM padrão (automático, PSM 3)**: manteve a tabela de rating como bloco separado do texto corrido ao lado — não misturou as duas colunas linha a linha. Só a faixa decorativa de ícones/cores (não é texto real, é indicador visual) saiu como ruído.
- **PSM 4 (coluna única de texto variável)** e **PSM 6 (bloco uniforme)**: pioraram — passaram a intercalar trechos da tabela de rating com o texto corrido da coluna ao lado, na mesma linha, tornando o resultado mais confuso que o PSM padrão.
- **PSM 11 (texto esparso)**: pior ainda — introduziu linhas de ruído puro (sequências de pontos) e também misturou as colunas.
- **Conclusão do teste de PSM**: pra esta página específica (duas colunas: tabela pequena + texto corrido ao lado), o PSM automático padrão do Tesseract já é a melhor opção das quatro testadas. Não há necessidade de forçar um PSM alternativo neste caso — a variação vale a pena testar caso a caso, mas não deve ser assumida como melhoria automática.

## Decisões técnicas tomadas
- **Renderização a 300 DPI, diferente da Ordem 03** — seguindo a instrução explícita da Ordem 05, pra garantir comparação justa entre os dois motores nesta sessão. Isso também explica por que os tempos do rapidocr aqui (36,8–79,1s) são maiores que os registrados na Ordem 03 (7,9–59,6s) para as mesmas páginas: a imagem de entrada é maior (300 DPI vs. ~144 DPI antes), não é uma regressão de desempenho do motor.
- **Medição quantitativa (contagem de acentos e tokens longos)** feita além do que a ordem pedia estritamente (que pedia avaliação sim/não/parcial) — decisão de adicionar evidência numérica reproduzível pra não depender só de leitura visual subjetiva na hora de comparar os dois motores.

## Testes realizados
- Ver seção "Comparação objetiva" acima — cobre os itens 1–4 do critério de pronto da ordem.
- **Não testado**: OCR de outras páginas do livro além das 3 já usadas na Ordem 03 (fora de escopo, conforme a própria ordem) e qualquer motor de OCR além dos dois pedidos (Tesseract, rapidocr-onnxruntime).

## Pendências / próximos passos
- Nenhuma mudança de código foi feita — a decisão de integrar (ou não) OCR ao pipeline continua pendente, agora com evidência concreta pra embasar a escolha.
- Se o arquiteto decidir seguir com OCR, `Tesseract` é a recomendação técnica desta sessão (ver "Contexto pro arquiteto"), o que muda o levantamento de custo/risco da Ordem 03 (que tinha avaliado só o rapidocr): passa a exigir um binário de sistema instalado (já presente nesta máquina, mas seria uma dependência a documentar/instalar em qualquer outra máquina que rode o pipeline), não só uma dependência pip.
- Nenhuma `ORDEM-06` foi criada nesta sessão.

## Contexto pro arquiteto
- **Recomendação explícita**: **Tesseract tem qualidade sensivelmente melhor** que `rapidocr-onnxruntime` nos três problemas identificados na Ordem 03 — preserva acentuação (quase perfeita nas amostras), preserva espaçamento entre palavras (nenhuma concatenação nas amostras, contra 74 ocorrências no rapidocr), e é **~8 a 17× mais rápido** nesta máquina (4-5s/página vs. 37-79s/página a 300 DPI). Nenhum dos dois resolve completamente o problema de layout de tabela/coluna múltipla, mas o Tesseract com PSM automático pelo menos separa a tabela do texto corrido, enquanto o rapidocr mistura tudo.
- **Trade-off a decidir**: o Tesseract não é `pip install`-able — precisa do binário instalado no sistema (`C:\Program Files\Tesseract-OCR` nesta máquina). Isso é aceitável pra uso pessoal numa máquina só, mas é uma dependência de instalação manual a mais se o pipeline algum dia rodar em Docker/VPS (a imagem Docker atual não tem Tesseract — precisaria adicionar ao `Dockerfile` via `apt-get install tesseract-ocr tesseract-ocr-por`).
- **Extrapolando o tempo pro livro inteiro** (418 páginas, ~4,5s/página em média nesta amostra): Tesseract processaria o livro completo em **~30 minutos**, contra as ~3 horas estimadas pro rapidocr na Ordem 03 — uma diferença prática enorme pra viabilidade de uso real.
- Com essa evidência, a opção 2 da Ordem 03 ("adicionar OCR local opcional") fica mais atraente com Tesseract do que parecia com rapidocr — mas a decisão de implementar (e como: síncrono no `watch.py`, job separado, etc.) continua em aberto, a cargo do arquiteto/usuário.
