# Instruções do projeto — MarkItDown Web

> Destilado de arquitetura + decisões vivas. Lido pelo executor (Claude Code) no início de toda sessão, antes de `audit/` recente e `docs/CHANGELOG.md`, conforme `docs/instrucoes-metodologia.md` (espelho da página Notion "Metodologia — Fluxo Arquiteto + Executor").

## O que é

Interface web offline + pipeline automatizado (Flask + watchdog) que converte PDF/Word/Excel/PowerPoint/HTML/Outlook para Markdown. Construído em cima do fork pessoal do [MarkItDown](https://github.com/paulo-pvbn/markitdown_web) (Microsoft). Objetivo: transformar material heterogêneo numa pasta de Markdown pronta pra qualquer app ou agente de IA consumir (RAG, fine-tuning, contexto manual) — Claude Projects é um exemplo de destino, não o único.

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

- **Não há chunking manual no pipeline** — cada app/agente de destino resolve indexação/busca do seu jeito. No caso específico dos Claude Projects, o RAG já é automático (ativa busca por trecho relevante quando o conteúdo se aproxima do limite da janela de contexto — [fonte](https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects)), mas o pipeline não presume isso pra nenhum outro consumidor.
- **Extras de rede excluídos de propósito** — todos dependem de API externa.
- **Entrega final no destino (upload, ingestão, indexação) é manual ou de responsabilidade de cada app** — o pipeline entrega até a pasta `converted/` com `.md` + manifesto; não há integração automatizada com nenhum destino específico. No caso de Claude Projects, isso significa upload manual no navegador (sem API pública da Anthropic pra isso — pacotes não-oficiais existem reaproveitando sessão logada, mas dependem de guardar a chave de sessão da conta, risco de segurança desnecessário pro ganho).
- **Host/porta via env var (`HOST`/`PORT`), não hardcoded** — mesmo código-fonte atende uso local, rede/Tailscale e VPS sem branch separado.
- **`app.py` e `watch.py` importam o `markitdown` do próprio repositório**, não do PyPI.
- **Convenção de pastas do pipeline**: uma subpasta em `raw/<nome>/` por projeto/tema/destino que o material vai alimentar (Claude Project, outro agente, um vector DB, etc.); `.md` correspondente sai em `converted/<nome>/` com front matter (`source`, `source_path`, `converted_at`) e um manifesto por subpasta (`_manifest.json`, ver Ordem 04) listando todos os arquivos convertidos ali.

## Três formas de rodar (documentadas em `webapp/README.md`)

1. Só local (`127.0.0.1`) — sem Docker.
2. Docker + rede local/Tailscale (`HOST=0.0.0.0`) — acesso mobile sem perder privacidade.
3. VPS público (fora do MVP) — precisa de proxy HTTPS + autenticação, deixa de ser "offline".

## Status persistente

Backup de status completo no Notion: [MarkItDown Web — Status Atual e Backup Técnico](https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72). Se as pastas locais do projeto tiverem qualquer problema, essa página reconstrói o contexto.

## Estado em 2026-09-03 (bootstrap)

Bootstrap publicado no fork real: commit `51e6546`, tag `v1.00`, push concluído em `origin/main` e `origin/v1.00` (relatório completo em `audit/2026-09-03-ORDEM-01-bootstrap-markitdown-web.md`). Docker não estava disponível na máquina no momento do bootstrap — validação feita via venv local (`python app.py`); `GET /` e `POST /convert` confirmados funcionando ponta a ponta com arquivo real. Ainda não testados: build Docker (`docker compose up -d --build`), `POST /convert-zip`, e o pipeline `watch.py` (`raw/` → `converted/`).

### Pendência

Decisão em aberto: instalar Docker Desktop na máquina antes de validar o caminho documentado no `webapp/README.md` para rede local/Tailscale, ou seguir testando via venv por enquanto.
