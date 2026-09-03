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
import json
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

MANIFEST_NAME = "_manifest.json"


def _load_manifest(out_dir: Path) -> dict:
    manifest_path = out_dir / MANIFEST_NAME
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"gerado_em": None, "arquivos": []}


def _save_manifest(out_dir: Path, manifest: dict) -> None:
    """Escrita atomica (tmp + rename) pra nao corromper o JSON se dois
    arquivos forem convertidos quase ao mesmo tempo na mesma subpasta."""
    manifest["gerado_em"] = datetime.datetime.now().isoformat(timespec="seconds")
    manifest_path = out_dir / MANIFEST_NAME
    tmp_path = out_dir / f".{MANIFEST_NAME}.tmp"
    tmp_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(manifest_path)


def _update_manifest(out_dir: Path, entry: dict) -> None:
    """Atualiza (nao recria do zero) o manifesto da subpasta: substitui a
    entrada existente do mesmo arquivo, se houver, ou adiciona uma nova."""
    manifest = _load_manifest(out_dir)
    arquivos = [a for a in manifest["arquivos"] if a["arquivo"] != entry["arquivo"]]
    arquivos.append(entry)
    manifest["arquivos"] = arquivos
    _save_manifest(out_dir, manifest)


def _parse_existing_md(out_path: Path):
    """Extrai front matter (source, source_path, converted_at) e corpo de um
    .md ja gerado por este script, pra backfill de manifesto sem reconverter."""
    content = out_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return None
    parts = content.split("---\n", 2)
    if len(parts) != 3:
        return None
    _, front, body = parts
    meta = {}
    for line in front.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, body.lstrip("\n")


def _backfill_manifest_entry(out_path: Path) -> None:
    """Garante entrada no manifesto pra um .md que ja existia antes desta
    ordem (Ordens 02/03), sem precisar reconverter o arquivo original."""
    parsed = _parse_existing_md(out_path)
    if parsed is None:
        return
    meta, body = parsed
    _update_manifest(
        out_path.parent,
        {
            "arquivo": out_path.name,
            "fonte": meta.get("source", out_path.stem),
            "convertido_em": meta.get("converted_at"),
            "caracteres": len(body),
        },
    )


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

    converted_at = datetime.datetime.now().isoformat(timespec="seconds")
    front_matter = (
        "---\n"
        f"source: {src_path.name}\n"
        f"source_path: raw/{rel.as_posix()}\n"
        f"converted_at: {converted_at}\n"
        "---\n\n"
    )
    out_path.write_text(front_matter + result.markdown, encoding="utf-8")
    _update_manifest(
        out_path.parent,
        {
            "arquivo": out_path.name,
            "fonte": src_path.name,
            "convertido_em": converted_at,
            "caracteres": len(result.markdown),
        },
    )
    print(f"[OK] {rel} -> converted/{out_path.relative_to(CONVERTED_DIR).as_posix()}", flush=True)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            convert_file(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            convert_file(Path(event.src_path))


def convert_existing() -> None:
    """Ao iniciar, converte o que já estiver em raw/ sem .md correspondente
    ainda, e garante entrada no manifesto pros .md que já existiam
    (retroagindo pra conversões feitas antes desta ordem)."""
    for src_path in RAW_DIR.rglob("*"):
        if not src_path.is_file():
            continue
        rel = src_path.relative_to(RAW_DIR)
        out_path = (CONVERTED_DIR / rel).with_suffix(".md")
        if not out_path.exists():
            convert_file(src_path)
        else:
            _backfill_manifest_entry(out_path)


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
