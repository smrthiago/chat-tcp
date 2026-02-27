@echo off
REM ============================================================
REM  Chat TCP - Demo REMOTO (servidor Railway ja rodando)
REM  Conecta 2 clientes ao servidor publico
REM ============================================================
set "PROJ=g:\Meu Drive\Pessoal\Estudos\Faculdade - Eng. Software\Infraestrutura de Redes\Trabalho Fevereiro 2026 - Socket"
set "PY=C:\Users\thiag\AppData\Local\Programs\Python\Python313\python.exe"
set "HOST=crossover.proxy.rlwy.net"
set "PORT=21518"

echo.
echo ============================================================
echo  Chat TCP - Conectando ao Servidor Remoto (Railway)
echo  Host: %HOST%:%PORT%
echo ============================================================
echo.
echo Abrindo 2 janelas de cliente...

REM Abre cliente Alice
start "Alice @ Railway" powershell -NoExit -Command ^
  "cd '%PROJ%'; $env:PYTHONIOENCODING='utf-8'; Write-Host '=== CLIENTE: Alice -> Railway ===' -ForegroundColor Cyan; & '%PY%' -m src.client.client --host %HOST% --port %PORT% --username Alice"

timeout /t 2 /nobreak >nul

REM Abre cliente Bob
start "Bob @ Railway" powershell -NoExit -Command ^
  "cd '%PROJ%'; $env:PYTHONIOENCODING='utf-8'; Write-Host '=== CLIENTE: Bob -> Railway ===' -ForegroundColor Green; & '%PY%' -m src.client.client --host %HOST% --port %PORT% --username Bob"

echo.
echo 2 clientes conectando ao servidor Railway!
echo Host: %HOST%
echo Porta: %PORT%
echo.
echo Agora basta digitar mensagens em cada janela.
echo Use: /dm Bob ola   -^> mensagem direta para Bob
echo Use: /users        -^> ver quem esta online
echo Use: /quit         -^> desconectar
pause
