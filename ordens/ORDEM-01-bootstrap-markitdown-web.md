## Ordem 01: Bootstrap do projeto — estrutura de pastas, integração no fork e primeiro commit

- **Depende de**: nenhuma
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — arquitetura definida e testada em sessão de chat (Flask + watchdog + Docker), ver `docs/instrucoes-projeto-markitdown-web.md`

## Objetivo

Colocar a interface web + pipeline automático de conversão (já implementados e testados em sandbox pelo arquiteto) dentro do fork real do usuário (paulo-pvbn/markitdown_web), com a estrutura de pastas do método (`docs/`, `audit/`, `ordens/`, `versoes/`), e publicar o primeiro commit + tag `v1.00`.

## Contrato de dados

Sem alteração de schema — não há banco de dados neste projeto.

Contrato de arquivos: os arquivos abaixo já existem prontos (fornecidos pelo arquiteto, testados em sandbox) e devem ser colocados exatamente nesses caminhos, sem reescrever o conteúdo:
- `webapp/app.py`
- `webapp/watch.py`
- `webapp/static/index.html`
- `webapp/requirements.txt`
- `webapp/Dockerfile`
- `webapp/docker-compose.yml`
- `webapp/README.md`
- `docs/instrucoes-projeto-markitdown-web.md`
- `audit/TEMPLATE-AUDITORIA.md`

## Casos de borda que o executor deve tratar

- Se o repositório local já tiver mudanças não commitadas antes desta ordem começar, parar e perguntar ao usuário antes de sobrescrever qualquer coisa.
- Se `webapp/` já existir no repo local com conteúdo diferente do fornecido, não sobrescrever silenciosamente — comparar e reportar a diferença no relatório de auditoria em vez de decidir sozinho qual versão vale.
- Se `git push` falhar por falta de permissão/credencial configurada, registrar isso como pendência explícita no relatório em vez de tentar contornar (ex: não trocar de remote, não desabilitar autenticação).
- Se `docker compose up -d --build` falhar por falta do Docker instalado na máquina, registrar como pendência e validar via `python app.py` local (venv) como alternativa, deixando claro no relatório qual dos dois foi de fato testado.

## Fora de escopo (explicitamente)

- Não modificar `packages/markitdown` (o conversor em si) nesta ordem — só integrar a `webapp/` já construída.
- Não configurar Tailscale, VPS ou deploy remoto nesta ordem — só documentar a intenção em `docs/instrucoes-projeto-markitdown-web.md` se ainda não estiver.
- Não deixar `docker compose up` rodando permanentemente ao final da sessão — o objetivo é validar que builda e responde, não manter o serviço no ar.
- Não criar `ORDEM-02` ou seguintes nesta sessão — uma ordem por sessão, conforme o método.

## Referência visual/técnica

- Arquitetura completa e decisões já documentadas em `docs/instrucoes-projeto-markitdown-web.md` (mesma pasta desta ordem).
- Página de status persistente no Notion (Categoria A): https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72

## Critério de pronto

1. Estrutura de pastas criada na raiz do repo: `docs/`, `audit/`, `ordens/`, `versoes/` (esta pasta pode ficar vazia por enquanto — não há build versionado ainda).
2. `webapp/` presente na raiz do repo com os 7 arquivos listados no Contrato de dados.
3. `docker compose up -d --build` (rodado de dentro de `webapp/`) builda sem erro e `http://127.0.0.1:5000` responde HTTP 200. Se Docker não estiver disponível, validar via `python app.py` em venv local e registrar isso no relatório.
4. Primeiro commit feito e enviado (`git push`) para o fork em paulo-pvbn/markitdown_web.
5. Tag `v1.00` criada no commit e enviada (`git push --tags`).
6. Relatório de auditoria escrito em `audit/` seguindo `audit/TEMPLATE-AUDITORIA.md`, incluindo o hash do commit e o que foi de fato testado.
