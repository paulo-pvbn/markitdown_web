## Ordem 03: Piloto real — material de verdade em `raw/` até pronto pro Claude Project

- **Depende de**: Ordem 02
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: parcialmente — decidido em chat que este é o próximo passo (validar o pipeline com material real, visando um Claude Project de verdade). **Qual material e qual Project ainda não foram escolhidos — isso deve ser perguntado ao usuário no início da sessão, não decidido pelo executor.**

## Objetivo

Validar o pipeline completo com material real do Paulo (não mais fixtures sintéticos): escolher, com o usuário, uma pasta de documentos reais destinada a um Claude Project (existente ou a criar), rodar via `watch.py`, e deixar os `.md` prontos e revisados para o upload manual no Knowledge do Project.

## Contrato de dados

Sem alteração de schema nem de código-fonte esperada. Se o material real revelar um formato ou caso ainda não exercitado nas Ordens 01/02 (ex.: PDF com muitas imagens, planilha grande, arquivo protegido por senha), documentar a limitação encontrada no relatório — não é objetivo desta ordem corrigir bugs de conversão além disso, a menos que a falha seja bloqueante pro piloto.

## Casos de borda que o executor deve tratar

- **Antes de qualquer ação**, perguntar ao usuário: (1) qual pasta local de documentos reais usar como piloto, (2) que nome dar à subpasta em `raw/` (convenção já estabelecida: nome do Claude Project), (3) se é um Claude Project já existente ou um novo que ele vai criar no navegador.
- Se o material contiver dados sensíveis (ex.: documentos de investigação, dados pessoais), **confirmar explicitamente com o usuário que ele está ciente de que esse conteúdo vai para o Knowledge de um Claude Project na nuvem da Anthropic** antes de prosseguir — não presumir que está tudo bem só porque ele escolheu a pasta.
- Se algum arquivo real falhar na conversão, registrar no relatório qual arquivo e qual erro, em vez de pular silenciosamente ou tentar contornar sem reportar.

## Fora de escopo (explicitamente)

- Não automatizar o upload para o Claude Project — esse passo é manual, feito pelo Paulo no navegador (sem API pública pra isso, decisão já registrada em `docs/`).
- Não instalar Docker nem configurar Tailscale nesta ordem.
- Não criar `ORDEM-04` nesta sessão.

## Referência visual/técnica

- `docs/instrucoes-projeto-markitdown-web.md` — seção "Pipeline automatizado pra RAG", convenção de pastas `raw/<projeto>/` → `converted/<projeto>/`.
- Página de status persistente no Notion: https://app.notion.com/p/3d07fc15116481e28daef4f2f6be7a72

## Critério de pronto

1. Perguntado e confirmado com o usuário: pasta de origem, nome do Claude Project piloto, e ciência de que o conteúdo vai pra nuvem.
2. Subpasta criada em `raw/<nome-do-project>/` com o material real fornecido pelo usuário.
3. `watch.py` processou o material e gerou `.md` em `converted/<nome-do-project>/`, sem erro bloqueante (falhas pontuais documentadas, não escondidas).
4. Executor abriu pelo menos 1-2 dos `.md` gerados pra confirmar visualmente que a conversão preservou estrutura/conteúdo de forma legível — não só que o arquivo foi criado.
5. Relatório de auditoria escrito em `audit/`, incluindo instrução clara pro Paulo sobre o próximo passo manual (upload no navegador) — o upload em si e a confirmação de que o RAG está retornando o conteúdo certo ficam fora desta sessão, a cargo do usuário, reportados depois em chat.
