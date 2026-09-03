"""
MarkItDown Watch — converte automaticamente qualquer arquivo solto em
raw/ para Markdown em converted/, espelhando a estrutura de subpastas.

Pensado para: cada subpasta de raw/ = material de um projeto/tema
diferente (ex.: raw/investigacao-x/, raw/artigo-y/). O .md sai na
mesma subpasta dentro de converted/, pronto para arrastar para o
Knowledge do Claude Project correspondente.

Uso:
    python watch.py
    RAW_DIR=/dados/raw CONVERTED_DIR=/dados/converted python watch.py
"""

import datetime
import os
import sys
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Garante que importamos o pacote markitdown deste repo, não do PyPI.
_LOCAL_MARKITDOWN_SRC = Path(__file__).resolve().parent.parent / "packages" / "markitdown" / "src"
if _LOCAL_MARKITDOWN_SRC.exists():
    sys.path.insert(0, str(_LOCAL_MARKITDOWN_SRC))

from markitdown import MarkItDown  # noqa: E402

RAW_DIR = Path(os.environ.get("RAW_DIR", "raw")).resolve()
CONVERTED_DIR = Path(os.environ.get("CONVERTED_DIR", "converted")).resolve()
STABLE_CHECK_SECONDS = 1.5  # intervalo entre checagens de "arquivo parou de crescer"
STABLE_CHECK_ATTEMPTS = 20  # ~30s de espera máxima (arquivos grandes copiando pela rede, etc.)

RAW_DIR.mkdir(parents=True, exist_ok=True)
CONVERTED_DIR.mkdir(parents=True, exist_ok=True)

# enable_plugins=False e nenhum llm_client/endpoint de nuvem => 100% local.
md = MarkItDown(enable_plugins=False)

IGNORED_SUFFIXES = {".md", ".tmp", ".crdownload", ".part"}


def _wait_until_stable(path: Path) -> bool:
    """Espera o tamanho do arquivo parar de mudar, pra não converter um arquivo
    que ainda está sendo copiado/baixado pela metade."""
    last_size = -1
    for _ in range(STABLE_CHECK_ATTEMPTS):
        if not path.exists():
            return False
        size = path.stat().st_size
        if size == last_size:
            return True
        last_size = size
        time.sleep(STABLE_CHECK_SECONDS)
    return True


def convert_file(src_path: Path) -> None:
    if src_path.name.startswith("."):
        return
    if src_path.suffix.lower() in IGNORED_SUFFIXES:
        return
    if not src_path.is_file():
        return
    if not _wait_until_stable(src_path):
        return

    rel = src_path.relative_to(RAW_DIR)
    out_path = (CONVERTED_DIR / rel).with_suffix(".md")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = md.convert(str(src_path))
    except Exception as e:  # noqa: BLE001 - queremos logar qualquer falha de conversão e seguir
        print(f"[ERRO] {rel}: {e}", flush=True)
        return

    front_matter = (
        "---\n"
        f"source: {src_path.name}\n"
        f"source_path: raw/{rel.as_posix()}\n"
        f"converted_at: {datetime.datetime.now().isoformat(timespec='seconds')}\n"
        "---\n\n"
    )
    out_path.write_text(front_matter + result.markdown, encoding="utf-8")
    print(f"[OK] {rel} -> converted/{out_path.relative_to(CONVERTED_DIR).as_posix()}", flush=True)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            convert_file(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            convert_file(Path(event.src_path))


def convert_existing() -> None:
    """Ao iniciar, converte o que já estiver em raw/ sem .md correspondente ainda."""
    for src_path in RAW_DIR.rglob("*"):
        if not src_path.is_file():
            continue
        rel = src_path.relative_to(RAW_DIR)
        out_path = (CONVERTED_DIR / rel).with_suffix(".md")
        if not out_path.exists():
            convert_file(src_path)


if __name__ == "__main__":
    print(f"Observando {RAW_DIR} -> {CONVERTED_DIR}", flush=True)
    convert_existing()

    observer = Observer()
    observer.schedule(Handler(), str(RAW_DIR), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
