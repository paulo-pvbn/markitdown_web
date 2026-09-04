## Ordem 12: Melhorias de UX na interface manual (lote, pasta, progresso, estatísticas)

- **Depende de**: nenhuma (independente das Ordens 10/11)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-04): adicionar launcher `.bat` complementar ao `.exe`, contador de caracteres/tokens, seleção de pasta inteira via `webkitdirectory`, e indicador simples de progresso "convertendo N de M".

## Objetivo

Quatro melhorias pequenas e independentes na interface manual, inspiradas numa comparação com um projeto de terceiro revisado em chat: (1) launcher `.bat` como alternativa mais leve ao `.exe` pra quem já tem Python; (2) contagem de caracteres/tokens (estimado) por arquivo convertido; (3) opção de selecionar uma pasta inteira, não só arquivos individuais; (4) progresso "convertendo N de M" ao converter vários arquivos.

## Contrato de dados

1. **`webapp/iniciar.bat`**: novo arquivo, mesmo padrão do `.bat` de referência mostrado em chat — checa `python` no PATH, checa se `flask`/`markitdown` importam, instala `requirements.txt` se faltar, roda `python launcher.py` (não `serve_network.py`, que não existe aqui — reaproveita o launcher já existente das Ordens 06/11).
2. **Contador de tokens**: estimativa simples (`caracteres / 4`, arredondado), sem nova dependência de tokenizer real — é só indicativo. Mostrar caracteres (exato) e tokens (estimado, rotulado como "~") por resultado, e um total quando houver mais de um arquivo.
3. **Seleção de pasta**: novo botão "Selecionar pasta" ao lado do dropzone existente, usando `<input type="file" webkitdirectory multiple>`. Arquivos entram no mesmo array/fluxo já existente (`addFiles()`), sem endpoint novo.
4. **Progresso em lote**: ao converter múltiplos arquivos, o frontend chama `/convert` **um arquivo por vez em sequência** (não em paralelo, não via streaming/SSE) e atualiza o texto de status entre cada chamada ("Convertendo 3 de 10..."). Simplicidade deliberada — nada de infraestrutura de progresso no backend.

## Casos de borda que o executor deve tratar

- `.bat`: testar com Python ausente do PATH (mensagem clara, não trava) e com dependências já instaladas (não tenta reinstalar à toa).
- Contador de tokens: deixar claro na interface que é estimativa (rótulo com `~` ou texto "aprox."), pra não parecer uma contagem exata de tokens de verdade.
- Seleção de pasta: testar que arquivos de subpastas (aninhados) também entram na lista — `webkitdirectory` inclui recursivamente.
- Progresso em lote: se um arquivo no meio do lote falhar, seguir convertendo os seguintes (mesma tolerância a erro que `/convert-zip` já tem) — não abortar o lote inteiro por causa de um arquivo com problema.
- Conversão de 1 único arquivo: não precisa mostrar "Convertendo 1 de 1" redundante — pode pular o indicador de progresso nesse caso.

## Fora de escopo (explicitamente)

- Não implementar progresso via streaming/SSE/WebSocket — sequência simples de requisições basta.
- Não usar tokenizer real (ex.: `tiktoken`) — estimativa por caractere é suficiente pro propósito (informativo, não preciso).
- Não adicionar "dividir markdown existente" nem redesenho visual/branding — decidido em chat que não vale a pena agora.
- Não criar `ORDEM-13` nesta sessão.

## Referência visual/técnica

- `iniciar-rede.bat` de um projeto de terceiro, colado em chat — padrão de verificação de Python/dependências a seguir (adaptado: roda `launcher.py`, não `serve_network.py`).
- Screenshot em chat do "MarkItDown Studio" — referência de conceito pros contadores de caracteres/tokens (não copiar o styling deles, só o conceito).

## Critério de pronto

1. `webapp/iniciar.bat` funcional — testado com e sem dependências pré-instaladas.
2. Caracteres e tokens (estimados) exibidos por resultado e em total, com estimativa claramente rotulada como aproximada.
3. Botão "Selecionar pasta" funcional, incluindo arquivos de subpastas.
4. Progresso "Convertendo N de M" visível durante conversão de múltiplos arquivos, com tolerância a falha individual mantida.
5. `.exe` reconstruído com as mudanças relevantes.
6. Relatório de auditoria em `audit/`.
