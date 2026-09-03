# Sessão: Piloto real — material de verdade em raw/ até pronto pro Claude Project

- **Data/hora**: 2026-09-03 16:53–17:05
- **Versão resultante**: v1.00 (sem nova tag — ordem de validação/descoberta, não de release)
- **Commit**: (ver commits desta sessão no log do `main`, feitos após este relatório)
- **Arquivos de exemplo usados**: `733086206-Mercado-Financeiro-13ed.pdf` (livro real fornecido pelo Paulo, ~66 MB, 418 páginas) — único arquivo disponível na pasta piloto.

## O que foi feito
- Confirmado com o usuário antes de qualquer ação: pasta de origem (`Arquivos Reais/`), nome do Claude Project piloto (**InvestBot**, ainda a ser criado no navegador), e que o material não é sensível.
- Adicionado `webapp/raw/` e `webapp/converted/` ao `.gitignore` — são dados do usuário (inclusive um livro possivelmente protegido por direitos autorais), não código-fonte; nunca deveriam ir pro GitHub. Não havia essa proteção antes desta ordem.
- Criada `webapp/raw/InvestBot/` e copiado o PDF real pra lá.
- Rodado `watch.py` real (pastas padrão `raw/`→`converted/` dentro de `webapp/`, via venv) sobre o material.
- **Resultado inesperado**: a conversão "funcionou" sem lançar erro, mas gerou um `.md` **vazio** (só front matter, 0 caracteres de conteúdo).
- Investigada a causa com `pdfplumber` diretamente: as 418 páginas do PDF são **imagens escaneadas**, 0 caracteres de texto extraível por página — é um livro escaneado, não um PDF com texto embutido.
- Reportado o achado ao usuário antes de prosseguir (conforme instrução da ordem: registrar falha real, não contornar silenciosamente). Usuário pediu para pensar numa solução, testar parcialmente se a ideia funciona, e documentar para o arquiteto validar — não pediu implementação completa.
- **Prova de conceito de OCR local** (fora do código da `webapp/`, só para avaliar viabilidade): instalado temporariamente `rapidocr-onnxruntime` (motor de OCR local, ONNX, sem binário externo tipo Tesseract, sem dependência de rede) no venv de teste; renderizadas 3 páginas de miolo do PDF (páginas 11, 51 e 121) como imagem via `pypdfium2`; rodado OCR nelas.
- Dependência de teste (`rapidocr-onnxruntime` e o que ela puxou: `opencv-python`, `pyclipper`, `shapely`, `PyYAML`) **desinstalada do venv** ao final — não faz parte do contrato desta ordem nem do `requirements.txt` do projeto.

## Decisões técnicas tomadas
- **Não implementei OCR no pipeline** — ficou só como prova de conceito isolada (script avulso, não integrado a `app.py`/`watch.py`), porque: (1) a Ordem 03 explicitamente proíbe criar `ORDEM-04` nesta sessão e o contrato de dados só previa documentar limitações, não corrigi-las, a menos que bloqueante; (2) os resultados da prova de conceito (ver abaixo) mostram que a solução, do jeito que foi testada, tem problemas sérios de qualidade e desempenho que merecem decisão consciente do arquiteto antes de qualquer implementação.
- **`.gitignore` atualizado nesta sessão** (`webapp/raw/`, `webapp/converted/`) — decisão tomada por conta própria, sem perguntar antes, porque o risco (subir um livro de terceiro pro GitHub, ainda que fork pessoal) é claro e a orientação de "não decidir sozinho" da Ordem 01 se aplicava a conflitos de conteúdo do contrato, não a proteções de segurança/privacidade óbvias. Sinalizando aqui pro arquiteto validar que concorda com a decisão.

## Arquivos alterados
- `.gitignore` — adicionadas as entradas `webapp/raw/` e `webapp/converted/`.
- `webapp/raw/InvestBot/733086206-Mercado-Financeiro-13ed.pdf` — cópia do material real (ignorado pelo git, não vai pro commit).
- `webapp/converted/InvestBot/733086206-Mercado-Financeiro-13ed.md` — saída da conversão real, vazia (ignorado pelo git).
- Nenhum arquivo de código (`webapp/app.py`, `webapp/watch.py`) foi alterado.

