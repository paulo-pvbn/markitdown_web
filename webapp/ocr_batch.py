"""
MarkItDown Web — OCR em lote via Tesseract.

Processa PDFs que o watch.py sinalizou como precisando de OCR (front
matter com `ocr_pendente: true`, corpo vazio/quase vazio porque o PDF é
uma imagem escaneada sem texto embutido — ver Ordem 03). Roda sob
demanda, nunca automaticamente pelo watch.py: OCR é lento (Tesseract,
~4-5s por página; um livro de ~400 páginas leva ~30 minutos), então
fica separado do pipeline em tempo real de propósito (Ordem 07).

Configuração validada na Ordem 05: Tesseract, idiomas por+eng, PSM
automático (não força PSM alternativo — o padrão venceu nos testes),
300 DPI.

Pré-requisito: Tesseract instalado no sistema (não é pacote pip).
Windows: https://github.com/UB-Mannheim/tesseract/wiki
Se não estiver no PATH, defina TESSERACT_CMD com o caminho completo do
executável.

Reprocessar um arquivo que já passou por OCR é seguro — o script sempre
refaz o OCR de qualquer .md com `ocr_pendente: true` e sobrescreve.

Uso:
    python ocr_batch.py raw/InvestBot
    RAW_DIR=/dados/raw CONVERTED_DIR=/dados/converted python ocr_batch.py raw/InvestBot
"""

import datetime
import json
import os
import sys
import time
from pathlib import Path

import pypdfium2 as pdfium
import pytesseract

from purify import purify_markdown

RAW_DIR = Path(os.environ.get("RAW_DIR", "raw")).resolve()
CONVERTED_DIR = Path(os.environ.get("CONVERTED_DIR", "converted")).resolve()

OCR_LANG = "por+eng"
OCR_DPI = 300

MANIFEST_NAME = "_manifest.json"

_COMMON_WINDOWS_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def _check_tesseract() -> None:
    """Confirma que o binário do Tesseract está acessível, tentando (nessa
    ordem) TESSERACT_CMD, o PATH, e os caminhos padrão de instalação no
    Windows. Falha com mensagem clara se nenhum funcionar."""
    custom_cmd = os.environ.get("TESSERACT_CMD")
    if custom_cmd:
        pytesseract.pytesseract.tesseract_cmd = custom_cmd

    candidates = [None] if custom_cmd else [None, *_COMMON_WINDOWS_TESSERACT_PATHS]
    for candidate in candidates:
        if candidate:
            pytesseract.pytesseract.tesseract_cmd = candidate
        try:
            pytesseract.get_tesseract_version()
            return
        except Exception:  # noqa: BLE001 - tenta o proximo candidato
            continue

    print(
        "ERRO: Tesseract não encontrado (nem no PATH, nem nos caminhos padrão "
        "do Windows). É um pré-requisito de sistema, não um pacote pip — "
        "instale e garanta que está no PATH, ou defina a variável de ambiente "
        "TESSERACT_CMD com o caminho completo do executável.\n"
        "Windows: https://github.com/UB-Mannheim/tesseract/wiki",
        file=sys.stderr,
    )
    sys.exit(1)


def _load_manifest(out_dir: Path) -> dict:
    manifest_path = out_dir / MANIFEST_NAME
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"gerado_em": None, "arquivos": []}


def _save_manifest(out_dir: Path, manifest: dict) -> None:
    manifest["gerado_em"] = datetime.datetime.now().isoformat(timespec="seconds")
    manifest_path = out_dir / MANIFEST_NAME
    tmp_path = out_dir / f".{MANIFEST_NAME}.tmp"
    tmp_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(manifest_path)


def _update_manifest(out_dir: Path, entry: dict) -> None:
    manifest = _load_manifest(out_dir)
    arquivos = [a for a in manifest["arquivos"] if a["arquivo"] != entry["arquivo"]]
    arquivos.append(entry)
    manifest["arquivos"] = arquivos
    _save_manifest(out_dir, manifest)


