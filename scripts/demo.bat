@echo off
REM ============================================================
REM  Chat TCP - Demo local com servidor + 2 clientes
REM  Abre 3 janelas PowerShell automaticamente
REM ============================================================
set "PROJ=g:\Meu Drive\Pessoal\Estudos\Faculdade - Eng. Software\Infraestrutura de Redes\Trabalho Fevereiro 2026 - Socket"
set "PY=C:\Users\thiag\AppData\Local\Programs\Python\Python313\python.exe"

echo Iniciando demo local do Chat TCP...
echo.

REM Abre o servidor em nova janela
start "Servidor TCP" powershell -NoExit -Command ^
  "cd '%PROJ%'; $env:PYTHONIOENCODING='utf-8'; Write-Host '=== SERVIDOR ===' -ForegroundColor Cyan; & '%PY%' -m src.server.server"

timeout /t 2 /nobreak >nul

REM Abre cliente Alice
start "Cliente - Alice" powershell -NoExit -Command ^
  "cd '%PROJ%'; $env:PYTHONIOENCODING='utf-8'; Write-Host '=== CLIENTE: Alice ===' -ForegroundColor Green; & '%PY%' -m src.client.client --username Alice"

timeout /t 1 /nobreak >nul

REM Abre cliente Bob
start "Cliente - Bob" powershell -NoExit -Command ^
  "cd '%PROJ%'; $env:PYTHONIOENCODING='utf-8'; Write-Host '=== CLIENTE: Bob ===' -ForegroundColor Yellow; & '%PY%' -m src.client.client --username Bob"

echo.
echo 3 janelas abertas!
echo  - Servidor rodando localmente
echo  - Alice conectada
echo  - Bob conectado
echo.
echo Agora basta digitar mensagens em Alice ou Bob!
echo Use: /dm Bob ola    -^> mensagem direta
echo Use: /users         -^> ver quem esta online
echo Use: /quit          -^> desconectar
pause
