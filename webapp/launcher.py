"""
MarkItDown Web — launcher.

Sobe a interface manual (app.py) em segundo plano e abre o navegador
padrão direto na tela de conversão — sem terminal, sem digitar
`python app.py`. Pensado pra ser empacotado como .exe via PyInstaller
(ver markitdown-web.spec).

Uso:
    python launcher.py
"""

import socket
import threading
import time
import webbrowser

HOST = "127.0.0.1"
PORT = 5000
URL = f"http://{HOST}:{PORT}"


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
    if _port_in_use(HOST, PORT):
        # Ja tem um app.py (ou outra instancia deste .exe) rodando nesta
        # porta - so abre o navegador na URL existente, sem tentar subir
        # outro servidor por cima (evita o erro de "endereco ja em uso").
        print(f"Porta {PORT} ja em uso - abrindo {URL} direto.")
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
