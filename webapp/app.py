"""
MarkItDown Web — interface web local e offline para o MarkItDown.

Como rodar:
    pip install -r requirements.txt
    python app.py

Depois abra http://127.0.0.1:5000 no navegador.

Nenhuma chamada de rede é feita durante a conversão — tudo roda
localmente com os conversores nativos (sem LLM, sem nuvem). Ver
README.md para detalhes sobre o que fica de fora no modo offline.
"""

import io
import os
import sys
import tempfile
import zipfile
from pathlib import Path

from flask import Flask, request, jsonify, send_file, send_from_directory

# Garante que importamos o pacote markitdown deste repo (packages/markitdown/src),
# e não uma versão instalada via PyPI.
_LOCAL_MARKITDOWN_SRC = Path(__file__).resolve().parent.parent / "packages" / "markitdown" / "src"
if _LOCAL_MARKITDOWN_SRC.exists():
    sys.path.insert(0, str(_LOCAL_MARKITDOWN_SRC))

from markitdown import MarkItDown  # noqa: E402

app = Flask(__name__, static_folder="static", static_url_path="")

# enable_plugins=False e nenhum llm_client/endpoint de nuvem configurado
# => conversão 100% local, sem sair para a internet.
md = MarkItDown(enable_plugins=False)

# Uso pessoal/local, não exposto publicamente - limite generoso por padrão,
# ajustável via env var (mesmo padrão de HOST/PORT) se um arquivo real ainda
# assim for maior que isso.
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "500"))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
# Limite separado do Werkzeug >=3.1 pro buffer interno de parsing de
# multipart/form-data (não é específico de campo de texto - também trava
# upload de arquivo grande, ver Ordem 08). MAX_CONTENT_LENGTH já protege
# contra requisição gigante, então desativa esse teto à parte.
app.config["MAX_FORM_MEMORY_SIZE"] = None


@app.errorhandler(413)
def _upload_too_large(_e):
    # Sem isso, o Flask devolve uma pagina HTML de erro e o frontend quebra
    # tentando fazer res.json() nela (ver Ordem 08).
    return jsonify({"error": f"Arquivo muito grande. Limite atual: {MAX_UPLOAD_MB} MB."}), 413


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


def _convert_one(file_storage):
    original_name = file_storage.filename or "arquivo"
    suffix = Path(original_name).suffix
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            file_storage.save(tmp.name)
            tmp_path = tmp.name
        result = md.convert(tmp_path)
        return original_name, result.markdown, None
    except Exception as e:  # noqa: BLE001 - queremos reportar qualquer erro de conversão ao usuário
        return original_name, None, str(e)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.route("/convert", methods=["POST"])
def convert():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    results = []
    for f in files:
        name, markdown, error = _convert_one(f)
        if error:
            results.append({"filename": name, "ok": False, "error": error})
        else:
            results.append({"filename": name, "ok": True, "markdown": markdown})

    return jsonify({"results": results})


@app.route("/convert-zip", methods=["POST"])
def convert_zip():
    """Converte múltiplos arquivos e devolve um .zip com um .md para cada um."""
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "Nenhum arquivo enviado."}), 400

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        used_names = set()
        for f in files:
            name, markdown, error = _convert_one(f)
            stem = Path(name).stem or "arquivo"
            out_name = f"{stem}.md" if not error else f"{stem}_ERRO.txt"
            base_out_name = out_name
            i = 1
            while out_name in used_names:
                out_name = f"{stem}_{i}{Path(base_out_name).suffix}"
                i += 1
            used_names.add(out_name)
            zf.writestr(out_name, markdown if not error else error)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="markdown_convertido.zip",
    )


if __name__ == "__main__":
    # Padrão: só esta máquina (127.0.0.1). Para acesso pela rede local, Docker,
    # Tailscale, etc., defina HOST=0.0.0.0 (o Dockerfile já faz isso).
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(host=host, port=port, debug=False)
