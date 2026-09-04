## Ordem 07: OCR local via Tesseract, como job em lote separado

- **Depende de**: Ordem 05 (comparação já confirmou Tesseract como motor)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-03): implementar Tesseract, como job em lote, não síncrono no `watch.py` em tempo real.

## Objetivo

Adicionar suporte a OCR local (Tesseract) para PDFs escaneados, mantendo a separação já decidida: o `watch.py` continua rápido e nunca bloqueia esperando OCR — só detecta e sinaliza quando um PDF precisa de OCR. Um script separado, rodado manualmente quando o usuário quiser, faz o OCR de fato e substitui o conteúdo vazio pelo texto reconhecido, sempre marcado como "revisar" no front matter.

## Contrato de dados

- Sem mudança de front matter quando a conversão normal já extrai texto.
- Quando o `watch.py` detecta corpo vazio (ou quase) num PDF, grava o `.md` normalmente, mas acrescenta `ocr_pendente: true` ao front matter.
- Depois que `webapp/ocr_batch.py` processa um arquivo, o front matter passa a ter `ocr: true`, `ocr_engine: tesseract`, `ocr_revisar: true` — este último nunca é removido automaticamente; a Ordem 05 mostrou que layout de tabela continua imperfeito mesmo com o melhor motor testado, então revisão humana continua recomendada mesmo depois do OCR.
- `requirements.txt`: adicionar `pytesseract` e `pypdfium2` (já usados nas provas de conceito das Ordens 03/05). Tesseract em si continua sendo dependência de sistema, não pip — documentar no `README.md` como pré-requisito opcional.

## Casos de borda que o executor deve tratar

- Detecção de "precisa de OCR": corpo do markdown vazio ou abaixo de um limite pequeno (ex.: <50 caracteres) para arquivos PDF. Não tentar detectar scan parcial (algumas páginas com texto, outras não) nesta ordem — documentar como limitação conhecida se aparecer.
- `webapp/ocr_batch.py` deve mostrar progresso (página N de M) — um livro de ~400 páginas leva ~30 minutos; silêncio total nesse tempo é ruim.
- Se o Tesseract não estiver instalado/no PATH quando `ocr_batch.py` rodar, falhar com mensagem clara apontando o pré-requisito — não travar sem explicação.
- Reprocessar um arquivo que já passou por OCR deve ser seguro — pode simplesmente refazer o OCR e sobrescrever (idempotente); o custo de detectar "já foi feito" com segurança não compensa pra este volume de uso.
- Atualizar o `_manifest.json` (Ordem 04) da subpasta depois do OCR — o campo `caracteres` precisa refletir o novo conteúdo, não ficar com o valor zerado antigo.

## Fora de escopo (explicitamente)

- Não integrar OCR ao fluxo síncrono do `watch.py` — decisão já tomada, `watch.py` só detecta e sinaliza.
- Não implementar detecção de scan parcial (mistura de páginas com/sem texto).
- Não adicionar Tesseract ao `Dockerfile`/Docker nesta ordem — Docker segue como decisão em aberto separada.
- Não construir interface web pra disparar o OCR — fica CLI mesmo (`python ocr_batch.py <pasta>`).
- Não criar `ORDEM-08` nesta sessão.

## Referência visual/técnica

- `audit/2026-09-03-ORDEM-05-comparar-ocr-tesseract-rapidocr.md` — configuração validada: `por+eng`, PSM automático (não forçar PSM alternativo — a Ordem 05 já testou e o padrão venceu), 300 DPI.
- `webapp/watch.py` — `_wait_until_stable`, front matter existente, convenção de manifesto (Ordem 04) — seguir os mesmos padrões já estabelecidos.

## Critério de pronto

1. `watch.py` sinaliza `ocr_pendente: true` no front matter quando um PDF gera corpo vazio/quase vazio, sem mudar o tempo de resposta do pipeline em tempo real.
2. `webapp/ocr_batch.py` roda via CLI, recebe uma pasta (ex.: `raw/InvestBot/`), localiza os `.md` com `ocr_pendente: true` na subpasta `converted/` correspondente, faz OCR (Tesseract, `por+eng`, PSM automático, 300 DPI) do PDF de origem, e substitui o conteúdo do `.md` com front matter atualizado.
3. Testado com o mesmo livro real da Ordem 03/05 (`733086206-Mercado-Financeiro-13ed.pdf`) — pelo menos as páginas já usadas como amostra (ou o livro inteiro, se o tempo permitir) confirmadas com texto legível no `.md` resultante.
4. `_manifest.json` da subpasta atualizado após o OCR, refletindo o novo tamanho de conteúdo.
5. `webapp/README.md` documenta o Tesseract como pré-requisito opcional e como rodar `ocr_batch.py`.
6. Relatório de auditoria em `audit/`.
