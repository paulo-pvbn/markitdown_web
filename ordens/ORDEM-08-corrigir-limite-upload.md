## Ordem 08: Corrigir limite de upload e tratamento de erro no `/convert`

- **Depende de**: Ordem 06 (empacotamento `.exe`, onde o bug foi encontrado)
- **Bloqueia**: uso pleno da interface manual pra arquivos grandes (>50MB)
- **Decisão de produto já confirmada?**: parcialmente — está claro que o limite de 50MB é baixo demais e que o erro precisa ficar legível; o valor exato do novo limite fica a critério do executor dentro de uma faixa generosa, já que é uso pessoal/local, não exposto publicamente.

## Objetivo

Corrigir dois problemas relacionados, encontrados testando o `.exe` com um arquivo real de 66,4MB: (1) o limite de upload (`MAX_CONTENT_LENGTH`, hoje 50MB) é baixo demais pra documentos reais — o próprio arquivo de teste do projeto excede; (2) quando o limite é excedido (ou qualquer erro HTTP não-2xx acontece), o Flask devolve uma página HTML de erro em vez de JSON, e o frontend quebra tentando fazer `res.json()` nela, mostrando "Unexpected token '<'... is not valid JSON" em vez de dizer o que realmente aconteceu.

## Contrato de dados

- `app.py`: `MAX_UPLOAD_MB` sobe de 50 pra um valor generoso (sugestão: 500, ou tornar configurável via env var `MAX_UPLOAD_MB`, seguindo o mesmo padrão já usado pra `HOST`/`PORT`).
- `app.py`: adicionar `@app.errorhandler(413)` retornando JSON (`{"error": "Arquivo muito grande. Limite atual: X MB."}`) em vez de deixar o Flask devolver a página HTML padrão.
- `static/index.html`: antes de chamar `res.json()`, checar `res.ok`; se a resposta não for OK, tentar ler como JSON e, se falhar (não é JSON), mostrar uma mensagem genérica clara em vez do erro de parsing cru (ex.: "O servidor respondeu com erro inesperado (HTTP {status})").

## Casos de borda que o executor deve tratar

- Aplicar a mesma correção (413 e resposta não-JSON) tanto em `/convert` quanto em `/convert-zip` — os dois têm a mesma estrutura de upload e o mesmo risco.
- Testar com o mesmo arquivo real que revelou o bug (66,4MB) pra confirmar que agora converte com sucesso dentro do novo limite.
- Testar também o caminho de erro de propósito (ex.: configurar um limite bem baixo temporariamente, tipo 1MB, mandar um arquivo maior, confirmar que a mensagem de erro agora é legível) — não basta só aumentar o limite e nunca mais ver o erro; o tratamento em si precisa ser validado.
- Depois de corrigir, gerar o `.exe` de novo (Ordem 06 já validou o processo de build) e testar a conversão do arquivo de 66,4MB dentro do `.exe` atualizado, não só via `python app.py`.

## Fora de escopo (explicitamente)

- Não mudar a lógica de conversão em si (`markitdown`, `magika`) — o problema é só limite de tamanho + tratamento de erro HTTP.
- Não implementar upload em chunks/streaming pra arquivos ainda maiores — fora de propósito pro volume de uso atual.
- Não criar `ORDEM-09` nesta sessão.

## Referência visual/técnica

- Erro reportado em chat: arquivo de 66,4MB (`733086206-Mercado-Financeiro-13ed.pdf`), mensagem "Unexpected token '<', "<!doctype "... is not valid JSON".
- `webapp/app.py` — `MAX_CONTENT_LENGTH` atual (50MB), definido perto do topo do arquivo.
- `webapp/static/index.html` — função que faz `fetch('/convert', ...)` e `await res.json()`.

## Critério de pronto

1. Limite de upload aumentado (valor generoso ou configurável via env var).
2. `@app.errorhandler(413)` retornando JSON em `/convert` e `/convert-zip`.
3. Frontend não quebra mais com erro de parsing cru quando a resposta não é JSON — mostra mensagem clara baseada no status HTTP.
4. Arquivo real de 66,4MB convertido com sucesso via `/convert`, testado dentro do `.exe` reconstruído.
5. Caso de erro testado de propósito (limite baixo temporário) confirmando mensagem legível.
6. Relatório de auditoria em `audit/`.
