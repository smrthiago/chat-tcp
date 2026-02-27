# Arquitetura do Sistema — Chat TCP/IP

> Documento técnico explicando as decisões de design, escolhas de tecnologia e fundamentos de cada componente do sistema.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Por que TCP e não UDP?](#2-por-que-tcp-e-não-udp)
3. [Protocolo de Comunicação](#3-protocolo-de-comunicação)
4. [Criptografia — Fernet (AES-128)](#4-criptografia--fernet-aes-128)
5. [Integridade — Checksum SHA-256](#5-integridade--checksum-sha-256)
6. [Concorrência — Threads vs Asyncio](#6-concorrência--threads-vs-asyncio)
7. [TCP Framing — O Problema e a Solução](#7-tcp-framing--o-problema-e-a-solução)
8. [Autenticação](#8-autenticação)
9. [Keep-Alive — PING/PONG](#9-keep-alive--pingpong)
10. [Reconexão Automática](#10-reconexão-automática)
11. [Logging Estruturado](#11-logging-estruturado)
12. [Containerização com Docker](#12-containerização-com-docker)
13. [CI/CD com GitHub Actions](#13-cicd-com-github-actions)
14. [Limitações e Trabalhos Futuros](#14-limitações-e-trabalhos-futuros)

---

## 1. Visão Geral

O sistema é uma aplicação **cliente-servidor** de chat em tempo real construída sobre **sockets TCP/IP** puros em Python, sem frameworks de rede de alto nível.

```
┌─────────────┐     TCP     ┌──────────────────────────────────┐
│  Cliente A  │────────────▶│                                  │
│  (Alice)    │◀────────────│          Servidor TCP            │
└─────────────┘             │        (ChatServer)              │
                            │                                  │
┌─────────────┐     TCP     │  ┌────────────────────────────┐  │
│  Cliente B  │────────────▶│  │  Thread por cliente        │  │
│  (Bob)      │◀────────────│  │  handle_client()           │  │
└─────────────┘             │  └────────────────────────────┘  │
                            │                                  │
┌─────────────┐     TCP     │  Lock global: dict de clientes  │
│  Cliente C  │────────────▶│  Broadcast thread-safe          │
│  (Carol)    │◀────────────│                                  │
└─────────────┘             └──────────────────────────────────┘
```

### Fluxo completo de uma mensagem

```
Alice digita → [criptografa com AES-128] → [calcula SHA-256]
  → [encapsula em JSON] → [prefija com 4 bytes de tamanho]
  → TCP stream → Servidor
  → [valida tamanho] → [desencapsula JSON] → [descriptografa]
  → [re-criptografa com chave do Bob] → [envia para Bob]
  → Bob recebe → [descriptografa] → [verifica SHA-256] → exibe
```

---

## 2. Por que TCP e não UDP?

### Características comparadas

| Critério | TCP | UDP |
|---|---|---|
| **Entrega garantida** | ✅ Sim (retransmissão automática) | ❌ Não (melhor-esforço) |
| **Ordem garantida** | ✅ Sim | ❌ Não |
| **Orientado a conexão** | ✅ Sim | ❌ Não (datagrama) |
| **Controle de fluxo** | ✅ Sim | ❌ Não |
| **Overhead** | Maior (cabeçalho 20+ bytes) | Menor (cabeçalho 8 bytes) |
| **Latência** | Ligeiramente maior | Menor |

### Justificativa da escolha: TCP

Para um **sistema de chat**, a **ordem e a entrega** das mensagens são requisitos não-negociáveis:

1. **Ordem importa**: Se Alice manda "Oi" depois "como vai?", Bob precisa ver exatamente nessa ordem. UDP pode inverter.
2. **Entrega importa**: Uma mensagem perdida em UDP é uma mensagem que o receptor nunca viu — inaceitável em chat.
3. **Conexão persistente**: TCP mantém estado de conexão, ideal para sessões de chat longas.
4. **Complexidade**: UDP exigiria implementar manualmente: retransmissão, ordenação por número de sequência, controle de congestionamento — trabalho que o TCP já faz.

> **UDP faz sentido em**: jogos online (onde frames antigos são inúteis), streaming de vídeo/áudio, DNS lookups. Não em chat.

---

## 3. Protocolo de Comunicação

### Por que JSON?

O protocolo usa mensagens em **JSON (JavaScript Object Notation)**:

```json
{
  "version": "1.0",
  "type": "MESSAGE",
  "timestamp": "2026-02-27T15:30:00.000Z",
  "sender": "Alice",
  "recipient": "all",
  "payload": {
    "content": "gAAAAABj8x9K3mR...",
    "encrypted": true,
    "is_dm": false
  },
  "checksum": "a1b2c3d4e5f6..."
}
```

**Vantagens do JSON para este projeto:**
- **Legibilidade**: Fácil de debugar — você consegue ler a mensagem no Wireshark
- **Flexibilidade**: Adicionar novos campos não quebra clientes antigos
- **Universalidade**: Qualquer linguagem parseia JSON facilmente (importante para interoperabilidade)
- **Self-describing**: O campo `type` diz o que é a mensagem sem precisar de documentação extra

**Alternativas e por que não usamos:**
- **Protobuf/MessagePack**: Mais eficiente em bytes, mas requer schema compartilhado e é opaco (difícil para fins didáticos)
- **XML**: Verboso demais, overhead desnecessário
- **Formato binário próprio**: Mais performático mas muito mais complexo de implementar corretamente

### Tipos de Mensagem

| Tipo | Direção | Propósito |
|---|---|---|
| `AUTH` | Cliente → Servidor | Enviada ao conectar: username + chave pública |
| `AUTH` | Servidor → Cliente | Resposta: success/fail + lista de usuários |
| `MESSAGE` | Cliente → Servidor | Mensagem de chat (criptografada) |
| `MESSAGE` | Servidor → Cliente | Mensagem re-criptografada para o destinatário |
| `PING` | Qualquer → Qualquer | Keep-alive: "ainda estou vivo" |
| `PONG` | Qualquer → Qualquer | Resposta ao PING |
| `DISCONNECT` | Cliente → Servidor | Desconexão voluntária e graciosa |
| `USER_LIST` | Bidirecional | Solicita/retorna lista de usuários online |
| `SYSTEM` | Servidor → Clientes | Notificações: usuário entrou/saiu |
| `ERROR` | Servidor → Cliente | Erro com código e mensagem descritiva |

---

## 4. Criptografia — Fernet (AES-128)

### O que é Fernet?

**Fernet** é um esquema de criptografia simétrica da biblioteca `cryptography` do Python que combina:

```
Fernet = AES-128-CBC + HMAC-SHA256 + Timestamp + IV aleatório
```

Cada token Fernet tem a estrutura:

```
┌─────────┬──────────┬────────────────────┬──────────────────────────┐
│ Versão  │Timestamp │  IV (16 bytes)     │  Ciphertext + HMAC       │
│ (1 byte)│ (8 bytes)│  (aleat. por msg)  │  (tamanho variável)      │
└─────────┴──────────┴────────────────────┴──────────────────────────┘
```

### Por que AES-128 e não AES-256?

- **AES-128 é computacionalmente seguro**: Nenhum ataque conhecido mais eficiente que força bruta — que exigiria 2¹²⁸ operações (inviável até 2050+)
- **AES-256 não é "mais seguro na prática"**: Para ataques modernos, ambos são equivalentemente seguros
- **AES-128 é mais rápido**: Menos rounds de encriptação (10 vs 14) — importante em sistemas com muitas mensagens

### Por que modo CBC (Cipher Block Chaining)?

```
Bloco n = Encrypt(Plaintext_n XOR Ciphertext_(n-1))
```

- **Difusão**: Uma mudança em um bloco afeta todos os blocos seguintes
- **Evita padrões**: Mensagens idênticas produzem ciphertexts diferentes (graças ao IV aleatório)
- **Alternativa ECB seria perigosa**: Em ECB, blocos idênticos produzem ciphertext idêntico — revela padrões

### IV (Initialization Vector) aleatório

O Fernet gera um **IV de 16 bytes aleatório para cada mensagem**. Isso garante que:

```
encrypt("Oi") → "gAAAAABj8x9K..."  (mensagem 1)
encrypt("Oi") → "gAAAAABj9Y3M..."  (mensagem 2 — diferente!)
```

Mesmo mensagem, cipher diferente. Isso impede **ataques de análise de frequência**.

### Arquitetura de chaves — Uma chave por cliente

Cada cliente gera sua própria chave Fernet ao iniciar:

```python
# No cliente:
crypto = CryptoManager()           # Gera chave aleatória de 256 bits
key_b64 = crypto.get_key_b64()     # Exporta em base64

# No AUTH: envia a chave ao servidor
make_auth_request(username, key_b64)
```

O servidor re-criptografa cada mensagem com a chave do destinatário:

```
Alice (chave_A) → MSG → Servidor → descriptografa com chave_A
                                 → re-criptografa com chave_B → Bob
```

**Vantagem**: Bob não consegue ler mensagens de Carol (chaves diferentes).

### Limitação conhecida: troca de chave não-segura

```
[!] ATENÇÃO: Limitação educacional

A chave Fernet é enviada em TEXTO CLARO durante o AUTH:
  Cliente → Servidor: {"username": "Alice", "encryption_key": "abc123..."}

Um atacante com acesso à rede pode:
  1. Interceptar o pacote AUTH
  2. Capturar a chave
  3. Descriptografar TODAS as mensagens futuras

Solução em produção: TLS/SSL (camada de transporte) ou
Diffie-Hellman para troca segura de chaves sem nunca transmiti-las.
```

Esta limitação está documentada e é esperada para um projeto educacional.

---

## 5. Integridade — Checksum SHA-256

### Por que checksum além do HMAC do Fernet?

O Fernet já inclui HMAC-SHA256 internamente. O checksum adicional serve para:

1. **Verificar antes de exibir**: Depois de descriptografar, confirmamos que o conteúdo não foi corrompido
2. **Auditoria**: O checksum fica no campo `checksum` da mensagem JSON, visível nos logs
3. **Didático**: Demonstra explicitamente o conceito de integridade de mensagem

### SHA-256 em detalhes

```python
SHA-256("Olá Bob!") → "a8f5f167f44f4964e6c998dee827110c..."  (64 chars hex = 32 bytes)
```

- **Determinístico**: Mesmo input → sempre mesmo output
- **Efeito avalanche**: Mudar 1 bit no input muda ~50% do hash (output completamente diferente)
- **Irreversível**: Impossível recuperar o input a partir do hash
- **Resistente a colisões**: Impossível criar dois inputs diferentes com o mesmo hash

### Comparação em tempo constante

```python
def _constant_time_compare(a: str, b: str) -> bool:
    # Usa hmac.compare_digest — tempo constante mesmo se strings diferentes
    return hmac.compare_digest(a.encode(), b.encode())
```

**Por que tempo constante?** Uma comparação normal `a == b` retorna imediatamente se o primeiro caractere já difere. Um atacante pode medir o tempo de resposta para discovrir caractere a caractere qual é o checksum correto (**timing attack**). `hmac.compare_digest` sempre leva o mesmo tempo independente de onde a diferença está.

---

## 6. Concorrência — Threads vs Asyncio

### O que escolhemos: Threading

```python
# Uma thread por cliente conectado
thread = threading.Thread(
    target=handle_client,
    args=(self, client_socket, address),
    daemon=True,
)
thread.start()
```

### Por que Thread e não Asyncio?

| Aspecto | Threading | Asyncio |
|---|---|---|
| **Legibilidade** | ✅ Código sequencial, fácil de entender | Requer `async/await` em todo lugar |
| **Debugging** | ✅ Stack trace claro | Coroutines mais difíceis de debugar |
| **Didático** | ✅ Modelo "um cliente = uma thread" é intuitivo | Modelo de event loop menos óbvio |
| **Escalabilidade** | ~100-500 clientes (limite de threads do OS) | Dezenas de milhares de conexões |
| **GIL do Python** | Impacto (GIL libera em I/O, ok para sockets) | Contorna o GIL completamente |
| **Contexto** | Trabalho acadêmico | Sistema em produção com alta carga |

**Para este projeto** (demonstração acadêmica, max ~50 clientes), **threading é a escolha correta**. Em um sistema em produção com 10.000 usuários simultâneos, asyncio seria necessário.

### Thread safety — Lock global

O dicionário `server.clients` é acessado por múltiplas threads simultaneamente. Para evitar **race conditions**:

```python
# ERRADO: race condition
for sock, info in server.clients.items():  # RuntimeError se outra thread apaga

# CORRETO: snapshot + lock
with server.lock:
    snapshot = list(server.clients.items())  # Cópia rápida com lock
# Itera fora do lock — seguro
for sock, info in snapshot:
    send_message(sock, msg)
```

O `threading.Lock()` garante que apenas uma thread modifica o dict por vez.

---

## 7. TCP Framing — O Problema e a Solução

### O problema: TCP é um protocolo de STREAM

TCP **não preserva fronteiras de mensagem**. Quando você chama `sock.recv(1024)`, pode receber:
- Menos bytes que a mensagem completa (fragmentação de rede)
- Exatamente uma mensagem
- Múltiplas mensagens concatenadas

```
# Enviamos: [MSG_A: 200 bytes] [MSG_B: 150 bytes]

# recv() pode retornar qualquer um desses cenários:
recv() → b"{"type": "ME..."         # Fragmentado! Só metade da MSG_A
recv() → b'...SSAGE"}{"type":...'   # MSG_A + começo da MSG_B
recv() → b'{"type": "MESSAGE"}{"type": "AUTH"}'  # Duas mensagens juntas!
```

Se usarmos `recv()` ingenuamente, o parser JSON vai **falhar** ou **confundir mensagens**.

### A solução: Length-Prefix Framing

Antes de cada mensagem JSON, enviamos **4 bytes (big-endian)** indicando o tamanho em bytes do payload:

```
┌────────────────────┬────────────────────────────────────────┐
│  4 bytes (uint32)  │         N bytes (JSON UTF-8)           │
│  tamanho = N       │         conteúdo da mensagem           │
└────────────────────┴────────────────────────────────────────┘
```

**Envio:**
```python
def send_message(sock, msg):
    data = msg.to_json().encode("utf-8")
    header = struct.pack(">I", len(data))  # ">I" = big-endian unsigned int 4 bytes
    sock.sendall(header + data)
```

**Recebimento:**
```python
def recv_message(sock):
    header = recv_exactly(sock, 4)           # Lê exatamente 4 bytes
    size = struct.unpack(">I", header)[0]    # Interpreta como uint32
    data = recv_exactly(sock, size)          # Lê exatamente N bytes
    return Message.from_json(data.decode())

def recv_exactly(sock, n):
    """Lê exatamente n bytes — nunca mais, nunca menos."""
    buffer = b""
    while len(buffer) < n:
        chunk = sock.recv(n - len(buffer))
        if not chunk:
            raise ConnectionError("Conexão encerrada")
        buffer += chunk
    return buffer
```

A função `recv_exactly` resolve o problema de fragmentação: ela **continua lendo** até ter exatamente N bytes, independente de quantos `recv()` forem necessários.

---

## 8. Autenticação

### Fluxo de autenticação

```
Cliente                          Servidor
   │                                │
   │── AUTH {username, key} ────────▶│
   │                                │── Valida username (regex, comprimento)
   │                                │── Verifica duplicata (case-insensitive)
   │                                │── Verifica limite de clientes
   │◀── AUTH {status: success} ─────│
   │    {users_online: [...]}        │
   │                                │── Notifica outros: SYSTEM "Alice entrou"
```

### Validação de username

```python
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")

# Regras:
# - 3 a 20 caracteres
# - Apenas letras, números, underscore e hífen
# - Sem espaços, emojis ou caracteres especiais
# - Case-insensitive para verificar duplicatas (Alice == alice == ALICE)
```

### Por que não usar senha?

Este projeto é educacional e foca em **infraestrutura de rede**, não em autenticação de usuário. Em produção, adicionaríamos:
- Hash de senha (bcrypt/argon2)
- Tokens JWT para sessão
- Rate limiting para tentativas de login

---

## 9. Keep-Alive — PING/PONG

### O problema: conexões TCP "fantasmas"

Uma conexão TCP pode parecer ativa mas estar morta:
- Usuário fechou o laptop abruptamente (sem `close()`)
- Queda de rede (cabo desconectado)
- Timeout de NAT/firewall

O servidor continuaria "esperando" mensagens de um cliente que não existe mais.

### A solução: PING/PONG periódico

```
Servidor ──── PING ────▶ Cliente   (a cada PING_INTERVAL segundos)
Servidor ◀─── PONG ──── Cliente   (dentro de PING_TIMEOUT segundos)

Se não receber PONG: fecha conexão e remove cliente
```

**Configuração (.env):**
```
PING_INTERVAL=30    # Envia PING a cada 30 segundos
PING_TIMEOUT=60     # Se não receber PONG em 60s, encerra
```

### No lado do cliente: atualizar timestamp

Qualquer mensagem recebida do cliente (não só PONG) atualiza o `last_ping`:

```python
# Em client_handler.py:
msg = recv_message(client_socket)
client_info.last_ping = datetime.now(timezone.utc)  # Qualquer msg serve como "vivo"
```

---

## 10. Reconexão Automática

### Backoff exponencial

Quando a conexão cai, o cliente não tenta reconectar imediatamente em loop rápido (isso sobrecarregaria o servidor). Usa **backoff exponencial com jitter**:

```
Tentativa 1: aguarda 2s
Tentativa 2: aguarda 4s
Tentativa 3: aguarda 8s
Tentativa 4: aguarda 16s
Tentativa 5: aguarda 32s  (cap de 60s)
```

**Por que exponencial?** Se o servidor cai e volta, 500 clientes não tentam reconectar ao mesmo tempo — eles ficam distribuídos no tempo, evitando o **thundering herd problem** (avalanche de reconexões simultâneas).

**Configuração:**
```
RECONNECT_ATTEMPTS=5   # Máximo de tentativas
RECONNECT_DELAY=2      # Delay inicial em segundos
```

---

## 11. Logging Estruturado

### Dois formatos simultâneos

```python
# Console (humano): fácil de ler durante desenvolvimento
13:45:22 [server] INFO — Cliente autenticado: Alice @ ('127.0.0.1', 52341)

# Arquivo JSON (máquina): fácil de parsear com ferramentas de análise
{"timestamp":"2026-02-27T16:45:22Z","level":"INFO","component":"server",
 "message":"Cliente autenticado","data":{"username":"Alice","address":"127.0.0.1"}}
```

### Por que JSON nos logs?

Em produção, logs JSON permitem:
- **Agregação**: Ferramentas como Elasticsearch, Datadog, Splunk parseiam automaticamente
- **Filtragem**: `jq '.[] | select(.level == "ERROR")'`
- **Análise**: Contar mensagens por usuário, detectar padrões de erro

### Rotação automática

```python
RotatingFileHandler(
    log_path,
    maxBytes=10 * 1024 * 1024,  # Máximo 10 MB por arquivo
    backupCount=5,              # Mantém últimos 5 arquivos
)
# Gera: server.log, server.log.1, server.log.2, ... server.log.5
```

---

## 12. Containerização com Docker

### Por que Docker?

- **Reprodutibilidade**: "Funciona na minha máquina" deixa de ser problema
- **Isolamento**: Dependências Python não conflitam com o sistema
- **Deploy simplificado**: Railway faz deploy a partir do Dockerfile automaticamente
- **Portabilidade**: Qualquer pessoa com Docker pode rodar o servidor identicamente

### Estrutura dos Dockerfiles

```dockerfile
# Multi-stage build não foi usado (simplicidade para fins educacionais)
# Em produção, usaríamos:
FROM python:3.11-slim as builder
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
# Resultado: imagem menor, sem ferramentas de build
```

### Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD nc -z localhost 5000 || exit 1
```

O Docker verifica a cada 30s se a porta 5000 está respondendo. Se falhar 3 vezes seguidas, marca o container como `unhealthy` e o Railway reinicia automaticamente.

---

## 13. CI/CD com GitHub Actions

### Pipeline automatizado

```
git push → GitHub Actions dispara automaticamente
     │
     ├── flake8: verifica estilo e erros óbvios
     │     (max-line-length=100, exclui __pycache__)
     │
     └── pytest: executa 47 testes
           ├── test_crypto.py  (20 testes)
           ├── test_protocol.py (13 testes)
           └── test_server.py  (14 testes)
                 └── coverage ≥ 65%
```

**Integração com Railway**: Após cada push na branch `main`, o Railway detecta automaticamente e faz novo deploy.

---

## 14. Limitações e Trabalhos Futuros

| Limitação | Impacto | Solução em Produção |
|---|---|---|
| Troca de chave em texto claro | Alto (interceptação de chave) | TLS/SSL ou Diffie-Hellman |
| Auth por username apenas | Médio (qualquer um se passa por outro) | Senha + hash bcrypt + JWT |
| Threading (não asyncio) | Baixo (max ~500 clientes) | asyncio para alta escala |
| Sem persistência de mensagens | Médio (histórico perdido) | PostgreSQL/Redis para histórico |
| Sem grupos/canais | Baixo (MVP) | Modelo de canais (como IRC) |
| Sem moderação | Baixo | Roles: admin, moderador, usuário |

---

*Documento gerado para o trabalho de Infraestrutura de Redes — 5º Período de Engenharia de Software.*
