## Ordem 09: Sinalizar PDF escaneado na interface manual (evitar saída vazia silenciosa)

- **Depende de**: Ordem 07 (lógica de detecção original), Ordem 08 (mesma sessão de correção, mesmas rotas)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — mesma decisão da Ordem 07 (OCR nunca síncrono numa requisição), aplicada agora também à interface manual: detectar e avisar, nunca rodar Tesseract dentro do `/convert`.

## Objetivo

A interface manual (`/convert`, `/convert-zip`, incluindo dentro do `.exe`) hoje reproduz o mesmo problema que a Ordem 03 encontrou no pipeline automático: um PDF escaneado sem texto embutido converte "com sucesso" mas devolve conteúdo vazio, sem nenhum aviso — confirmado pelo Paulo testando o `.exe` com o livro do InvestBot (não travou, gerou `.md` de 0 KB). A Ordem 07 já resolveu isso pro `watch.py`, mas nunca tocou `app.py`. Esta ordem estende a mesma detecção — não a mesma solução, continua sem OCR síncrono — pra `/convert` e `/convert-zip`.

## Contrato de dados

- `app.py`: aplicar a mesma condição de detecção já usada em `watch.py` (`OCR_EMPTY_THRESHOLD`, PDF com corpo convertido abaixo de 50 caracteres) dentro de `_convert_one()`.
- Resposta de `/convert` pra um arquivo nessa condição: em vez de `{"ok": true, "markdown": ""}`, retornar algo que deixe claro que precisa de OCR — ex.: `{"ok": false, "ocr_pendente": true, "error": "PDF parece ser escaneado (sem texto embutido). Rode ocr_batch.py nesta pasta pra extrair via OCR local."}`.
- `/convert-zip`: no mesmo caso, escrever `<nome>_PRECISA_OCR.txt` no lugar do `.md` vazio, com a mesma mensagem.
- `static/index.html`: resultado com `ocr_pendente: true` deve aparecer de forma distinguível pro usuário — não pode parecer uma conversão normal bem-sucedida.

## Casos de borda que o executor deve tratar

- Aplicar em ambas as rotas (`/convert` e `/convert-zip`), mesmo padrão da Ordem 08.
- Não confundir "PDF vazio por ser realmente um arquivo vazio/corrompido" com "PDF escaneado" — a mensagem deve deixar claro que é uma hipótese razoável (texto não encontrado), não um diagnóstico certo.
- Testar exatamente com o caso real que revelou o problema: o livro do InvestBot (ou, se mais rápido, um PDF escaneado sintético de 1 página) arrastado na interface do `.exe`.
- Depois de corrigir, reconstruir o `.exe` (mesmo processo já validado nas Ordens 06/08) e confirmar o comportamento dentro do binário, não só via `python app.py`.

## Fora de escopo (explicitamente)

- Não rodar Tesseract dentro de `/convert`/`/convert-zip` — decisão já tomada (OCR é sempre em lote, `ocr_batch.py`, nunca síncrono numa requisição HTTP). Esta ordem é só sobre avisar corretamente, não sobre resolver o OCR ali.
- Não mudar nada em `watch.py`/`ocr_batch.py` — já corretos desde a Ordem 07.
- Não implementar detecção de scan parcial — mesma limitação já registrada, continua fora de escopo.
- Não criar `ORDEM-10` nesta sessão.

## Referência visual/técnica

- `webapp/watch.py` — `OCR_EMPTY_THRESHOLD`, lógica de detecção já validada, reaproveitar a mesma condição.
- Relato do Paulo em chat: livro do InvestBot convertido pelo `.exe`/navegador, sem erro, mas `.md` de 0 KB.

## Critério de pronto

1. `/convert` com um PDF escaneado retorna resposta que deixa claro que precisa de OCR, não um "sucesso" com conteúdo vazio.
2. `/convert-zip` no mesmo caso gera `<nome>_PRECISA_OCR.txt` em vez de um `.md` vazio.
3. Frontend mostra isso de forma distinguível de uma conversão normal bem-sucedida.
4. Testado com o livro real do InvestBot (ou fixture equivalente) pelo `.exe` reconstruído, não só em desenvolvimento.
5. Relatório de auditoria em `audit/`.
