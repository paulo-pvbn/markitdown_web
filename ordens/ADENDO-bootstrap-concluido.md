> Mesclar na próxima vez que uma ordem tocar em `docs/instrucoes-projeto-markitdown-web.md` — não substituir o arquivo inteiro.

## Atualizar a seção "Estado em 2026-09-03 (bootstrap)"

Substituir o parágrafo atual dessa seção por:

Bootstrap publicado no fork real: commit `51e6546`, tag `v1.00`, push concluído em `origin/main` e `origin/v1.00` (relatório completo em `audit/2026-09-03-ORDEM-01-bootstrap-markitdown-web.md`). Docker não estava disponível na máquina no momento do bootstrap — validação feita via venv local (`python app.py`); `GET /` e `POST /convert` confirmados funcionando ponta a ponta com arquivo real. Ainda não testados: build Docker (`docker compose up -d --build`), `POST /convert-zip`, e o pipeline `watch.py` (`raw/` → `converted/`).

## Pendência nova a registrar

Decisão em aberto: instalar Docker Desktop na máquina antes de validar o caminho documentado no `webapp/README.md` para rede local/Tailscale, ou seguir testando via venv por enquanto.
