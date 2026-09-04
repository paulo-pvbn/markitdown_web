# Changelog — MarkItDown Web

> Índice rápido de reorientação. Se você (ou uma sessão nova, sem memória desta conversa) está retomando do zero, leia nesta ordem: **1) este arquivo → 2) `docs/instrucoes-projeto-markitdown-web.md` → 3) o `audit/*.md` mais recente listado abaixo → 4) `ordens/` pra ver o que ainda não rodou.** A página do Notion (link no fim) tem o mesmo conteúdo, pra quando as pastas locais não estiverem à mão.

## Estado agora (2026-09-03, fim de sessão de chat)

- **Repositório**: https://github.com/paulo-pvbn/markitdown_web — fork publicado, commit `51e6546`, tag `v1.00`.
- **Concluído e testado**: Ordens 01–05 (ver tabela abaixo). Interface manual + pipeline automático + manifesto funcionando. OCR: Tesseract escolhido e recomendado, ainda não implementado no código.
- **Prestes a rodar** (você está saindo antes de confirmar o resultado): **Ordem 06** (empacotar `.exe`) e **Ordem 07** (implementar OCR via Tesseract). Nenhuma das duas depende da outra — podem rodar em qualquer ordem, inclusive em paralelo em sessões diferentes do Claude Code.
- **Importante sobre interrupção**: fechar o chat aqui **não afeta** o Claude Code rodando no seu terminal — são processos totalmente independentes. O risco real é só se o próprio Claude Code for interrompido no meio de uma Ordem (ex.: fechar o VS Code durante os ~30 min do OCR do livro inteiro). Se isso acontecer antes do commit de fim de Ordem, não há checkpoint parcial — a Ordem precisaria recomeçar do início, não é perda de dados do projeto, só de tempo de execução.

## Histórico de Ordens

| Ordem | O que fez | Status | Relatório |
|---|---|---|---|
| 01 | Bootstrap: estrutura de pastas, arquivos da webapp no fork, commit + tag v1.00 | ✅ Concluída | `audit/2026-09-03-ORDEM-01-bootstrap-markitdown-web.md` |
| 02 | Validou `/convert-zip` e `watch.py` (sem Docker, via venv) | ✅ Concluída | `audit/2026-09-03-ORDEM-02-validar-convertzip-watch.md` |
| 03 | Piloto com material real — revelou PDF escaneado sem texto (gap de cobertura) | ✅ Concluída (achado documentado, não resolvido) | `audit/2026-09-03-ORDEM-03-piloto-real-claude-project.md` |
| 04 | Generalizou o pipeline (framing "qualquer app de IA") + `_manifest.json` por pasta | ✅ Concluída | `audit/2026-09-03-ORDEM-04-generalizar-pipeline.md` |
| 05 | Comparou Tesseract vs. rapidocr — Tesseract venceu com folga (8–17× mais rápido, qualidade muito melhor) | ✅ Concluída (investigação, recomendação registrada) | `audit/2026-09-03-ORDEM-05-comparar-ocr-tesseract-rapidocr.md` |
| 06 | Empacotar interface manual como `.exe` (duplo clique, sem terminal) | ⏳ Pronta pra rodar, ainda não executada | `ordens/ORDEM-06-empacotar-exe.md` |
| 07 | Implementar OCR via Tesseract, como job em lote separado do `watch.py` | ⏳ Pronta pra rodar, ainda não executada | `ordens/ORDEM-07-ocr-tesseract-lote.md` |

## Decisões-chave já tomadas (não re-perguntar)

- Pular Docker por enquanto (venv resolve pros testes atuais).
- Tesseract, não rapidocr, se/quando OCR for implementado — já decidido, Ordem 07 já escrita nessa direção.
- OCR roda como job em lote manual, nunca síncrono no `watch.py`.
- `.exe` na versão simples (abre navegador), não `pywebview` (janela nativa) — não proporcional pro ganho.
- Pipeline reposicionado como genérico ("qualquer app de IA"), não exclusivo a Claude Projects.
- Upload final pro Claude Project continua manual — sem API pública da Anthropic pra isso, e não vale o risco de segurança de soluções não-oficiais baseadas em sessão do navegador.

## Link permanente

Status completo e narrativo (mesmo conteúdo, outra forma): [MarkItDown Web — Status Atual e Backup Técnico](https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72) (Notion).
