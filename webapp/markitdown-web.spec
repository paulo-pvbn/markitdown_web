# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec para o MarkItDown Web (interface manual empacotada).

Gera um .exe unico (Windows) que sobe app.py em segundo plano e abre o
navegador (via launcher.py) - sem terminal visivel.

O magika (usado pelo markitdown pra detectar tipo de arquivo) carrega um
modelo ONNX e um JSON de tipos de conteudo em tempo de execucao a partir
de arquivos dentro do proprio pacote (magika/models/, magika/config/) -
PyInstaller nao inclui isso automaticamente por serem dados, nao codigo,
entao precisam ser coletados explicitamente com collect_data_files.

Uso:
    pyinstaller markitdown-web.spec
"""

from PyInstaller.utils.hooks import collect_data_files

magika_datas = collect_data_files("magika")

a = Analysis(
    ["launcher.py"],
    pathex=[SPECPATH],
    binaries=[],
    datas=[
        ("static", "static"),
        *magika_datas,
    ],
    hiddenimports=["app"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="markitdown-web",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
