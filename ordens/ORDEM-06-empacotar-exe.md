## Ordem 06: Empacotar a interface manual como `.exe` (duplo clique, sem terminal)

- **Depende de**: nenhuma (independente das Ordens 04/05)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-03): variante simples (abre navegador), não `pywebview`. Avaliação do arquiteto: a única diferença real entre as duas é estética (aba de navegador vs. janela nativa); `pywebview` soma dependência do WebView2 + mais uma camada de empacotamento em cima do problema já conhecido do `magika`/onnxruntime, sem ganho funcional pra um uso pessoal. Não é proporcional agora.

## Objetivo

Gerar um `.exe` único (Windows) que, com duplo clique, sobe a interface manual (`app.py`) em segundo plano e abre o navegador padrão direto na tela de conversão — sem terminal, sem digitar `python app.py`. Só a interface manual; `watch.py` fica fora do escopo desta ordem.

## Contrato de dados

Sem alteração de schema. Dois arquivos novos:
- `webapp/launcher.py` — inicia o Flask (`app.py`) numa thread em segundo plano com `debug=False, use_reloader=False` (já é o padrão do projeto), espera o servidor responder, e chama `webbrowser.open("http://127.0.0.1:5000")`.
- `webapp/markitdown-web.spec` — build do PyInstaller, com `--add-data` explícito para: (1) `static/index.html` e demais estáticos, (2) o(s) arquivo(s) de modelo ONNX que o `magika` carrega em tempo de execução. **Localizar o caminho exato desses arquivos dentro do pacote instalado antes de escrever o spec — não presumir o caminho.**

## Casos de borda que o executor deve tratar

- **Porta 5000 já em uso** (ex.: `app.py` já rodando manualmente, ou o `.exe` executado duas vezes) — o launcher deve detectar isso e só abrir o navegador na URL existente, em vez de travar com erro de "endereço já em uso".
- **`magika` carrega um modelo ONNX em tempo de execução** — se o PyInstaller não empacotar esse arquivo corretamente, a conversão falha silenciosamente ou com erro obscuro dentro do `.exe`, mesmo que o build em si tenha "funcionado" sem erro aparente. Testar conversão de um arquivo real dentro do `.exe` gerado é obrigatório — sucesso do comando `pyinstaller` não é evidência de que o app funciona.
- Caminho dos arquivos estáticos precisa resolver tanto rodando normal (`python app.py`) quanto congelado dentro do `.exe` (via `sys._MEIPASS`) — usar o padrão documentado do PyInstaller pra isso, sem quebrar o modo de desenvolvimento atual.
- Se o Windows Defender/SmartScreen bloquear ou colocar o `.exe` recém-gerado em quarentena, registrar isso no relatório como comportamento esperado (não é bug do app) — não tentar contornar ou desabilitar proteção do sistema.

## Fora de escopo (explicitamente)

- Não empacotar `watch.py` nesta ordem — só a interface manual.
- Não implementar a variante `pywebview` (janela nativa) — decisão já tomada.
- Não assinar digitalmente o `.exe` — certificado de editor é custo/processo à parte, fora do escopo de uma ferramenta pessoal.
- Não integrar Docker, Tailscale, OCR, ou o manifesto da Ordem 04 nesta ordem.
- Não criar `ORDEM-07` nesta sessão.

## Referência visual/técnica

- `webapp/app.py` — usar exatamente como está, sem mudar a lógica de conversão.
- `webapp/static/index.html` — interface já validada (ver preview mostrado em chat), sem mudanças de UI nesta ordem.

## Critério de pronto

1. `webapp/launcher.py` criado e funcional rodando via `python launcher.py` (sem PyInstaller ainda) — sobe o Flask e abre o navegador sozinho.
2. `.exe` gerado via PyInstaller a partir do spec.
3. `.exe` testado numa pasta limpa (fora do ambiente de desenvolvimento, sem venv ativo) — duplo clique abre o navegador na tela de conversão, sem terminal visível.
4. Pelo menos uma conversão real de arquivo (reaproveitar o `.docx` de teste já usado nas Ordens anteriores) testada rodando dentro do `.exe`, confirmando que `magika`/`markitdown` funcionam empacotados, não só em desenvolvimento.
5. Porta ocupada tratada sem crash (testar abrindo o `.exe` duas vezes seguidas).
6. Relatório de auditoria em `audit/`, incluindo tamanho final do `.exe` e se o SmartScreen/Defender reagiu de alguma forma.
