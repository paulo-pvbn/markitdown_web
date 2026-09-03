## Ordem 02: Validar `/convert-zip` e pipeline `watch.py` via venv (sem Docker)

- **Depende de**: Ordem 01 (bootstrap)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em sessão de chat (2026-09-03): pular Docker por enquanto, validar via venv.

## Objetivo

Confirmar que os dois recursos ainda não testados na Ordem 01 — download `/convert-zip` e o pipeline automático `watch.py` (`raw/` → `converted/`) — funcionam corretamente, usando o mesmo venv já criado em `webapp/.venv`, sem depender de Docker.

## Contrato de dados

Sem alteração de schema. Sem alteração de código-fonte esperada — se algum bug real for encontrado durante o teste, corrigir o mínimo necessário pra destravar e documentar a decisão no relatório (não é objetivo desta ordem refatorar nada além disso).

Usar pelo menos 2 tipos de arquivo diferentes nos testes (reaproveitar `test_convert.html` da Ordem 01 + gerar mais 1-2, ex.: um `.docx` sintético).

## Casos de borda que o executor deve tratar

- `watch.py`: reiniciar o processo com um arquivo já em `raw/` sem `.md` correspondente ainda — confirmar que `convert_existing()` converte na inicialização, sem precisar de novo evento de arquivo.
- `watch.py`: dois arquivos com o mesmo nome em subpastas diferentes de `raw/` (ex.: `raw/projeto-a/nota.docx` e `raw/projeto-b/nota.docx`) — confirmar que não colidem em `converted/`.
- `/convert-zip`: múltiplos arquivos no mesmo request, incluindo pelo menos um que falhe de propósito (extensão não suportada ou arquivo corrompido) — confirmar que o `.zip` resultante inclui o `.md` dos que deram certo **e** um `_ERRO.txt` do que falhou, sem que a falha interrompa os demais.
- Se não for prático simular um arquivo grande "ainda sendo copiado" pra testar a espera de estabilidade de tamanho do `watch.py`, registrar isso como não testado no relatório em vez de forçar um teste artificial de baixa confiança.

## Fora de escopo (explicitamente)

- Não instalar ou testar Docker nesta ordem — decisão já tomada de adiar.
- Não configurar Tailscale ou qualquer acesso de rede nesta ordem.
- Não modificar `packages/markitdown`.
- Não criar `ORDEM-03` nesta sessão.

## Referência visual/técnica

- Mesclar `ordens/ADENDO-bootstrap-concluido.md` em `docs/instrucoes-projeto-markitdown-web.md` antes de começar — é a primeira ordem desde o bootstrap a tocar nesse arquivo, conforme convenção do método (mesclar, nunca substituir).
- `audit/2026-09-03-ORDEM-01-bootstrap-markitdown-web.md` — relatório da sessão anterior, pra saber exatamente o que já foi validado e não repetir.

## Critério de pronto

1. `watch.py` rodando localmente (venv), testado com pelo menos 2 arquivos de tipos diferentes soltos em `raw/<subpasta-teste>/`, gerando `.md` correspondente em `converted/<subpasta-teste>/` com front matter correto.
2. Reinício do `watch.py` com arquivo pendente em `raw/` sem `.md` — confirmado que converte ao iniciar, via `convert_existing()`.
3. `POST /convert-zip` testado com múltiplos arquivos (incluindo um caso de erro proposital) — `.zip` resultante contém `.md` de cada sucesso + `.txt` de erro da falha, sem interromper os demais.
4. `ADENDO-bootstrap-concluido.md` mesclado em `docs/instrucoes-projeto-markitdown-web.md` (não sobrescrito).
5. Relatório de auditoria escrito em `audit/` seguindo `audit/TEMPLATE-AUDITORIA.md`.
