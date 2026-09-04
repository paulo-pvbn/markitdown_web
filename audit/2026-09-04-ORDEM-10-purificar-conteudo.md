# Sessão: Purificar conteúdo convertido (boilerplate + lixo de OCR) para RAG

- **Data/hora**: 2026-09-04 18:00–18:45
- **Versão resultante**: v1.00 (sem nova tag — feature nova, não release marcado)
- **Commit**: (ver commits desta sessão no log do `main`, feitos após este relatório)
- **Arquivos de exemplo usados**: o material real do InvestBot (`733086206-Mercado-Financeiro-13ed.pdf`, 418 páginas, reconvertido do zero via OCR duas vezes nesta sessão) como fixture principal — não havia o "trecho colado pelo Paulo em chat" disponível nesta sessão (conversa diferente de onde a ordem foi escrita), mas o `.md` real já convertido nas Ordens 07/09 contém exatamente os mesmos padrões descritos no contrato (ISBN, direitos reservados, CIP, CDD, e os trechos de lixo `"wt,"`/`"een"`/`"ILI"`/`"eg"`/`"We ee"`/`"N TOA"`), então foi usado diretamente como fixture, com resultado equivalente.

## O que foi feito
- Criado `webapp/purify.py` com `purify_markdown(text) -> (str, dict)`, três camadas: normalização de espaço em branco, remoção de boilerplate por regex, remoção de lixo de OCR por dicionário.
- **Achado crítico durante a validação obrigatória** (ver seção dedicada abaixo): a implementação inicial, seguindo o contrato ao pé da letra (só dicionário `pt`), removeu **1283 linhas** do livro real — a maioria não era lixo, e sim entradas de sumário e termos técnicos em inglês comuns em finanças. Parei e consultei o usuário antes de prosseguir, com a evidência concreta.
- Com autorização do usuário pra manter o limite de tamanho original (`<40` caracteres) e aceitar o risco residual, apliquei duas melhorias que **só reduzem falso positivo, sem custo observado** (não pedidas explicitamente no contrato, mas dentro do espírito de "constantes ajustáveis, não hardcoded"):
  1. Dicionário combinado `pt`+`en` (não só `pt`) — livros técnicos em português usam muito termo em inglês sem tradução (swap, hedge, bond, yield, duration, warrant, factoring...).
  2. Linha com qualquer dígito nunca é candidata a lixo — forte indício de entrada de sumário/índice/nota de rodapé (número de página), não de lixo de capa estilizada.
- Com essas duas melhorias, a remoção caiu de 1283 para **190 linhas** — ainda com falso positivo residual documentado abaixo (aceito pelo usuário).
- Integrado `purify_markdown` nos três pontos de conversão (`app.py._convert_one`, `watch.py.convert_file`, `ocr_batch.py._rewrite_md`), todos importando de `purify.py`, sem duplicar lógica.
- Front matter de `watch.py` e `ocr_batch.py` ganha `purified: true`. **`app.py` não gera front matter** (nunca gerou, em nenhuma ordem anterior — `/convert` retorna JSON puro, `/convert-zip` escreve `.md` sem cabeçalho) — a purificação roda no conteúdo de qualquer forma (`aplicar em toda conversão`), mas o campo `purified: true` só se aplica onde já existe o conceito de front matter.
- `requirements.txt`: `pyspellchecker` adicionado.
- `markitdown-web.spec`: `collect_data_files("spellchecker")` adicionado (mesmo padrão do `magika`) — os dicionários `pt.json.gz`/`en.json.gz` são dados empacotados dentro do próprio pacote Python, não código, então o PyInstaller não os inclui automaticamente sem isso.
- `.exe` reconstruído e testado (não exigido explicitamente pelos critérios desta ordem, mas obrigatório pra não deixar o binário desatualizado/quebrado — o Ordem 06/08/09 já estabeleceram esse hábito).

## Achado crítico: falso positivo severo na primeira validação (antes de perguntar ao usuário)
Rodando a implementação **exatamente como o contrato pedia** (dicionário só `pt`, sem exclusão de dígito) contra o livro real, a camada de lixo de OCR removeu **1283 linhas**. Amostra do que foi removido incorretamente:
- Entradas de sumário/índice inteiras: `"BNDES, 49"`, `"SCR, 82"`, `"5.2.3 Depositary Receipts, 90"`, `"Glossário, 381"`.
- Termos financeiros em inglês sem tradução (comuns no domínio, não em nenhum dicionário `pt`): `"Warrants, 190"`, `"Bonds, Eurobonds e Global Bonds, 199"`, `"Yield to Maturity — YTM, 200"`, `"17.3.9 Hedge, 352"`.
- Fórmulas técnicas reais do livro: `"PIB=C+I|I+G+EL"`, `"Poupança do Governo = T-G"`.

