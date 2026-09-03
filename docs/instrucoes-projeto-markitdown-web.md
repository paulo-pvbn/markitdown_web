# Instruções do projeto — MarkItDown Web

> Destilado de arquitetura + decisões vivas. Lido pelo executor (Claude Code) no início de toda sessão, antes de `audit/` recente e `docs/CHANGELOG.md`, conforme `docs/instrucoes-metodologia.md` (espelho da página Notion "Metodologia — Fluxo Arquiteto + Executor").

## O que é

Interface web offline + pipeline automatizado (Flask + watchdog) que converte PDF/Word/Excel/PowerPoint/HTML/Outlook para Markdown. Construído em cima do fork pessoal do [MarkItDown](https://github.com/paulo-pvbn/markitdown_web) (Microsoft). Objetivo: alimentar Claude Projects como conhecimento de RAG a partir de material heterogêneo, sem upload manual arquivo por arquivo.

## Arquitetura

- **Backend**: Flask (`webapp/app.py`) — interface web manual, expõe `/convert` e `/convert-zip`.
- **Pipeline automático**: `webapp/watch.py` (usa `watchdog`) — monitora `raw/` recursivamente, converte sozinho pra `converted/`, espelhando subpastas.
- **Conversor**: pacote `markitdown` deste mesmo repositório (`packages/markitdown/src`), não instalado via PyPI — qualquer alteração no core reflete nos dois serviços sem reinstalar nada.
- **Front-end**: arquivo único `webapp/static/index.html` (HTML+CSS+JS, sem CDN).
- **Empacotamento**: Docker, `webapp/docker-compose.yml` sobe `markitdown-web` (interface) + `markitdown-watch` (pipeline) juntos.

## Formatos suportados no modo offline

PDF, Word (.docx), PowerPoint (.pptx), Excel novo e antigo (.xlsx/.xls), Outlook (.msg), HTML, CSV/JSON/XML, ZIP, EPUB, imagens (EXIF) — tudo com dependências locais, sem chamada de rede.

Fora de propósito: transcrição de áudio (API de voz do Google), transcrição de YouTube, Azure Document Intelligence/Content Understanding, descrição de imagem via LLM — todos dependem de serviço externo, o que quebraria a garantia de offline.

## Decisões técnicas vivas

- **RAG dos Claude Projects é automático** — quando o conteúdo se aproxima do limite da janela de contexto, o Claude ativa busca por trecho relevante sozinho ([fonte](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects)). Por isso não há chunking manual no pipeline.
- **Extras de rede excluídos de propósito** — todos dependem de API externa.
- **Upload final pro Claude Project é manual, sem solução automatizada** — não existe API pública da Anthropic pra isso. Pacotes não-oficiais existem (reaproveitando sessão logada do navegador), mas dependem de guardar a chave de sessão da conta — risco de segurança desnecessário pro ganho.
- **Host/porta via env var (`HOST`/`PORT`), não hardcoded** — mesmo código-fonte atende uso local, rede/Tailscale e VPS sem branch separado.
- **`app.py` e `watch.py` importam o `markitdown` do próprio repositório**, não do PyPI.
- **Convenção de pastas do pipeline**: uma subpasta em `raw/<projeto>/` por Claude Project que o material vai alimentar; `.md` correspondente sai em `converted/<projeto>/` com front matter (`source`, `source_path`, `converted_at`).

## Três formas de rodar (documentadas em `webapp/README.md`)

1. Só local (`127.0.0.1`) — sem Docker.
2. Docker + rede local/Tailscale (`HOST=0.0.0.0`) — acesso mobile sem perder privacidade.
3. VPS público (fora do MVP) — precisa de proxy HTTPS + autenticação, deixa de ser "offline".

## Status persistente

Backup de status completo no Notion: [MarkItDown Web — Status Atual e Backup Técnico](https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72). Se as pastas locais do projeto tiverem qualquer problema, essa página reconstrói o contexto.

## Estado em 2026-09-03 (bootstrap)

Testado ponta a ponta em ambiente de sandbox: conversão de `.docx` via `/convert`, `/convert-zip` e via `watch.py` (drop em `raw/` → `.md` automático em `converted/`, com front matter) — todos funcionando. Ainda não integrado ao fork real no GitHub nem rodado na máquina pessoal do Paulo — objetivo da Ordem 01.
