# Manual do Usuário — Chat TCP/IP

> Guia completo para instalar, configurar e usar o sistema de chat localmente e com o servidor Railway.

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Instalação Rápida](#2-instalação-rápida)
3. [Usando Localmente](#3-usando-localmente)
4. [Conectando ao Servidor Remoto (Railway)](#4-conectando-ao-servidor-remoto-railway)
5. [Comandos do Chat](#5-comandos-do-chat)
6. [Configuração Avançada (.env)](#6-configuração-avançada-env)
7. [Usando com Docker](#7-usando-com-docker)
8. [Rodando os Testes](#8-rodando-os-testes)
9. [Solução de Problemas](#9-solução-de-problemas)
10. [Deploy no Railway (guia completo)](#10-deploy-no-railway-guia-completo)

---

## 1. Pré-requisitos

### Obrigatório
- **Python 3.11+** — [Download](https://python.org/downloads)
  - Windows: marque "Add Python to PATH" durante a instalação
  - Verifique: `python --version`

### Opcional
- **Git** — para clonar o repositório
- **Docker** — para usar a versão containerizada
- **Conta Railway** — para deploy remoto

---

## 2. Instalação Rápida

### Clonar e instalar

```bash
# Clone o repositório
git clone https://github.com/smrthiago/chat-tcp.git
cd chat-tcp

# Windows — execute o script de setup
scripts\setup.bat

# Linux/macOS
chmod +x scripts/*.sh
./scripts/setup.sh
```

O script de setup automaticamente:
- Verifica a versão do Python
- Cria um ambiente virtual (`venv/`)
- Instala todas as dependências
- Cria o arquivo `.env` a partir do `.env.example`
- Cria o diretório `logs/`

### Instalação manual (alternativa)

```bash
# Instalar dependências diretamente (sem venv)
pip install cryptography colorama python-dotenv

# Instalar dependências de desenvolvimento (testes + lint)
pip install cryptography colorama python-dotenv pytest pytest-cov flake8
```

---

## 3. Usando Localmente

### Passo 1 — Inicie o servidor

Abra um terminal e rode:

```bash
# Windows (script)
scripts\run_server.bat

# Windows (direto)
python -m src.server.server

# Linux/macOS
./scripts/run_server.sh
# ou
python3 -m src.server.server
```

Você verá a saída:
```
============================================================
  Chat TCP Server v1.0
  Endereço : 0.0.0.0:5000
  Clientes : máximo 50
  Cripto   : Fernet AES-128 ativa
============================================================

15:30:22 [server] INFO — Aguardando conexões...
```

### Passo 2 — Conecte um cliente

Abra **outro terminal** (sem fechar o servidor) e rode:

```bash
# Windows (script)
scripts\run_client.bat

# Windows (direto)
python -m src.client.client

# Com username pré-definido
python -m src.client.client --username Alice

# Linux/macOS
./scripts/run_client.sh --username Alice
```

Você verá o prompt de login (ou entra direto se usou `--username`):
```
============================================================
  Chat TCP/IP  •  Conectado como Alice
  Criptografia Fernet (AES-128) ativa
============================================================
  Comandos: /users  /dm <user> <msg>  /help  /quit

Alice >
```

### Passo 3 — Conecte mais clientes

Repita o Passo 2 em **outros terminais** com usernames diferentes. Todos os clientes conectados ao mesmo servidor local vão trocar mensagens em tempo real.

### Demo automático (abre tudo de uma vez)

```bash
# Abre servidor + 2 clientes em janelas separadas automaticamente
scripts\demo.bat
```

---

## 4. Conectando ao Servidor Remoto (Railway)

O servidor está **publicado e rodando** 24/7 na internet. Qualquer pessoa com o código pode se conectar:

### Informações de conexão

| Campo | Valor |
|---|---|
| **Host** | `crossover.proxy.rlwy.net` |
| **Porta** | `21518` |
| **Protocolo** | TCP |
| **Status** | 🟢 Online |

### Como conectar

```bash
python -m src.client.client --host crossover.proxy.rlwy.net --port 21518
```

Com username definido:
```bash
python -m src.client.client --host crossover.proxy.rlwy.net --port 21518 --username SeuNome
```

### Demo remoto automático (abre 2 clientes)

```bash
# Clique duas vezes ou execute:
scripts\demo_railway.bat
```

### Demonstração com colega (redes diferentes!)

**No seu computador:**
```bash
python -m src.client.client --host crossover.proxy.rlwy.net --port 21518 --username Thiago
```

**No computador do colega (qualquer rede, qualquer lugar):**
```bash
# Colega precisa ter Python + cryptography instalados
pip install cryptography colorama python-dotenv
git clone https://github.com/smrthiago/chat-tcp.git
cd chat-tcp
python -m src.client.client --host crossover.proxy.rlwy.net --port 21518 --username Colega
```

Vocês vão conversar em tempo real, com mensagens criptografadas, via servidor na Europa (Railway).

---

## 5. Comandos do Chat

Dentro do chat, além de digitar mensagens normais, você tem esses comandos especiais:

| Comando | Descrição | Exemplo |
|---|---|---|
| `<texto>` | Envia mensagem para **todos** os usuários | `Olá pessoal!` |
| `/dm <user> <msg>` | Mensagem **direta e privada** para um usuário | `/dm Bob oi sumaê` |
| `/users` | Lista todos os usuários **online agora** | `/users` |
| `/help` | Mostra lista de comandos | `/help` |
| `/quit` | **Desconecta** e encerra o cliente | `/quit` |
| `Ctrl+C` | Interrompe e desconecta | — |

### Exemplo de sessão completa

```
Alice > Olá a todos!
[15:32] 💬 Alice: Olá a todos!

  ℹ  🟢 Bob entrou no chat

Alice > /users
  👥 Usuários online (2):
    • Alice (desde 15:30)
    • Bob (desde 15:32)

Alice > /dm Bob Oi Bob! Mensagem privada
[15:33] 🔮 → Bob: Oi Bob! Mensagem privada

Alice > /quit
  Desconectado. Até logo, Alice! 👋
```

---

## 6. Configuração Avançada (.env)

O arquivo `.env` na raiz do projeto controla todas as configurações. Copie o `.env.example` e edite:

```bash
cp .env.example .env
```

### Variáveis disponíveis

```bash
# ═══ SERVIDOR ═══════════════════════════════════════════════════
SERVER_HOST=0.0.0.0          # IP de bind (0.0.0.0 = todas as interfaces)
SERVER_PORT=5000             # Porta TCP (Railway sobrescreve com PORT)
MAX_CLIENTS=50               # Máximo de clientes simultâneos

# ═══ REDE ════════════════════════════════════════════════════════
BUFFER_SIZE=4096             # Tamanho do buffer de leitura em bytes
SOCKET_TIMEOUT=30            # Timeout do socket em segundos
MAX_MESSAGE_SIZE=65536       # Tamanho máximo de mensagem (64 KB)

# ═══ RECONEXÃO ═══════════════════════════════════════════════════
RECONNECT_ATTEMPTS=5         # Tentativas de reconexão automática
RECONNECT_DELAY=2            # Delay inicial (backoff exponencial: 2s, 4s, 8s...)

# ═══ SEGURANÇA ═══════════════════════════════════════════════════
ENABLE_ENCRYPTION=true       # Ativa/desativa criptografia Fernet
PING_INTERVAL=30             # Intervalo do keep-alive em segundos
PING_TIMEOUT=60              # Timeout para considerar cliente morto

# ═══ LOGGING ═════════════════════════════════════════════════════
LOG_LEVEL=INFO               # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=logs                 # Diretório dos arquivos de log

# ═══ DESENVOLVIMENTO ══════════════════════════════════════════════
DEBUG=false                  # Ativa logs verbose extras
```

### Exemplos de configuração

**Alta disponibilidade** (servidor em produção):
```bash
MAX_CLIENTS=200
SOCKET_TIMEOUT=60
PING_INTERVAL=15
PING_TIMEOUT=45
LOG_LEVEL=WARNING
```

**Desenvolvimento/Debug** (mais verbose):
```bash
MAX_CLIENTS=10
LOG_LEVEL=DEBUG
DEBUG=true
PING_INTERVAL=5
```

**Sem criptografia** (teste de performance):
```bash
ENABLE_ENCRYPTION=false
```

---

## 7. Usando com Docker

### Pré-requisito

Instale o [Docker Desktop](https://docker.com/products/docker-desktop) e o Docker Compose.

### Iniciar apenas o servidor

```bash
# Build e executa o servidor
docker-compose up server

# Em background (detached)
docker-compose up -d server
```

### Ver logs do servidor em tempo real

```bash
docker-compose logs -f server
```

### Conectar cliente ao servidor Docker

Em outro terminal (sem Docker — terminal Python normal):
```bash
python -m src.client.client --host localhost --port 5000 --username Alice
```

> **Por quê sem Docker para o cliente?** Clientes precisam de TTY interativo. É mais simples rodá-los direto no terminal do que via Docker.

### Parar e limpar

```bash
# Para os containers
docker-compose down

# Para e remove volumes
docker-compose down -v
```

### Ver containers em execução

```bash
docker ps
# CONTAINER ID  IMAGE    STATUS         PORTS
# a1b2c3d4e5f6  chat-tcp  Up 5 minutes  0.0.0.0:5000->5000/tcp
```

---

## 8. Rodando os Testes

```bash
# Todos os testes (modo verbose)
pytest tests/ -v

# Com relatório de cobertura
pytest tests/ -v --cov=src --cov-report=term-missing

# Apenas testes de criptografia
pytest tests/test_crypto.py -v

# Apenas testes de protocolo (inclui TCP framing)
pytest tests/test_protocol.py -v

# Apenas testes de integração do servidor
pytest tests/test_server.py -v

# Smoke test end-to-end (inicia servidor real + clientes)
python smoke_test.py
```

### Resultado esperado

```
47 passed in 4.39s

Tests/Cobertura:
  test_crypto.py   - 20 testes   ✅
  test_protocol.py - 13 testes   ✅
  test_server.py   - 14 testes   ✅
  Cobertura: ~75%
```

### Lint de código

```bash
flake8 src/ tests/ --max-line-length=100
```

---

## 9. Solução de Problemas

### Erro: "Address already in use" (porta ocupada)

```bash
# Verificar o que está usando a porta 5000
netstat -ano | findstr :5000   # Windows
lsof -i :5000                  # Linux/macOS

# Mudar a porta no .env
SERVER_PORT=5001
```

### Erro: "Connection refused" (sem servidor)

O servidor não está rodando. Inicie primeiro com `scripts\run_server.bat` ou verifique se está usando o host/porta corretos.

### Erro: "Username já em uso"

Outro cliente já está conectado com esse username. Escolha outro ou aguarde o cliente anterior desconectar.

### Mensagens com caracteres estranhos no Windows

```bash
# Defina o encoding UTF-8 antes de executar
$env:PYTHONIOENCODING="utf-8"
python -m src.client.client
```

### Cliente desconecta imediatamente

Verifique se o servidor está rodando na versão Python compatível (3.11+). Veja os logs do servidor para mensagens de erro.

### Erro: "ModuleNotFoundError: No module named 'src'"

Execute sempre a partir da **raiz do projeto** (a pasta que contém `src/`):

```bash
# CORRETO: na raiz do projeto
cd "g:\Meu Drive\...\Trabalho Fevereiro 2026 - Socket"
python -m src.client.client

# ERRADO: dentro de src/
cd src
python client/client.py  # Erro!
```

### Logs de diagnóstico

Os logs ficam em `logs/server.log` e `logs/client.log` em formato JSON. Para ler:

```bash
# Todas as linhas de erro
cat logs/server.log | python -c "import sys,json; [print(json.loads(l)['message']) for l in sys.stdin if '\"level\": \"ERROR\"' in l]"

# Ou simplesmente:
cat logs/server.log
```

---

## 10. Deploy no Railway (guia completo)

### Pré-requisitos

- Conta no [Railway](https://railway.com) (gratuita)
- Repositório no GitHub com o código

### Passo 1 — Criar conta no Railway

1. Acesse [railway.com](https://railway.com)
2. Clique em **"Sign in"**
3. Escolha **"Continue with GitHub"**
4. Autorize o Railway a acessar seu GitHub
5. Aceite os Termos de Serviço

### Passo 2 — Criar novo projeto

1. No dashboard, clique em **"New Project"**
2. Selecione **"GitHub Repository"**
3. Se necessário, clique em **"Configure GitHub App"** para dar acesso
4. Busque e selecione o repositório **`chat-tcp`**
5. Clique em **"Deploy Now"**

O Railway detecta automaticamente o `railway.json` e `docker/Dockerfile.server`.

### Passo 3 — Aguardar o build

O Railway vai:
1. Clonar o repositório
2. Fazer build da imagem Docker (Dockerfile.server)
3. Iniciar o container
4. Exibir o status como **"Active"** (verde)

Tempo estimado: 2-5 minutos no primeiro deploy.

### Passo 4 — Configurar TCP Proxy (para acesso externo)

Por padrão, Railway expõe apenas HTTP. Para TCP puro:

1. Clique no serviço **"web"** no dashboard
2. Vá em **"Settings"**
3. Role até **"Networking"**
4. Clique em **"Add TCP Proxy"** (ou "TCP Proxy")
5. Informe a porta interna: **`8080`** (Railway injeta PORT=8080 ou similar)
6. Clique em **"Create"**

O Railway vai gerar um endereço como:
```
crossover.proxy.rlwy.net:XXXXX
```

### Passo 5 — Testar a conexão

```bash
# Teste rápido de conectividade
python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('crossover.proxy.rlwy.net', XXXXX)); print('OK'); s.close()"

# Conectar cliente real
python -m src.client.client --host crossover.proxy.rlwy.net --port XXXXX
```

### Passo 6 — Deploy automático

A partir de agora, **qualquer `git push` para `main`** atualiza o servidor automaticamente:

```bash
git add .
git commit -m "feat: nova funcionalidade"
git push origin main
# Railway detecta → rebuild automático → novo deploy
```

### Configurar variáveis de ambiente no Railway

No Railway Dashboard → Seu projeto → Serviço → **"Variables"**:

```
MAX_CLIENTS     = 50
LOG_LEVEL       = INFO
ENABLE_ENCRYPTION = true
```

> **Não é necessário definir PORT** — Railway injeta automaticamente.

---

## Referências Rápidas

| O quê | Comando |
|---|---|
| Servidor local | `python -m src.server.server` |
| Cliente local | `python -m src.client.client` |
| Cliente Railway | `python -m src.client.client --host crossover.proxy.rlwy.net --port 21518` |
| Demo local (janelas) | `scripts\demo.bat` |
| Demo Railway (janelas) | `scripts\demo_railway.bat` |
| Testes | `pytest tests/ -v` |
| Smoke test | `python smoke_test.py` |
| Lint | `flake8 src/ tests/` |
| Docker servidor | `docker-compose up server` |

---

*Para dúvidas técnicas, consulte [docs/ARCHITECTURE.md](ARCHITECTURE.md) ou abra uma [issue no GitHub](https://github.com/smrthiago/chat-tcp/issues).*