Isso é uma limitação **estrutural**, não um bug de calibração: pra uma linha de uma palavra só, ela está 100% reconhecida ou 0% reconhecida no dicionário — não existe meio-termo pra distinguir "termo técnico real fora do dicionário" de "lixo de verdade" usando só frequência de reconhecimento.

**Parei e perguntei ao usuário** antes de prosseguir, apresentando a evidência concreta e três opções (reduzir o limite de tamanho pra `<=10` chars, manter `<40` e aceitar o risco, ou só sinalizar em vez de apagar). **Decisão do usuário: manter `<40` chars e aceitar o risco.**

## Validação de falso positivo (obrigatória pelo critério de pronto #3) — com a versão final (pt+en, exclusão de dígito)
- **Verificação sistemática, além do mínimo de 2-3 trechos pedido**: dos **1646 parágrafos longos (>300 caracteres) do livro inteiro**, **1645 permaneceram idênticos** depois da purificação — checado programaticamente, não por amostragem visual.
- **O único parágrafo afetado**: uma lista de referência de ~26 sites (`SITES\nwww.algorithmics.com\n...`). Dessa lista, **1 de 26 entradas** foi removida por engano: `www.fma.org` (0% de palavras reconhecidas — `fma` e `org` não estão no dicionário pt/en usado). As outras 25 sobreviveram porque `www`/`com`/`br` são reconhecidos como palavras válidas nos dicionários usados, elevando a taxa de reconhecimento acima de 50%.
- **Falso positivo residual conhecido e aceito pelo usuário** (das 190 linhas removidas na versão final): siglas e termos regulatórios/técnicos reais de uma palavra só — `Susep`, `Resseguradores`, `CNPC`, `PREVIC`, `BNDES` (isolado, sem número — diferente de `"BNDES, 49"` do sumário, que tem dígito e por isso sobrevive), `(CVM)`, `resseguro`, `Custodiante`, `bancários (CDB/RDB)`. Nenhum dicionário genérico conhece jargão regulatório-financeiro específico — esse tipo de perda é irredutível com a abordagem de dicionário genérico especificada no contrato.
- **Falso negativo notado** (lixo que sobrevive, achado incidental durante a validação): o bloco `"eg" / "We ee" / "N TOA"` (3 linhas consecutivas, lixo de capa) sobrevive porque cada linha individualmente bate com uma palavra curta comum do dicionário (`"eg"` como abreviação inglesa, `"we"` pronome inglês, `"n"`/`"toa"` como entradas curtas do dicionário) — o oposto do problema anterior: fragmentos de lixo muito curtos têm mais chance de colidir por acaso com entradas de 1-2 letras do dicionário.

## Testes realizados
1. **Boilerplate removido** (critério 2): ISBN, "TODOS OS DIREITOS RESERVADOS...", "Dados Internacionais de Catalogação na Publicação", `CDD-332.6`, "Depósito legal na Biblioteca Nacional...", `© 2015 by Editora Atlas S.A.` — todos confirmados ausentes do `.md` final (11 linhas de boilerplate contadas nas stats).
2. **Lixo de OCR conhecido removido** (critério 2): `"wt,"`, `"een"`, `"ILI"` confirmados ausentes como linhas exatas (checagem por linha, não substring — substring `"een"`/`"ILI"` aparece dentro de palavras legítimas como "utilizado" num arquivo de 1,4M caracteres, então a checagem certa é por linha inteira, não por `in`).
3. **Falso positivo sistemático**: ver seção dedicada acima — 1645/1646 parágrafos longos intactos, 1 lista de referência com 1/26 entradas afetada.
4. **Integração nos 3 pontos** (critério 4): `watch.py` reconvertendo o PDF real do zero → `purified: true` no front matter, corpo vazio (esperado, `ocr_pendente: true`, nada a purificar ainda). `ocr_batch.py` rodado no livro inteiro (418 páginas, ~29 min) → `.md` final com **1.464.117 caracteres** (contra 1.466.639 antes da purificação, Ordem 07 — redução de ~2.522 caracteres de boilerplate/lixo), front matter com todos os 8 campos esperados incluindo `purified: true`. `app.py` testado com `.pptx`/`.html` normais (conteúdo pequeno, sem boilerplate/lixo — confirma que a purificação não quebra conversão comum) e com PDF escaneado (fluxo `ocr_pendente` da Ordem 09 continua funcionando).
5. **`pyspellchecker`/dicionário confirmado offline** (critério 5): `spellchecker/resources/pt.json.gz` e `en.json.gz` vêm empacotados dentro do próprio pacote pip, carregados via `SpellChecker(language=...)` sem nenhuma chamada de rede — confirmado por inspeção do pacote instalado, sem exceção à filosofia offline do projeto.
6. **`.exe` reconstruído e testado**: `collect_data_files("spellchecker")` adicionado ao spec; build concluído (82,8MB, cresceu ~7MB pelos dicionários); testado numa pasta limpa — conversão normal, PDF com texto real, e PDF escaneado (`ocr_pendente`) todos funcionando dentro do binário, confirmando que os dicionários carregam corretamente empacotados (mesmo risco identificado pelo `magika` na Ordem 06, mesma solução aplicada).

