# Changelog — MarkItDown Web

> Índice rápido de reorientação. Se você (ou uma sessão nova, sem memória desta conversa) está retomando do zero, leia nesta ordem: **1) este arquivo → 2) `docs/instrucoes-projeto-markitdown-web.md` → 3) o `audit/*.md` mais recente listado abaixo → 4) `ordens/` pra ver o que ainda não rodou.** A página do Notion (link no fim) tem o mesmo conteúdo, pra quando as pastas locais não estiverem à mão.

## Estado agora (2026-09-04, fim de sessão de Claude Code)

- **Repositório**: https://github.com/paulo-pvbn/markitdown_web — fork publicado, commit `51e6546`, tag `v1.00`, mais commits das Ordens 02–12 em `main`.
- **Concluído e testado**: Ordens 01–12 (ver tabela abaixo). Interface manual + pipeline automático + manifesto + `.exe` empacotado + OCR em lote via Tesseract + purificação de conteúdo + ciclo de vida do `.exe` corrigido + UX de lote/pasta/progresso, todos funcionando.
- **Marco**: o livro-piloto da Ordem 03 (`733086206-Mercado-Financeiro-13ed.pdf`, 418 páginas escaneadas) foi processado por inteiro via `ocr_batch.py` (Ordem 07) e depois purificado (Ordem 10) — `.md` pronto (com `ocr_revisar: true`, recomenda revisão humana antes do upload) pra alimentar o Claude Project "InvestBot" quando o Paulo for criá-lo.
- **Achado recorrente resolvido**: instância antiga do `.exe` ficando esquecida em background e interferindo em testes (Ordens 08 e 09) — resolvido na raiz pela Ordem 11 (a instância nova sempre encerra a anterior automaticamente, mais um botão "Sair" real na interface).
- **Nenhuma Ordem pendente de execução no momento.** Pendências restantes são de decisão (Docker, Tailscale) ou de acompanhamento manual do Paulo: testar o `.exe`/`iniciar.bat` por duplo clique/execução real (não só via automação, como o Claude Code fez até aqui), revisar o material OCR+purificado do InvestBot antes do upload no Claude Project, e estar ciente de que a camada de purificação pode remover por engano siglas/termos técnicos reais de uma palavra só (ex.: Susep, BNDES) — risco aceito conscientemente na Ordem 10.

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
| 09 | Sinalizou PDF escaneado na interface manual (`ocr_pendente`) em vez de sucesso silencioso com `.md` vazio — mesma detecção da Ordem 07, agora em `/convert`/`/convert-zip` | ✅ Concluída | `audit/2026-09-04-ORDEM-09-sinalizar-ocr-interface-manual.md` |
| 10 | Purificação de boilerplate/lixo de OCR (`purify.py`) — achado crítico de falso positivo (1283 linhas removidas por engano na 1ª tentativa), resolvido parcialmente com aprovação do usuário para aceitar risco residual | ✅ Concluída (falso positivo residual aceito) | `audit/2026-09-04-ORDEM-10-purificar-conteudo.md` |
| 11 | Ciclo de vida do `.exe`: encerra instância antiga automaticamente + botão "Sair" real na interface — resolve achado recorrente das Ordens 08/09 | ✅ Concluída | `audit/2026-09-04-ORDEM-11-lifecycle-exe.md` |
| 12 | UX da interface manual: `iniciar.bat` (alternativa ao `.exe`), contador de caracteres/tokens, seleção de pasta, progresso em lote | ✅ Concluída | `audit/2026-09-04-ORDEM-12-ux-interface-manual.md` |

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
- Purificação de conteúdo (`purify.py`) roda automaticamente em toda conversão (Ordem 10) — boilerplate por regex (zero falso positivo observado) + lixo de OCR por dicionário pt+en (falso positivo residual aceito: siglas/termos técnicos reais de 1 palavra podem sumir, ex. Susep/BNDES/CNPC).
- `.exe`: só uma instância viva por vez, sempre — a mais nova encerra automaticamente qualquer anterior (Ordem 11, lock file com PID). Botão "Sair" na interface encerra de verdade, sem precisar do Gerenciador de Tarefas.
- `iniciar.bat` é uma alternativa ao `.exe` pra quem já tem Python — mesmo `launcher.py`, sem precisar baixar o binário de 82MB.

## Link permanente

Status completo e narrativo (mesmo conteúdo, outra forma): [MarkItDown Web — Status Atual e Backup Técnico](https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72) (Notion).
