@echo off
setlocal

rem MarkItDown Web - alternativa mais leve ao .exe pra quem ja tem Python
rem instalado. Checa Python no PATH, checa se as dependencias importam,
rem instala requirements.txt so se estiver faltando, e sobe o launcher.py
rem (mesmo launcher usado pelo .exe, Ordens 06/11 - abre o navegador
rem sozinho e encerra qualquer instancia anterior automaticamente).

where python >nul 2>nul
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale o Python em https://www.python.org/downloads/ e tente de novo.
    echo Lembre de marcar "Add python.exe to PATH" durante a instalacao.
    pause
    exit /b 1
)

python -c "import flask, markitdown" >nul 2>nul
if errorlevel 1 (
    echo Dependencias faltando ou incompletas - instalando via requirements.txt...
    python -m pip install -r "%~dp0requirements.txt"
    if errorlevel 1 (
        echo ERRO: falha ao instalar dependencias. Veja a mensagem acima.
        pause
        exit /b 1
    )
) else (
    echo Dependencias ja instaladas.
)

python "%~dp0launcher.py"