## Testes realizados
- **Pipeline real ponta a ponta**: `raw/InvestBot/*.pdf` → `watch.py` → `converted/InvestBot/*.md`. Rodou sem erro/crash, mas o resultado é vazio (ver "Pendências").
- **Diagnóstico de causa-raiz**: confirmado via `pdfplumber` que as 418 páginas do PDF não têm nenhum texto embutido — é 100% imagem escaneada.
- **Prova de conceito de OCR** (3 páginas de amostra, `rapidocr-onnxruntime`, CPU):
  - Página 11 (sumário): 100 linhas detectadas em 7,9s. Texto legível mas com **espaços entre palavras perdidos** em vários trechos (ex.: `"minadopelaflutuacaodamoedabrasileira"`) e **acentos removidos** (ex.: `"Politicas Economicas"` em vez de `"Políticas Econômicas"`).
  - Página 51 (texto corrido): 90 linhas em 9,0s. Mesmo padrão de qualidade — legível com esforço, mas não é um texto limpo.
  - Página 121 (tabela em duas colunas — rating de crédito): 106 linhas em **59,6s** — muito mais lento, e o texto saiu com a ordem das colunas embaralhada (célula de uma coluna intercalada com a outra), o que compromete a leitura de tabelas.
  - **Extrapolação de tempo**: com uma média grosseira de ~25s/página nessa amostra (bem variável, de 8s a 60s), as 418 páginas do livro levariam **da ordem de 3 horas** de processamento em CPU só para esse único arquivo.
- **Não testado**: qualquer arquivo de texto real (não-escaneado) — só havia esse PDF disponível na pasta piloto, e ele se revelou o "arquivo-problema" que a própria Ordem 03 previu como caso de borda possível (ver contrato de dados: "PDF com muitas imagens").
- **Critério de pronto #4** ("abrir 1-2 `.md` pra confirmar visualmente que a conversão preservou conteúdo") **não foi cumprido com o pipeline atual**, porque o único `.md` gerado está vazio. O que foi confirmado visualmente, em vez disso, foi a saída bruta do OCR de prova de conceito — que mostra que o *conteúdo* existe e é parcialmente recuperável, mas não com qualidade de produção.

## Pendências / próximos passos
- **Decisão em aberto para o arquiteto**: este livro escaneado específico não é compatível com o pipeline offline atual. Três caminhos possíveis, nenhum implementado nesta sessão:
  1. **Não oferecer suporte a PDF escaneado** — deixar documentado como limitação conhecida (mais simples, mais alinhado com o espírito "offline e enxuto" do projeto).
  2. **Adicionar OCR local opcional** (ex.: `rapidocr-onnxruntime` como extra) — viável tecnicamente e sem depender de rede, mas com qualidade imperfeita (falta de espaçamento e acentuação) e custo de tempo alto (horas por livro grande em CPU); precisaria de ajuste de pós-processamento e provavelmente rodar como job separado, não no fluxo do `watch.py` em tempo real.
  3. **Buscar uma versão do livro com texto embutido** (ex.: e-book oficial em vez de scan) em vez de resolver via OCR — mais simples e com qualidade muito superior, se disponível.
- Se o arquiteto optar pela opção 2, isso deveria virar uma `ORDEM-04` dedicada (fora de escopo desta sessão).
- O material real (`webapp/raw/InvestBot/`) permanece na máquina do Paulo, fora do controle de versão (protegido pelo `.gitignore` atualizado nesta sessão) — nenhuma ação de limpeza foi tomada, fica a critério do usuário mantê-lo ou não.
- **Próximo passo manual, fora desta sessão**: como o `.md` gerado está vazio, não há ainda conteúdo pronto pra subir no Knowledge de um Claude Project "InvestBot". Antes de criar o Project no navegador, vale decidir o caminho (1/2/3 acima) e obter pelo menos um documento com texto extraível pra validar o fluxo completo de ponta a ponta (incluindo o upload manual, que continua fora do escopo de qualquer ordem — sempre feito pelo Paulo no navegador).
- Nenhuma `ORDEM-04` foi criada nesta sessão, conforme escopo.

## Contexto pro arquiteto
- O objetivo original da Ordem 03 (validar com material real e deixar `.md` prontos pra upload) não foi alcançado com o único arquivo disponível, mas a sessão gerou uma descoberta importante: PDFs escaneados são um buraco real na cobertura do pipeline offline, e há uma solução tecnicamente viável (OCR local via ONNX, sem rede) mas com trade-offs que merecem uma decisão consciente, não uma implementação apressada.
- Recomendo decidir entre as 3 opções acima antes de escolher o material definitivo do piloto do InvestBot — se o Paulo tiver ou conseguir uma versão em texto (e-book, não scan) do mesmo material ou de outro livro de mercado financeiro, o piloto original (Ordem 03 tal como escrita) pode rodar rapidamente numa sessão seguinte, sem precisar resolver OCR primeiro.
