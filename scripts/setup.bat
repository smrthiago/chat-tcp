@echo off
echo === Chat TCP - Setup ===
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale em https://python.org
    exit /b 1
)
echo [OK] Python encontrado

REM Cria ambiente virtual
if not exist "venv" (
    python -m venv venv
    echo [OK] Ambiente virtual criado
)

REM Ativa e instala dependências
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo [OK] Dependencias instaladas

REM Cria .env
if not exist ".env" (
    copy .env.example .env
    echo [OK] Arquivo .env criado
)

REM Cria logs
if not exist "logs" mkdir logs
echo [OK] Diretorio de logs criado

echo.
echo === Setup concluido! ===
echo.
echo   Para iniciar o servidor:
echo     scripts\run_server.bat
echo.
echo   Para iniciar um cliente (em outro terminal):
echo     scripts\run_client.bat
echo.
