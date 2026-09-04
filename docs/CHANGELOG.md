# Changelog — MarkItDown Web

> Índice rápido de reorientação. Se você (ou uma sessão nova, sem memória desta conversa) está retomando do zero, leia nesta ordem: **1) este arquivo → 2) `docs/instrucoes-projeto-markitdown-web.md` → 3) o `audit/*.md` mais recente listado abaixo → 4) `ordens/` pra ver o que ainda não rodou.** A página do Notion (link no fim) tem o mesmo conteúdo, pra quando as pastas locais não estiverem à mão.

## Estado agora (2026-09-04, fim de sessão de Claude Code)

- **Repositório**: https://github.com/paulo-pvbn/markitdown_web — fork publicado, commit `51e6546`, tag `v1.00`, mais commits das Ordens 02–08 em `main`.
- **Concluído e testado**: Ordens 01–08 (ver tabela abaixo). Interface manual + pipeline automático + manifesto + `.exe` empacotado + OCR em lote via Tesseract + limite de upload corrigido, todos funcionando.
- **Marco**: o livro-piloto da Ordem 03 (`733086206-Mercado-Financeiro-13ed.pdf`, 418 páginas escaneadas) foi processado por inteiro via `ocr_batch.py` na Ordem 07 — `.md` pronto (com `ocr_revisar: true`, recomenda revisão humana antes do upload) pra alimentar o Claude Project "InvestBot" quando o Paulo for criá-lo.
- **Nenhuma Ordem pendente de execução no momento.** Pendências restantes são de decisão (Docker, Tailscale) ou de acompanhamento manual do Paulo: testar o `.exe` por duplo clique real (não só execução programática, como os Claude Code fizeram até aqui), e revisar o material OCR do InvestBot antes do upload no Claude Project.

## Histórico de Ordens

| Ordem | O que fez | Status | Relatório |
|---|---|---|---|
| 01 | Bootstrap: estrutura de pastas, arquivos da webapp no fork, commit + tag v1.00 | ✅ Concluída | `audit/2026-09-03-ORDEM-01-bootstrap-markitdown-web.md` |
| 02 | Validou `/convert-zip` e `watch.py` (sem Docker, via venv) | ✅ Concluída | `audit/2026-09-03-ORDEM-02-validar-convertzip-watch.md` |
| 03 | Piloto com material real — revelou PDF escaneado sem texto (gap de cobertura) | ✅ Concluída (achado documentado, não resolvido) | `audit/2026-09-03-ORDEM-03-piloto-real-claude-project.md` |
| 04 | Generalizou o pipeline (framing "qualquer app de IA") + `_manifest.json` por pasta | ✅ Concluída | `audit/2026-09-03-ORDEM-04-generalizar-pipeline.md` |
| 05 | Comparou Tesseract vs. rapidocr — Tesseract venceu com folga (8–17× mais rápido, qualidade muito melhor) | ✅ Concluída (investigação, recomendação registrada) | `audit/2026-09-03-ORDEM-05-comparar-ocr-tesseract-rapidocr.md` |
| 06 | Empacotou interface manual como `.exe` (72MB, sem terminal, testado com conversão real dentro do binário) | ✅ Concluída (pendente: teste por duplo clique humano) | `audit/2026-09-03-ORDEM-06-empacotar-exe.md` |
| 07 | Implementou OCR via Tesseract em lote (`ocr_batch.py`) + sinalização `ocr_pendente` no `watch.py`; rodou o livro-piloto inteiro (418 páginas, ~27min) | ✅ Concluída (pendente: revisão humana do resultado) | `audit/2026-09-03-ORDEM-07-ocr-tesseract-lote.md` |
| 08 | Corrigiu limite de upload (413) e tratamento de erro em `/convert`/`/convert-zip` — duas causas encontradas (`MAX_CONTENT_LENGTH` antigo + `MAX_FORM_MEMORY_SIZE` do Werkzeug ≥3.1, não previsto no contrato original) | ✅ Concluída | `audit/2026-09-04-ORDEM-08-corrigir-limite-upload.md` |

## Decisões-chave já tomadas (não re-perguntar)

- Pular Docker por enquanto (venv resolve pros testes atuais).
- Tesseract, não rapidocr — implementado na Ordem 07 (`ocr_batch.py`).
- OCR roda como job em lote manual (`ocr_batch.py`), nunca síncrono no `watch.py` — o `watch.py` só sinaliza `ocr_pendente: true`.
- `ocr_pendente: true` é permanente no front matter (nunca removido) — permite reprocessamento seguro sem lógica extra de fila.
- `ocr_revisar: true` fica pra sempre no front matter de qualquer `.md` que passou por OCR — nunca removido automaticamente, mesmo Tesseract erra em tabela/coluna dupla.
- `.exe` na versão simples (abre navegador), não `pywebview` (janela nativa) — não proporcional pro ganho. Empacotado via PyInstaller `--onefile`, com `collect_data_files` pros modelos do `magika` (não caminho manual).
- Pipeline reposicionado como genérico ("qualquer app de IA"), não exclusivo a Claude Projects.
- Upload final pro Claude Project continua manual — sem API pública da Anthropic pra isso, e não vale o risco de segurança de soluções não-oficiais baseadas em sessão do navegador.
- Limite de upload da interface manual: 500MB por padrão (era 50MB), ajustável via `MAX_UPLOAD_MB`.

## Link permanente

Status completo e narrativo (mesmo conteúdo, outra forma): [MarkItDown Web — Status Atual e Backup Técnico](https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72) (Notion).
