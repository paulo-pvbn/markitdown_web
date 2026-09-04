"""
MarkItDown Web — launcher.

Sobe a interface manual (app.py) em segundo plano e abre o navegador
padrão direto na tela de conversão — sem terminal, sem digitar
`python app.py`. Pensado pra ser empacotado como .exe via PyInstaller
(ver markitdown-web.spec).

Ao iniciar, encerra automaticamente qualquer instância anterior ainda
rodando (via arquivo de lock com o PID) — garante que só a versão mais
recente do código fica no ar, em vez de conviver com uma instância
antiga esquecida (achado recorrente nas Ordens 08/09, resolvido na
Ordem 11).

Uso:
    python launcher.py
"""

import os
import socket
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

import psutil

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"

_LOCK_PATH = Path(tempfile.gettempdir()) / "markitdown-web.pid"

# Sinal de que um processo com o PID do lock e' mesmo uma instancia nossa
# (nome do executavel congelado, ou "python" rodando launcher.py/app.py em
# desenvolvimento) - evita matar um PID reciclado pelo Windows pra outro
# programa depois que a instancia antiga ja morreu sem limpar o lock.
_OUR_MARKERS = ("markitdown-web", "launcher.py", "app.py")


def _looks_like_our_process(proc: psutil.Process) -> bool:
    try:
        name = proc.name().lower()
        if "markitdown-web" in name:
            return True
        cmdline = " ".join(proc.cmdline()).lower()
        return any(marker in cmdline for marker in _OUR_MARKERS)
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return False


def _terminate_previous_instance() -> None:
    if not _LOCK_PATH.exists():
        return
    try:
        old_pid = int(_LOCK_PATH.read_text().strip())
    except (ValueError, OSError):
        return
    if old_pid == os.getpid():
        return
    try:
        proc = psutil.Process(old_pid)
    except psutil.NoSuchProcess:
        return
    if not _looks_like_our_process(proc):
        # PID reciclado pra outro programa - nao mexe (caso de borda da Ordem 11).
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except psutil.TimeoutExpired:
        proc.kill()
    except psutil.NoSuchProcess:
        pass


def _write_lock() -> None:
    _LOCK_PATH.write_text(str(os.getpid()))


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _wait_until_up(host: str, port: int, timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _port_in_use(host, port):
            return True
        time.sleep(0.2)
    return False


def _run_server() -> None:
    from app import app  # import tardio: precisa rodar depois da checagem de porta

    app.run(host=HOST, port=PORT, debug=False, use_reloader=False)


def main() -> None:
    _terminate_previous_instance()
    _write_lock()

    if _port_in_use(HOST, PORT):
        # Porta ainda ocupada por algo que nao era nossa instancia anterior
        # (ou que nao conseguimos encerrar) - so abre o navegador na URL
        # existente, sem tentar bindar de novo (evita erro de "endereco ja
        # em uso"). Rede de seguranca; o caminho normal agora e' encerrar a
        # instancia antiga acima e assumir a porta.
        print(f"Porta {PORT} ja em uso por outro processo - abrindo {URL} direto.")
        webbrowser.open(URL)
        return

    thread = threading.Thread(target=_run_server, daemon=True)
    thread.start()

    if _wait_until_up(HOST, PORT):
        webbrowser.open(URL)
    else:
        print(f"Servidor nao respondeu em {URL} a tempo.")

    # Mantem o processo vivo enquanto a thread do servidor estiver rodando
    # (a thread e daemon, entao o processo encerra sozinho se o app cair).
    while thread.is_alive():
        time.sleep(1)


if __name__ == "__main__":
    main()
