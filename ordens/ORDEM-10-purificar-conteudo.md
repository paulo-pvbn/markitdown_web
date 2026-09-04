## Ordem 10: Purificar conteúdo convertido (boilerplate + lixo de OCR) para RAG

- **Depende de**: nenhuma diretamente, mas toca os três pontos de conversão já existentes (Ordens 01, 07)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-04): aplicar em toda conversão (OCR e normal), e apagar automaticamente lixo de OCR detectado (não só sinalizar para revisão).

## Objetivo

Reduzir ruído e consumo de tokens no material que alimenta RAG: remover boilerplate editorial formulaico (ISBN, direitos autorais, ficha catalográfica, depósito legal) e lixo de OCR (linhas curtas isoladas sem sentido, tipicamente de capas estilizadas), aplicado uniformemente nos três pontos de conversão do projeto (`app.py`, `watch.py`, `ocr_batch.py`).

## Contrato de dados

- Novo módulo `webapp/purify.py`, com função pública `purify_markdown(text: str) -> tuple[str, dict]` — retorna o texto purificado e um pequeno resumo do que foi removido (contagem de linhas de boilerplate removidas, contagem de linhas de lixo removidas), pra registrar em front matter.
- `purify.py` faz, nesta ordem:
  1. **Normalização de espaço em branco**: colapsar 3+ quebras de linha em 2, remover espaço à direita antes de quebra de linha, remover form feed.
  2. **Remoção de boilerplate por padrão de texto**: linhas/trechos batendo em ISBN, "TODOS OS DIREITOS RESERVADOS..." (até a próxima linha em branco), "Dados Internacionais de Catalogação na Publicação", código CDD/CDU, "Depósito legal na Biblioteca Nacional...", linha de copyright (`© AAAA by ...`).
  3. **Remoção de lixo de OCR**: candidatas são linhas **isoladas** (cercadas por linha em branco antes e depois) **e curtas** (< 40 caracteres). Entre essas candidatas, usar checagem de dicionário (`pyspellchecker`, dicionário `pt`) — linha é removida se menos de 50% das palavras forem reconhecidas. Threshold e comprimento são constantes ajustáveis no topo do módulo, não hardcoded no meio da lógica.
- `requirements.txt`: adicionar `pyspellchecker`.
- Front matter dos `.md` gerados ganha `purified: true` quando a purificação rodou (todos os casos, já que passa a ser padrão).

## Casos de borda que o executor deve tratar

- **Validação obrigatória contra o material real do InvestBot** (já convertido, com o boilerplate exato mostrado pelo Paulo em chat) — confirmar que ISBN/direitos-autorais/CIP somem e que as linhas de lixo (`"MERCADO\nAMAS,\nwt,\neen"`, `"eg\nWe ee\nN TOA"`, o "A" solto) somem.
- **Verificação obrigatória de falso positivo**: pegar pelo menos 2-3 trechos de conteúdo técnico real do mesmo livro (ex.: o trecho da página 51 já usado nas Ordens 05/07) e confirmar que **nada** de conteúdo real foi removido pela checagem de dicionário. Reportar explicitamente no relatório qualquer linha real removida por engano, mesmo que pareça pouco importante — o critério de pronto exige isso documentado, não só "pareceu ok".
- Aplicar a purificação nos três pontos (`app.py` em `_convert_one`, `watch.py` em `convert_file`, `ocr_batch.py`) sem duplicar a lógica — importar de `purify.py` nos três.
- Arquivos já convertidos (`.md` existentes de sessões anteriores) **não são reprocessados automaticamente** por esta ordem — só as novas conversões a partir de agora passam pela purificação. Reprocessar o material antigo (InvestBot) é opcional, à parte, se o Paulo quiser.
- `pyspellchecker` com dicionário `pt` precisa ser confirmado como funcional offline depois de instalado (alguns dicionários desse pacote baixam dados na primeira execução) — se precisar de download de internet na primeira vez, registrar isso claramente como exceção à filosofia "offline" do projeto, e verificar se dá pra empacotar o dicionário localmente em vez disso.

## Fora de escopo (explicitamente)

- Não tentar generalizar pra boilerplate de outras línguas além de português/inglês nesta ordem.
- Não tentar remover boilerplate de endereço/telefone de editora (formato varia demais pra regex confiável) — só os padrões universais listados no contrato de dados.
- Não reprocessar automaticamente arquivos já convertidos.
- Não criar `ORDEM-11` nesta sessão.

## Referência visual/técnica

- Trecho real colado pelo Paulo em chat (front matter + boilerplate + lixo de OCR do InvestBot) — usar como fixture de teste principal.
- `webapp/ocr_batch.py`, `webapp/watch.py`, `webapp/app.py` — pontos de integração.

## Critério de pronto

1. `webapp/purify.py` criado, com as 3 camadas (whitespace, boilerplate regex, lixo de OCR via dicionário).
2. Testado contra o trecho real do InvestBot: boilerplate conhecido removido, lixo de OCR conhecido removido.
3. Teste de falso positivo documentado: conteúdo técnico real do mesmo livro conferido, sem remoção indevida (ou, se houver, reportado explicitamente com o trecho exato).
4. Purificação integrada nos três pontos de conversão (`app.py`, `watch.py`, `ocr_batch.py`), front matter com `purified: true`.
5. `pyspellchecker`/dicionário `pt` confirmado funcionando offline (ou exceção documentada).
6. Relatório de auditoria em `audit/`.