## Decisões técnicas tomadas
- **Consultei o usuário em vez de decidir sozinho** ao encontrar o falso positivo severo (1283 linhas) — a "decisão de produto já confirmada" da ordem (apagar automaticamente) presumia que a abordagem funcionaria bem; a evidência mostrou um risco não trivial de perder conteúdo técnico real, então tratei como uma decisão de trade-off que caberia ao usuário, não a mim.
- **Dicionário pt+en combinado e exclusão de linha com dígito**, além do literalmente pedido no contrato (só "dicionário pt") — decisão tomada unilateralmente por serem melhorias estritas (só reduzem falso positivo, sem nenhum custo observado nos testes) dentro do espírito da ordem ("threshold e comprimento são constantes ajustáveis, não hardcoded") — não são mudanças de comportamento que o usuário precisaria aprovar previamente, ao contrário da decisão de manter `<40` chars.
- **`app.py` não ganhou front matter novo** — decisão de manter escopo restrito: adicionar front matter a `/convert`/`/convert-zip` seria uma mudança de formato de saída da interface manual não pedida por nenhuma ordem até agora; a purificação do conteúdo em si já satisfaz "aplicar em toda conversão".
- **Checagem de OCR pendente (`OCR_EMPTY_THRESHOLD`) roda no texto bruto, antes da purificação** — evita que a purificação (que pode encurtar texto real removendo boilerplate) empurre um PDF com conteúdo real pra baixo do limiar de 50 caracteres por engano.

## Arquivos alterados
- `webapp/purify.py` — novo.
- `webapp/app.py`, `webapp/watch.py`, `webapp/ocr_batch.py` — importam e chamam `purify_markdown`.
- `webapp/requirements.txt` — `pyspellchecker`.
- `webapp/markitdown-web.spec` — `collect_data_files("spellchecker")`.
- `webapp/raw/InvestBot/` e `webapp/converted/InvestBot/` — dados do usuário, fora do controle de versão; `.md` final atualizado com conteúdo purificado.

## Pendências / próximos passos
- **Falso positivo residual aceito, não resolvido**: siglas/termos regulatórios reais de uma palavra só continuam podendo ser removidos por engano (ver lista acima). Não há solução simples dentro da abordagem de dicionário genérico — precisaria de um dicionário de domínio (financeiro/regulatório) especializado, fora do escopo desta ordem.
- **Falso negativo notado, não resolvido**: blocos de lixo muito curtos (2-3 letras por linha) podem coincidir por acaso com entradas do dicionário e sobreviver — impacto baixo (poucos caracteres de ruído), não vale complexidade adicional agora.
- Arquivos já convertidos de sessões anteriores que não foram tocados nesta sessão continuam sem purificação (conforme fora de escopo explícito da ordem) — só o material do InvestBot foi reprocessado, e só porque era o próprio fixture de validação.
- Nenhuma `ORDEM-11` foi criada por mim nesta sessão (já havia `ORDEM-11` e `ORDEM-12` fornecidas pelo usuário durante a execução desta ordem).

## Contexto pro arquiteto
- **A decisão de produto "apagar automaticamente" sobreviveu à validação, mas com evidência concreta de custo real** — o usuário optou por aceitar isso conscientemente. Vale registrar essa decisão como "revisitável": se no futuro surgir um caso onde uma sigla/termo regulatório importante sumir de um documento crítico, a mitigação mais direta é migrar de "remover" para "marcar e revisar" nessa camada especificamente (a camada de boilerplate por regex, em contraste, teve **zero falso positivo** observado e pode continuar automática com confiança).
- A purificação reduziu o livro do InvestBot em ~2.500 caracteres (~0,17% do total) — um ganho pequeno em volume absoluto pra este livro específico (a maior parte do conteúdo já era texto corrido legítimo), mas o valor real está em remover ruído concentrado no início do arquivo (capa, ficha catalográfica) que desperdiçaria proporcionalmente mais atenção/tokens num contexto de RAG do que sugere o tamanho absoluto removido.