def _parse_md(md_path: Path) -> dict:
    content = md_path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    parts = content.split("---\n", 2)
    if len(parts) != 3:
        return {}
    _, front, _body = parts
    meta = {}
    for line in front.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta


def _find_pending(converted_subdir: Path):
    for md_path in sorted(converted_subdir.rglob("*.md")):
        meta = _parse_md(md_path)
        if meta.get("ocr_pendente") == "true":
            yield md_path, meta


def _ocr_pdf(pdf_path: Path) -> str:
    pdf = pdfium.PdfDocument(str(pdf_path))
    n_pages = len(pdf)
    scale = OCR_DPI / 72
    parts = []
    for i in range(n_pages):
        t0 = time.time()
        page = pdf[i]
        img = page.render(scale=scale).to_pil()
        text = pytesseract.image_to_string(img, lang=OCR_LANG)
        parts.append(text.strip())
        print(f"  página {i + 1} de {n_pages} ({time.time() - t0:.1f}s)", flush=True)
    return "\n\n".join(parts)


def _rewrite_md(md_path: Path, meta: dict, ocr_text: str) -> int:
    ocr_text, _purify_stats = purify_markdown(ocr_text)
    meta["ocr"] = "true"
    meta["ocr_engine"] = "tesseract"
    meta["ocr_revisar"] = "true"
    meta["purified"] = "true"
    order = [
        "source",
        "source_path",
        "converted_at",
        "ocr_pendente",
        "ocr",
        "ocr_engine",
        "ocr_revisar",
        "purified",
    ]
    lines = ["---"]
    for key in order:
        if key in meta:
            lines.append(f"{key}: {meta[key]}")
    lines.append("---")
    lines.append("")
    front_matter = "\n".join(lines) + "\n\n"
    md_path.write_text(front_matter + ocr_text, encoding="utf-8")
    return len(ocr_text)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Uso: python {Path(__file__).name} <pasta em raw/, ex.: raw/InvestBot>", file=sys.stderr)
        sys.exit(1)

    _check_tesseract()

    raw_arg = Path(sys.argv[1]).resolve()
    try:
        rel = raw_arg.relative_to(RAW_DIR)
    except ValueError:
        print(f"ERRO: {raw_arg} não está dentro de RAW_DIR ({RAW_DIR}).", file=sys.stderr)
        sys.exit(1)

    converted_subdir = CONVERTED_DIR / rel
    if not converted_subdir.exists():
        print(f"ERRO: {converted_subdir} não existe.", file=sys.stderr)
        sys.exit(1)

    pending = list(_find_pending(converted_subdir))
    if not pending:
        print(f"Nenhum .md com ocr_pendente: true em {converted_subdir}.")
        return

    print(f"{len(pending)} arquivo(s) com OCR pendente em {converted_subdir}.")
    for md_path, meta in pending:
        source_name = meta.get("source")
        pdf_dir = RAW_DIR / rel / md_path.parent.relative_to(converted_subdir)
        pdf_path = pdf_dir / source_name
        if not source_name or not pdf_path.exists():
            print(f"[ERRO] {md_path.name}: PDF de origem não encontrado em {pdf_path}", file=sys.stderr)
            continue

        print(f"OCR: {md_path.relative_to(CONVERTED_DIR).as_posix()} <- {pdf_path.name}")
        ocr_text = _ocr_pdf(pdf_path)
        n_chars = _rewrite_md(md_path, meta, ocr_text)
        _update_manifest(
            md_path.parent,
            {
                "arquivo": md_path.name,
                "fonte": source_name,
                "convertido_em": meta.get("converted_at"),
                "caracteres": n_chars,
            },
        )
        print(f"[OK] {md_path.name}: {n_chars} caracteres extraídos via OCR")


if __name__ == "__main__":
    main()
