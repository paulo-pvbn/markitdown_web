## Ordem 11: Encerrar instância antiga automaticamente + botão de sair na interface

- **Depende de**: Ordem 06 (`launcher.py`, comportamento de porta ocupada que esta ordem substitui)
- **Bloqueia**: nenhuma conhecida
- **Decisão de produto já confirmada?**: sim — decidido em chat (2026-09-04): resolver de vez o problema recorrente de instância antiga do `.exe` ficar rodando e interferir em testes (3+ ocorrências documentadas nas Ordens 08/09), em vez de só documentar/lembrar.

## Objetivo

Duas mudanças relacionadas: (1) ao iniciar, o launcher detecta e encerra automaticamente qualquer instância anterior do `.exe` ainda rodando, garantindo que só a versão mais recente do código fica no ar — resolve o problema real que já causou resultado de teste enganoso em duas sessões (Ordens 08 e 09); (2) a interface ganha um botão "Sair" que encerra o servidor de dentro do navegador, dando ao Paulo uma forma real de fechar sem precisar do Gerenciador de Tarefas.

## Contrato de dados

- `webapp/launcher.py`: escreve um arquivo de lock com o PID do processo atual (ex.: `%TEMP%/markitdown-web.pid`, ou caminho equivalente ao lado do executável). Ao iniciar, se o arquivo já existir e o PID nele ainda estiver vivo, encerrar esse processo antes de prosseguir (`terminate()`, com fallback pra `kill()` se não encerrar em alguns segundos), então escrever o próprio PID no lock.
- **Isso substitui o comportamento da Ordem 06** ("porta ocupada → só abre o navegador na URL existente") — a instância nova agora sempre assume o controle, não convive mais com a antiga.
- `webapp/app.py`: nova rota `POST /shutdown` que encerra o processo do servidor de forma limpa.
- `webapp/static/index.html`: botão "Sair" (canto superior, discreto) que chama `/shutdown` e mostra confirmação antes de a página parar de responder.

## Casos de borda que o executor deve tratar

- Se o processo antigo não for um `markitdown-web.exe`/`launcher.py` de verdade (PID reciclado pelo Windows pra outro programa depois que o antigo já morreu sem limpar o lock file), **não matar processo errado** — validar de alguma forma (nome do processo), ou aceitar a corrida residual e documentar como limitação de baixo risco (uso pessoal, máquina única).
- `/shutdown` só deve funcionar chamado de `127.0.0.1`/localhost — não expor encerramento remoto do servidor caso `HOST=0.0.0.0` (modo rede/Tailscale) esteja em uso.
- Testar o cenário completo real: abrir o `.exe`, abrir de novo sem fechar o primeiro (o caso que vem causando o problema), confirmar que só a instância nova sobrevive e responde.
- Testar o botão "Sair" de verdade encerrando o processo (verificar via lista de processos do Windows que ele realmente some, não só que a página para de responder).
- `.exe` reconstruído ao final (mesmo processo já validado) com as duas mudanças.

## Fora de escopo (explicitamente)

- Não implementar ícone na bandeja do sistema (system tray) — mais complexo de empacotar (dependência nova, mais um ponto de falha no PyInstaller); o botão "Sair" na própria interface resolve o mesmo problema com bem menos risco.
- Não mudar nada em `watch.py`/`ocr_batch.py`.
- Não criar `ORDEM-12` nesta sessão.

## Referência visual/técnica

- `webapp/launcher.py` (Ordem 06) — lógica atual de detecção de porta ocupada, a ser substituída.
- Achado recorrente relatado pelo Paulo em chat: `.exe` antigo interferindo em testes nas Ordens 08 e 09.

## Critério de pronto

1. Abrir o `.exe` duas vezes seguidas sem fechar a primeira resulta em só uma instância viva (a mais nova) — testado de verdade, não só revisão de código.
2. Botão "Sair" na interface encerra o processo de fato (confirmado via lista de processos).
3. `/shutdown` não responde a chamadas de fora de localhost.
4. `.exe` reconstruído com as duas mudanças, testado numa pasta limpa.
5. Relatório de auditoria em `audit/`.
