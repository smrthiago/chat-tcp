# 📋 PDR - Plano de Desenvolvimento Rápido
## Sistema de Chat em Tempo Real com Socket TCP/IP

**Projeto:** Sistema Cliente-Servidor de Chat  
**Disciplina:** Infraestrutura de Redes - 5º Período  
**Curso:** Engenharia de Software  
**Prazo:** 5 dias  
**Versão:** Boa (Portfólio)  
**Data de Criação:** 26 de Fevereiro de 2026

---

## 1. VISÃO GERAL

### 1.1 Objetivo do Projeto
Desenvolver um sistema cliente-servidor de comunicação em tempo real utilizando sockets TCP/IP, com arquitetura escalável, criptografia end-to-end, e infraestrutura profissional containerizada.

### 1.2 Escopo da "Versão Boa"
- ✅ Servidor multi-cliente com threading
- ✅ Broadcast de mensagens entre clientes
- ✅ Criptografia Fernet (simétrica)
- ✅ Sistema de autenticação básico
- ✅ Logs estruturados em JSON
- ✅ Docker e Docker Compose
- ✅ Graceful shutdown
- ✅ Reconexão automática
- ✅ Tratamento robusto de erros
- ✅ Documentação completa

### 1.3 Fora do Escopo (para não extrapolar 5 dias)
- ❌ Interface gráfica (GUI)
- ❌ Persistência em banco de dados
- ❌ Criptografia assimétrica (RSA)
- ❌ Sistema de salas/canais
- ❌ Transferência de arquivos
- ❌ WebSockets ou API REST

### 1.4 Proposta de Valor
**Para o usuário final:** Um sistema de chat em tempo real onde múltiplas pessoas podem se conectar e trocar mensagens de forma segura e instantânea.

**Para a avaliação acadêmica:** Demonstração prática de conceitos de redes (TCP/IP, sockets), concorrência (threading), segurança (criptografia) e infraestrutura moderna (Docker).

**Para o portfólio:** Projeto completo com código limpo, documentação profissional e deploy containerizado.

---

## 2. ESPECIFICAÇÕES TÉCNICAS

### 2.1 Stack Tecnológica

**Linguagem:** Python 3.11+

**Bibliotecas Core (Built-in):**
```
socket          # Comunicação TCP/IP
threading       # Concorrência multi-cliente
json            # Serialização de dados
logging         # Sistema de logs
datetime        # Timestamps
argparse        # CLI arguments
signal          # Graceful shutdown
hashlib         # Checksum de mensagens
base64          # Encoding de dados
```

**Bibliotecas Externas (requirements.txt):**
```
cryptography==41.0.7  # Criptografia Fernet (AES-128)
colorama==0.4.6       # Cores no terminal
python-dotenv==1.0.0  # Variáveis de ambiente
```

**Infraestrutura:**
- Docker 24.0+
- Docker Compose 2.20+
- Git 2.40+

### 2.2 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    CAMADA DE REDE                       │
│                     (Internet)                          │
└─────────────────────────────────────────────────────────┘
                            │
                    TCP Socket (5000)
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼────────┐
│  CLIENTE 1     │                    │  CLIENTE 2      │
│  (client.py)   │                    │  (client.py)    │
├────────────────┤                    ├─────────────────┤
│ - UI Handler   │                    │ - UI Handler    │
│ - Send Thread  │                    │ - Send Thread   │
│ - Recv Thread  │                    │ - Recv Thread   │
│ - Encryption   │                    │ - Encryption    │
└────────────────┘                    └─────────────────┘
        │                                       │
        └───────────────────┬───────────────────┘
                            │
                    ┌───────▼────────┐
                    │   SERVIDOR     │
                    │  (server.py)   │
                    ├────────────────┤
                    │ - Socket Pool  │
                    │ - Thread Pool  │
                    │ - Message Bus  │
                    │ - Client Mgr   │
                    │ - Logger       │
                    │ - Crypto       │
                    └────────────────┘
```

### 2.3 Estrutura de Diretórios Completa

```
chat-system/
├── README.md                          # Documentação principal
├── LICENSE                            # Licença MIT
├── .gitignore                         # Arquivos ignorados pelo Git
├── .env.example                       # Template de variáveis de ambiente
├── requirements.txt                   # Dependências Python
├── docker-compose.yml                 # Orquestração de containers
│
├── docs/                              # Documentação técnica
│   ├── ARCHITECTURE.md                # Arquitetura detalhada
│   ├── PROTOCOL.md                    # Especificação do protocolo
│   ├── API.md                         # Documentação da API interna
│   └── images/                        # Diagramas e screenshots
│       ├── architecture-diagram.png
│       ├── sequence-diagram.png
│       └── demo.gif
│
├── src/                               # Código fonte
│   ├── __init__.py
│   │
│   ├── server/                        # Módulo do servidor
│   │   ├── __init__.py
│   │   ├── server.py                  # Servidor principal
│   │   ├── client_handler.py          # Handler de conexões individuais
│   │   ├── message_broker.py          # Sistema de broadcast
│   │   └── auth.py                    # Autenticação de usuários
│   │
│   ├── client/                        # Módulo do cliente
│   │   ├── __init__.py
│   │   ├── client.py                  # Cliente principal
│   │   ├── ui.py                      # Interface CLI
│   │   └── connection_manager.py      # Gerenciamento de reconexão
│   │
│   ├── common/                        # Módulos compartilhados
│   │   ├── __init__.py
│   │   ├── protocol.py                # Protocolo de comunicação
│   │   ├── crypto.py                  # Sistema de criptografia
│   │   ├── logger.py                  # Sistema de logs estruturados
│   │   ├── config.py                  # Configurações centralizadas
│   │   └── exceptions.py              # Exceções customizadas
│   │
│   └── utils/                         # Utilitários
│       ├── __init__.py
│       └── helpers.py                 # Funções auxiliares
│
├── tests/                             # Testes automatizados
│   ├── __init__.py
│   ├── test_server.py                 # Testes do servidor
│   ├── test_client.py                 # Testes do cliente
│   ├── test_protocol.py               # Testes do protocolo
│   ├── test_crypto.py                 # Testes de criptografia
│   └── conftest.py                    # Configurações do pytest
│
├── docker/                            # Arquivos Docker
│   ├── Dockerfile.server              # Container do servidor
│   ├── Dockerfile.client              # Container do cliente
│   └── .dockerignore                  # Arquivos ignorados no build
│
├── scripts/                           # Scripts auxiliares
│   ├── run_server.sh                  # Executa servidor
│   ├── run_client.sh                  # Executa cliente
│   ├── setup.sh                       # Setup inicial do projeto
│   └── test_all.sh                    # Roda todos os testes
│
└── logs/                              # Diretório de logs
    └── .gitkeep                       # Mantém diretório no Git
```

---

## 3. PROTOCOLO DE COMUNICAÇÃO

### 3.1 Formato de Mensagem (JSON)

Todas as mensagens trocadas entre cliente e servidor seguem este formato JSON:

```json
{
  "version": "1.0",
  "type": "MESSAGE|AUTH|PING|PONG|DISCONNECT|USER_LIST|ERROR|SYSTEM",
  "timestamp": "2024-02-26T10:30:15.123456",
  "sender": "username",
  "recipient": "all|username",
  "payload": {
    "content": "mensagem ou dados",
    "metadata": {}
  },
  "checksum": "sha256_hash"
}
```

**Campos obrigatórios:**
- `version`: Versão do protocolo (sempre "1.0")
- `type`: Tipo da mensagem
- `timestamp`: Data/hora ISO 8601
- `payload`: Conteúdo da mensagem

**Campos opcionais:**
- `sender`: Identificação do remetente
- `recipient`: Destinatário (default: "all")
- `checksum`: Hash SHA-256 para validação

### 3.2 Tipos de Mensagem Detalhados

#### AUTH (Autenticação)
Cliente se autentica no servidor com username e chave de criptografia.

```json
{
  "version": "1.0",
  "type": "AUTH",
  "timestamp": "2024-02-26T10:30:15.123456",
  "payload": {
    "username": "joao123",
    "encryption_key": "gAAAAABj8x9K3mR..."
  }
}
```

**Resposta de sucesso:**
```json
{
  "type": "AUTH",
  "payload": {
    "status": "success",
    "message": "Autenticação bem-sucedida",
    "users_online": ["maria456", "pedro789"]
  }
}
```

**Resposta de erro:**
```json
{
  "type": "ERROR",
  "payload": {
    "code": "AUTH_FAILED",
    "message": "Username já em uso"
  }
}
```

#### MESSAGE (Mensagem de Chat)
Mensagem enviada por um usuário para todos ou para usuário específico.

```json
{
  "version": "1.0",
  "type": "MESSAGE",
  "timestamp": "2024-02-26T10:30:22.123456",
  "sender": "joao123",
  "recipient": "all",
  "payload": {
    "content": "Olá pessoal!",
    "encrypted": true
  },
  "checksum": "a1b2c3d4..."
}
```

#### PING / PONG (Keep-Alive)
Mantém conexão ativa e detecta desconexões.

```json
{
  "version": "1.0",
  "type": "PING",
  "timestamp": "2024-02-26T10:30:15.123456"
}
```

```json
{
  "version": "1.0",
  "type": "PONG",
  "timestamp": "2024-02-26T10:30:15.234567"
}
```

#### USER_LIST (Lista de Usuários Online)
Servidor envia lista de usuários conectados.

```json
{
  "type": "USER_LIST",
  "timestamp": "2024-02-26T10:30:15.123456",
  "payload": {
    "users": [
      {
        "username": "joao123",
        "connected_at": "2024-02-26T10:15:00"
      },
      {
        "username": "maria456",
        "connected_at": "2024-02-26T10:20:00"
      }
    ],
    "count": 2
  }
}
```

#### SYSTEM (Mensagem do Sistema)
Notificações automáticas do servidor.

```json
{
  "type": "SYSTEM",
  "timestamp": "2024-02-26T10:30:15.123456",
  "payload": {
    "event": "user_joined|user_left|server_shutdown",
    "message": "maria456 entrou no chat",
    "data": {
      "username": "maria456"
    }
  }
}
```

#### DISCONNECT (Desconexão)
Cliente informa que vai desconectar.

```json
{
  "type": "DISCONNECT",
  "timestamp": "2024-02-26T10:30:15.123456",
  "sender": "joao123",
  "payload": {
    "reason": "user_quit"
  }
}
```

#### ERROR (Erro)
Comunicação de erros.

```json
{
  "type": "ERROR",
  "timestamp": "2024-02-26T10:30:15.123456",
  "payload": {
    "code": "INVALID_MESSAGE|AUTH_FAILED|SERVER_FULL|TIMEOUT",
    "message": "Descrição legível do erro",
    "details": {}
  }
}
```

### 3.3 Fluxo de Conexão Completo

```
CLIENTE                          SERVIDOR
  |                                 |
  |------ TCP Connect ------------->|
  |    (socket.connect)             |
  |                                 |
  |<----- TCP Accept ---------------|
  |    (socket.accept)              |
  |                                 |
  |------ AUTH Request ------------>|
  |  {username, encryption_key}     |
  |                                 |--- Valida username
  |                                 |--- Registra cliente
  |                                 |--- Cria thread handler
  |                                 |
  |<----- AUTH Response ------------|
  |  {success, users_online}        |
  |                                 |
  |<----- SYSTEM BROADCAST ---------|
  |  "Usuario X entrou"             |
  |  (para todos os outros)         |
  |                                 |
  |------ MESSAGE ----------------->|
  |  "Olá pessoal!"                 |
  |                                 |--- Descriptografa
  |                                 |--- Valida checksum
  |                                 |--- Re-criptografa
  |                                 |
  |<----- BROADCAST ----------------|
  |  (para todos os clientes)       |
  |                                 |
  |------ PING -------------------->|
  |  (a cada 30 segundos)           |
  |                                 |
  |<----- PONG ---------------------|
  |  (confirma conexão ativa)       |
  |                                 |
  |------ DISCONNECT -------------->|
  |  {reason: "user_quit"}          |
  |                                 |--- Remove cliente
  |                                 |--- Fecha thread
  |                                 |
  |<----- SYSTEM BROADCAST ---------|
  |  "Usuario X saiu"               |
  |  (para todos os outros)         |
  |                                 |
  |<----- TCP Close ----------------|
  |                                 |
```

### 3.4 Tratamento de Erros no Protocolo

**Timeout de conexão:**
- Cliente não responde PONG após 3 PING: desconexão forçada

**Username duplicado:**
- Retorna erro AUTH_FAILED
- Cliente deve tentar novamente com outro username

**Servidor cheio:**
- Retorna erro SERVER_FULL
- Fecha conexão imediatamente

**Mensagem inválida:**
- Log do erro
- Ignora mensagem (não fecha conexão)
- Retorna ERROR ao cliente

**Checksum inválido:**
- Mensagem corrompida
- Retorna ERROR ao cliente
- Solicita reenvio

---

## 4. ESPECIFICAÇÃO DETALHADA DOS COMPONENTES

### 4.1 SERVIDOR (server.py)

#### Responsabilidades:
1. Aceitar conexões TCP na porta configurada
2. Criar thread dedicada para cada cliente conectado
3. Gerenciar pool de clientes ativos
4. Fazer broadcast de mensagens para todos os clientes
5. Validar e autenticar usuários
6. Manter logs estruturados de todas as ações
7. Implementar shutdown gracioso com SIGINT/SIGTERM

#### Classe Principal:

```python
class ChatServer:
    """
    Servidor TCP multi-cliente para chat em tempo real.
    
    Attributes:
        host (str): Endereço IP do servidor
        port (int): Porta de escuta
        max_clients (int): Número máximo de conexões simultâneas
        clients (dict): Dicionário de clientes conectados {socket: ClientInfo}
        lock (threading.Lock): Lock para operações thread-safe
        running (bool): Flag de controle do servidor
        logger (logging.Logger): Sistema de logs
    """
    
    def __init__(self, host='0.0.0.0', port=5000, max_clients=10):
        """
        Inicializa o servidor.
        
        Args:
            host: Endereço IP para bind
            port: Porta para escuta
            max_clients: Máximo de clientes simultâneos
        """
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.clients = {}  # {socket: ClientInfo}
        self.usernames = set()  # Controle de usernames únicos
        self.lock = threading.Lock()
        self.running = False
        self.server_socket = None
        self.logger = setup_logger('server')
        
    def start(self):
        """
        Inicia o servidor e começa a aceitar conexões.
        
        Raises:
            OSError: Se não conseguir fazer bind na porta
        """
        
    def accept_connections(self):
        """
        Loop principal que aceita novas conexões.
        Cria uma thread para cada cliente conectado.
        """
        
    def handle_client(self, client_socket, address):
        """
        Handler executado em thread separada para cada cliente.
        
        Args:
            client_socket: Socket da conexão do cliente
            address: Tupla (ip, port) do cliente
        """
        
    def authenticate_client(self, client_socket, address):
        """
        Autentica cliente e registra no sistema.
        
        Args:
            client_socket: Socket do cliente
            address: Endereço do cliente
            
        Returns:
            ClientInfo: Objeto com dados do cliente autenticado
            None: Se autenticação falhar
        """
        
    def broadcast(self, message, exclude_socket=None):
        """
        Envia mensagem para todos os clientes conectados.
        
        Args:
            message: Mensagem a ser enviada (dict ou str)
            exclude_socket: Socket a ser excluído do broadcast (opcional)
        """
        
    def send_to_client(self, client_socket, message):
        """
        Envia mensagem para um cliente específico.
        
        Args:
            client_socket: Socket do cliente destinatário
            message: Mensagem a ser enviada
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        
    def remove_client(self, client_socket):
        """
        Remove cliente do pool e fecha conexão.
        
        Args:
            client_socket: Socket do cliente a ser removido
        """
        
    def get_users_list(self):
        """
        Retorna lista de usuários conectados.
        
        Returns:
            list: Lista de usernames
        """
        
    def shutdown(self):
        """
        Encerra servidor graciosamente.
        - Notifica todos os clientes
        - Fecha todas as conexões
        - Libera recursos
        """
```

#### Estrutura ClientInfo:

```python
from dataclasses import dataclass
from datetime import datetime
import socket

@dataclass
class ClientInfo:
    """
    Informações de um cliente conectado.
    
    Attributes:
        socket: Socket TCP da conexão
        address: Tupla (ip, port)
        username: Nome de usuário escolhido
        encryption_key: Chave Fernet para criptografia
        connected_at: Timestamp de conexão
        last_ping: Timestamp do último PING recebido
        thread: Thread handler do cliente
    """
    socket: socket.socket
    address: tuple
    username: str
    encryption_key: bytes
    connected_at: datetime
    last_ping: datetime
    thread: threading.Thread
```

#### Funções Auxiliares:

```python
def setup_signal_handlers(server):
    """
    Configura handlers para SIGINT e SIGTERM.
    Permite shutdown gracioso com CTRL+C.
    """
    
def validate_message(message):
    """
    Valida estrutura e campos de uma mensagem.
    
    Returns:
        bool: True se válida, False caso contrário
    """
```

### 4.2 CLIENTE (client.py)

#### Responsabilidades:
1. Conectar ao servidor via TCP
2. Autenticar com username único
3. Thread separada para envio de mensagens
4. Thread separada para recebimento de mensagens
5. Criptografar mensagens antes de enviar
6. Descriptografar mensagens recebidas
7. Interface CLI amigável e colorida
8. Reconexão automática em caso de queda

#### Classe Principal:

```python
class ChatClient:
    """
    Cliente TCP para chat em tempo real.
    
    Attributes:
        host (str): Endereço do servidor
        port (int): Porta do servidor
        username (str): Nome de usuário
        socket (socket.socket): Socket de conexão
        crypto (CryptoManager): Gerenciador de criptografia
        running (bool): Flag de controle
        logger (logging.Logger): Sistema de logs
    """
    
    def __init__(self, host='localhost', port=5000, username=None):
        """
        Inicializa o cliente.
        
        Args:
            host: Endereço do servidor
            port: Porta do servidor
            username: Nome de usuário (prompt se None)
        """
        self.host = host
        self.port = port
        self.username = username or self._prompt_username()
        self.socket = None
        self.crypto = CryptoManager()
        self.running = False
        self.connected = False
        self.logger = setup_logger('client')
        
    def connect(self):
        """
        Estabelece conexão TCP com o servidor.
        
        Returns:
            bool: True se conectado, False caso contrário
        """
        
    def authenticate(self):
        """
        Envia credenciais de autenticação ao servidor.
        
        Returns:
            bool: True se autenticado, False caso contrário
        """
        
    def start(self):
        """
        Inicia threads de envio e recebimento.
        """
        
    def send_message(self, content):
        """
        Criptografa e envia mensagem ao servidor.
        
        Args:
            content: Conteúdo da mensagem (string)
        """
        
    def receive_loop(self):
        """
        Loop executado em thread separada para receber mensagens.
        Processa e exibe mensagens recebidas do servidor.
        """
        
    def input_loop(self):
        """
        Loop executado em thread separada para input do usuário.
        Captura comandos e mensagens digitadas.
        """
        
    def handle_command(self, command):
        """
        Processa comandos especiais (/quit, /users, etc).
        
        Args:
            command: Comando digitado pelo usuário
        """
        
    def reconnect(self):
        """
        Tenta reconectar ao servidor automaticamente.
        Implementa backoff exponencial.
        
        Returns:
            bool: True se reconectado, False se desistiu
        """
        
    def disconnect(self):
        """
        Desconecta do servidor graciosamente.
        """
```

#### UI Handler (ui.py):

```python
class ChatUI:
    """
    Interface de linha de comando para o chat.
    Gerencia exibição de mensagens e input do usuário.
    """
    
    @staticmethod
    def print_welcome(username):
        """Exibe banner de boas-vindas"""
        
    @staticmethod
    def print_message(sender, content, timestamp=None):
        """
        Exibe mensagem formatada com cores.
        
        Args:
            sender: Nome do remetente
            content: Conteúdo da mensagem
            timestamp: Horário da mensagem (opcional)
        """
        
    @staticmethod
    def print_system(message):
        """Exibe mensagem do sistema"""
        
    @staticmethod
    def print_error(message):
        """Exibe mensagem de erro"""
        
    @staticmethod
    def print_help():
        """Exibe comandos disponíveis"""
```

### 4.3 CRIPTOGRAFIA (crypto.py)

#### Algoritmo: Fernet (AES-128 em modo CBC com HMAC)

Fernet é um sistema de criptografia simétrica que garante:
- Confidencialidade (AES-128-CBC)
- Autenticidade (HMAC-SHA256)
- Não pode ser manipulada ou lida sem a chave

#### Implementação:

```python
from cryptography.fernet import Fernet
import base64

class CryptoManager:
    """
    Gerenciador de criptografia usando Fernet.
    
    Attributes:
        key (bytes): Chave de criptografia
        cipher (Fernet): Instância do cipher
    """
    
    def __init__(self, key=None):
        """
        Inicializa gerenciador de criptografia.
        
        Args:
            key: Chave existente em base64 (gera nova se None)
        """
        if key:
            self.set_key(key)
        else:
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
    
    def get_key(self):
        """
        Retorna chave em formato base64 para transmissão.
        
        Returns:
            str: Chave codificada em base64
        """
        return base64.b64encode(self.key).decode('utf-8')
    
    def set_key(self, key_b64):
        """
        Define chave a partir de string base64.
        
        Args:
            key_b64: Chave em formato base64
        """
        self.key = base64.b64decode(key_b64)
        self.cipher = Fernet(self.key)
    
    def encrypt(self, message: str) -> bytes:
        """
        Criptografa mensagem.
        
        Args:
            message: Texto plano
            
        Returns:
            bytes: Mensagem criptografada
        """
        return self.cipher.encrypt(message.encode('utf-8'))
    
    def decrypt(self, encrypted: bytes) -> str:
        """
        Descriptografa mensagem.
        
        Args:
            encrypted: Dados criptografados
            
        Returns:
            str: Texto plano
            
        Raises:
            InvalidToken: Se mensagem for corrompida ou chave incorreta
        """
        return self.cipher.decrypt(encrypted).decode('utf-8')
    
    @staticmethod
    def generate_checksum(data: str) -> str:
        """
        Gera checksum SHA-256 de dados.
        
        Args:
            data: String para gerar hash
            
        Returns:
            str: Hash hexadecimal
        """
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()
```

#### Fluxo de Criptografia:

```
CLIENTE                              SERVIDOR
  |                                     |
  | 1. Gera chave Fernet aleatória      |
  |                                     |
  | 2. Envia chave no AUTH              |
  |------ {encryption_key} ------------>|
  |                                     |
  |                                     | 3. Armazena chave do cliente
  |                                     |
  | 4. Criptografa mensagem             |
  |    msg = "Olá"                      |
  |    enc = encrypt(msg)               |
  |                                     |
  | 5. Envia criptografado              |
  |------ gAAAAABj8x9K... -------------->|
  |                                     |
  |                                     | 6. Descriptografa com chave do cliente
  |                                     |    msg = decrypt(enc)
  |                                     |
  |                                     | 7. Re-criptografa para outros
  |                                     |    (com chave de cada um)
  |                                     |
  |<----- gAAAAABk9y8L... ---------------|
  |                                     |
  | 8. Descriptografa com sua chave     |
  |    msg = decrypt(enc)               |
```

### 4.4 LOGGING (logger.py)

#### Formato JSON Estruturado

Todos os logs são salvos em formato JSON para facilitar parsing e análise:

```json
{
  "timestamp": "2024-02-26T10:30:15.123456",
  "level": "INFO",
  "component": "server",
  "event": "client_connected",
  "data": {
    "address": "192.168.1.5:12345",
    "username": "joao123"
  }
}
```

#### Implementação:

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatter customizado que gera logs em JSON.
    """
    
    def format(self, record):
        """
        Formata record de log como JSON.
        
        Args:
            record: LogRecord do Python
            
        Returns:
            str: JSON formatado
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'component': record.name,
            'event': record.funcName,
            'message': record.getMessage(),
        }
        
        # Adiciona dados extras se existirem
        if hasattr(record, 'data'):
            log_data['data'] = record.data
            
        return json.dumps(log_data, ensure_ascii=False)

def setup_logger(name):
    """
    Configura logger com handlers para arquivo e console.
    
    Args:
        name: Nome do logger (server, client, etc)
        
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Evita duplicação de handlers
    if logger.handlers:
        return logger
    
    # Handler para arquivo (JSON)
    fh = logging.FileHandler(f'logs/{name}.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(JSONFormatter())
    
    # Handler para console (texto legível)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

#### Eventos Logados:

**Servidor:**
- `server_started`: Servidor iniciou
- `client_connected`: Cliente conectou
- `client_authenticated`: Cliente autenticou com sucesso
- `auth_failed`: Falha na autenticação
- `message_received`: Mensagem recebida
- `message_broadcast`: Mensagem enviada para todos
- `client_disconnected`: Cliente desconectou
- `server_shutdown`: Servidor encerrando

**Cliente:**
- `client_started`: Cliente iniciou
- `connected_to_server`: Conectou ao servidor
- `authentication_sent`: Enviou autenticação
- `message_sent`: Enviou mensagem
- `message_received`: Recebeu mensagem
- `reconnecting`: Tentando reconectar
- `disconnected`: Desconectou

### 4.5 PROTOCOL (protocol.py)

```python
from enum import Enum
from dataclasses import dataclass
import json
from datetime import datetime

class MessageType(Enum):
    """Tipos de mensagem do protocolo"""
    AUTH = "AUTH"
    MESSAGE = "MESSAGE"
    PING = "PING"
    PONG = "PONG"
    DISCONNECT = "DISCONNECT"
    USER_LIST = "USER_LIST"
    SYSTEM = "SYSTEM"
    ERROR = "ERROR"

@dataclass
class Message:
    """
    Representação de uma mensagem do protocolo.
    """
    version: str = "1.0"
    type: MessageType = None
    timestamp: str = None
    sender: str = None
    recipient: str = "all"
    payload: dict = None
    checksum: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        if not self.payload:
            self.payload = {}
    
    def to_json(self) -> str:
        """
        Serializa mensagem para JSON.
        
        Returns:
            str: JSON string
        """
        data = {
            'version': self.version,
            'type': self.type.value if isinstance(self.type, MessageType) else self.type,
            'timestamp': self.timestamp,
            'sender': self.sender,
            'recipient': self.recipient,
            'payload': self.payload,
            'checksum': self.checksum
        }
        return json.dumps(data, ensure_ascii=False)
    
    @classmethod
    def from_json(cls, json_str: str):
        """
        Desserializa mensagem de JSON.
        
        Args:
            json_str: String JSON
            
        Returns:
            Message: Objeto mensagem
        """
        data = json.loads(json_str)
        return cls(
            version=data.get('version'),
            type=MessageType(data.get('type')),
            timestamp=data.get('timestamp'),
            sender=data.get('sender'),
            recipient=data.get('recipient', 'all'),
            payload=data.get('payload', {}),
            checksum=data.get('checksum')
        )
    
    def validate(self) -> bool:
        """
        Valida estrutura da mensagem.
        
        Returns:
            bool: True se válida
        """
        if not self.version or not self.type:
            return False
        if not isinstance(self.payload, dict):
            return False
        return True
```

---

## 5. CONFIGURAÇÕES

### 5.1 Arquivo .env

```env
# ===== CONFIGURAÇÕES DO SERVIDOR =====
SERVER_HOST=0.0.0.0
SERVER_PORT=5000
MAX_CLIENTS=50

# ===== SEGURANÇA =====
ENABLE_ENCRYPTION=true
PING_INTERVAL=30

# ===== REDE =====
BUFFER_SIZE=4096
SOCKET_TIMEOUT=300
RECONNECT_ATTEMPTS=5
RECONNECT_DELAY=2

# ===== LOGGING =====
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# ===== DESENVOLVIMENTO =====
DEBUG=false
```

### 5.2 Arquivo config.py

```python
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    """
    Configurações centralizadas do sistema.
    Carrega valores de variáveis de ambiente com fallback para defaults.
    """
    
    # ===== SERVIDOR =====
    SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
    MAX_CLIENTS = int(os.getenv('MAX_CLIENTS', 50))
    
    # ===== REDE =====
    BUFFER_SIZE = int(os.getenv('BUFFER_SIZE', 4096))
    SOCKET_TIMEOUT = int(os.getenv('SOCKET_TIMEOUT', 300))
    RECONNECT_ATTEMPTS = int(os.getenv('RECONNECT_ATTEMPTS', 5))
    RECONNECT_DELAY = int(os.getenv('RECONNECT_DELAY', 2))
    
    # ===== SEGURANÇA =====
    ENABLE_ENCRYPTION = os.getenv('ENABLE_ENCRYPTION', 'true').lower() == 'true'
    PING_INTERVAL = int(os.getenv('PING_INTERVAL', 30))
    
    # ===== LOGGING =====
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # ===== DESENVOLVIMENTO =====
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """
        Valida configurações críticas.
        
        Raises:
            ValueError: Se configuração inválida
        """
        if cls.SERVER_PORT < 1024 or cls.SERVER_PORT > 65535:
            raise ValueError(f"Porta inválida: {cls.SERVER_PORT}")
        
        if cls.MAX_CLIENTS < 1:
            raise ValueError(f"MAX_CLIENTS deve ser >= 1")
        
        if not os.path.exists(cls.LOG_DIR):
            os.makedirs(cls.LOG_DIR)
```

---

## 6. DOCKER E CONTAINERIZAÇÃO

### 6.1 Dockerfile.server

```dockerfile
# Imagem base
FROM python:3.11-slim

# Metadados
LABEL maintainer="seu-email@example.com"
LABEL description="Servidor TCP de Chat em Tempo Real"

# Define diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements primeiro (cache de layers)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY src/ ./src/
COPY .env.example .env

# Cria diretório de logs com permissões
RUN mkdir -p logs && chmod 755 logs

# Expõe porta do servidor
EXPOSE 5000

# Health check para monitoramento
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD nc -z localhost 5000 || exit 1

# Variáveis de ambiente default
ENV SERVER_HOST=0.0.0.0 \
    SERVER_PORT=5000 \
    LOG_LEVEL=INFO

# Comando de inicialização
CMD ["python", "-m", "src.server.server"]
```

### 6.2 Dockerfile.client

```dockerfile
FROM python:3.11-slim

LABEL maintainer="seu-email@example.com"
LABEL description="Cliente TCP de Chat em Tempo Real"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env.example .env

RUN mkdir -p logs && chmod 755 logs

ENV SERVER_HOST=localhost \
    SERVER_PORT=5000

# Cliente precisa de TTY para input interativo
CMD ["python", "-m", "src.client.client"]
```

### 6.3 docker-compose.yml

```yaml
version: '3.8'

services:
  # ===== SERVIDOR =====
  server:
    build:
      context: .
      dockerfile: docker/Dockerfile.server
    container_name: chat-server
    hostname: chat-server
    ports:
      - "5000:5000"
    environment:
      - SERVER_HOST=0.0.0.0
      - SERVER_PORT=5000
      - MAX_CLIENTS=50
      - LOG_LEVEL=INFO
      - ENABLE_ENCRYPTION=true
    volumes:
      - ./logs:/app/logs
      - ./src:/app/src
    networks:
      - chat-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "nc", "-z", "localhost", "5000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
  
  # ===== CLIENTE (exemplo) =====
  client:
    build:
      context: .
      dockerfile: docker/Dockerfile.client
    container_name: chat-client
    stdin_open: true
    tty: true
    environment:
      - SERVER_HOST=server
      - SERVER_PORT=5000
    depends_on:
      server:
        condition: service_healthy
    networks:
      - chat-network

networks:
  chat-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 6.4 .dockerignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# Git
.git/
.gitignore

# Docker
.dockerignore
docker-compose.yml

# Docs
docs/
README.md

# Tests
tests/
*.pytest_cache

# Outros
.env
*.db
*.sqlite
```

---

## 7. PLANO DE DESENVOLVIMENTO (5 DIAS)

### 📅 DIA 1 - FUNDAÇÃO (6-8 horas)
**Data:** Dia 1/5

#### Objetivos:
- ✅ Setup completo do projeto
- ✅ Estrutura de diretórios criada
- ✅ Servidor básico funcionando
- ✅ Cliente básico funcionando
- ✅ Comunicação simples sem criptografia

#### Checklist Detalhado:

**Manhã (3-4h):**
- [ ] Criar repositório no GitHub
- [ ] Clonar localmente
- [ ] Criar toda estrutura de diretórios
- [ ] Criar requirements.txt
- [ ] Criar .gitignore
- [ ] Criar .env.example
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Commit inicial: "feat: initial project structure"

**Tarde (3-4h):**
- [ ] Implementar `protocol.py` (classe Message, MessageType)
- [ ] Implementar `server.py` versão básica:
  - Socket bind
  - Accept de 1 cliente
  - Receber mensagem
  - Printar no console
  - Enviar resposta
- [ ] Implementar `client.py` versão básica:
  - Socket connect
  - Enviar mensagem
  - Receber resposta
  - Printar no console
- [ ] Testar comunicação local:
  ```bash
  # Terminal 1
  python -m src.server.server
  
  # Terminal 2
  python -m src.client.client
  ```
- [ ] Commit: "feat: basic client-server communication"

**Entregável do Dia:** Cliente e servidor trocando mensagens simples em texto plano.

**Critério de Sucesso:**
```
Terminal Servidor:
[INFO] Servidor iniciado em 0.0.0.0:5000
[INFO] Cliente conectou: ('127.0.0.1', 12345)
[INFO] Mensagem recebida: "Olá servidor"

Terminal Cliente:
[INFO] Conectado ao servidor
Digite mensagem: Olá servidor
[INFO] Resposta: "Mensagem recebida"
```

---

### 📅 DIA 2 - CONCORRÊNCIA E BROADCAST (6-8 horas)
**Data:** Dia 2/5

#### Objetivos:
- ✅ Múltiplos clientes simultâneos
- ✅ Threading no servidor
- ✅ Sistema de broadcast de mensagens
- ✅ Autenticação básica com username

#### Checklist Detalhado:

**Manhã (3-4h):**
- [ ] Refatorar `server.py` para threading:
  - Pool de clientes (dict)
  - Thread por cliente
  - Lock para operações thread-safe
- [ ] Implementar `client_handler.py`:
  - Função handle_client()
  - Loop de recebimento
  - Tratamento de desconexão
- [ ] Implementar autenticação:
  - Cliente envia username
  - Servidor valida (único)
  - Registra no pool
- [ ] Testar com 2 clientes simultâneos
- [ ] Commit: "feat: multi-client support with threading"

**Tarde (3-4h):**
- [ ] Implementar `message_broker.py`:
  - Função broadcast()
  - Lista de destinatários
  - Exclusão de sender
- [ ] Atualizar cliente para receber broadcasts:
  - Thread separada para recebimento
  - Exibir mensagens de outros usuários
- [ ] Implementar `ui.py`:
  - Funções de formatação
  - Cores com colorama
  - Banner de boas-vindas
- [ ] Testar chat room completo:
  - 3 clientes conectados
  - Todos veem mensagens de todos
- [ ] Commit: "feat: broadcast system and chat room"

**Entregável do Dia:** Chat funcional com múltiplos usuários vendo mensagens em tempo real.

**Critério de Sucesso:**
```
Terminal Servidor:
[INFO] João conectou
[INFO] Maria conectou
[INFO] Pedro conectou
[INFO] [João]: Olá pessoal!
[INFO] Broadcast para 2 clientes

Terminal João:
[Sistema] Você entrou como João
[Sistema] Maria entrou no chat
[Sistema] Pedro entrou no chat
[Você]: Olá pessoal!

Terminal Maria:
[Sistema] Você entrou como Maria
[Sistema] Pedro entrou no chat
[João]: Olá pessoal!
```

---

### 📅 DIA 3 - SEGURANÇA E ROBUSTEZ (6-8 horas)
**Data:** Dia 3/5

#### Objetivos:
- ✅ Criptografia Fernet implementada
- ✅ Sistema de logging estruturado
- ✅ Tratamento robusto de erros
- ✅ Graceful shutdown

#### Checklist Detalhado:

**Manhã (3-4h):**
- [ ] Implementar `crypto.py`:
  - Classe CryptoManager
  - Métodos encrypt/decrypt
  - Geração de chaves
- [ ] Integrar criptografia no cliente:
  - Gerar chave na inicialização
  - Enviar chave no AUTH
  - Criptografar mensagens enviadas
  - Descriptografar mensagens recebidas
- [ ] Integrar criptografia no servidor:
  - Armazenar chave de cada cliente
  - Descriptografar mensagens recebidas
  - Re-criptografar para broadcast
- [ ] Testar mensagens criptografadas
- [ ] Commit: "feat: end-to-end encryption with Fernet"

**Tarde (3-4h):**
- [ ] Implementar `logger.py`:
  - Classe JSONFormatter
  - Função setup_logger()
  - Rotação de logs
- [ ] Adicionar logs em servidor:
  - Todas as conexões
  - Todas as mensagens
  - Todos os erros
- [ ] Adicionar logs em cliente:
  - Conexão/desconexão
  - Mensagens enviadas/recebidas
- [ ] Implementar tratamento de erros:
  - Try-catch em todas as operações de rede
  - Validação de mensagens
  - Timeouts
- [ ] Implementar graceful shutdown:
  - Signal handlers (SIGINT, SIGTERM)
  - Notificação para clientes
  - Fechamento de conexões
  - Limpeza de recursos
- [ ] Implementar keep-alive:
  - PING a cada 30s
  - Detecção de timeout
  - Remoção de clientes inativos
- [ ] Commit: "feat: logging, error handling, graceful shutdown"

**Entregável do Dia:** Sistema seguro com criptografia e logging completo.

**Critério de Sucesso:**
```
# Mensagem em texto plano
"Olá servidor"

# Mensagem na rede (criptografada)
gAAAAABj8x9K3mR8NqKKH7vZ5rQ...

# Arquivo de log (logs/server.log)
{"timestamp": "2024-02-26T10:30:15.123", "level": "INFO", ...}

# CTRL+C no servidor
[INFO] Shutdown signal recebido
[INFO] Notificando 3 clientes
[INFO] Encerrando threads
[INFO] Servidor encerrado
```

---

### 📅 DIA 4 - INFRAESTRUTURA E TESTES (6-8 horas)
**Data:** Dia 4/5

#### Objetivos:
- ✅ Docker funcionando completamente
- ✅ Testes unitários implementados
- ✅ Configurações via .env funcionando
- ✅ Scripts de execução criados

#### Checklist Detalhado:

**Manhã (3-4h):**
- [ ] Criar `docker/Dockerfile.server`
- [ ] Criar `docker/Dockerfile.client`
- [ ] Criar `docker-compose.yml`
- [ ] Criar `.dockerignore`
- [ ] Testar build:
  ```bash
  docker-compose build
  ```
- [ ] Testar execução:
  ```bash
  docker-compose up server
  ```
- [ ] Testar cliente conectando ao servidor Docker
- [ ] Commit: "feat: Docker support"

**Tarde (3-4h):**
- [ ] Implementar `config.py`:
  - Carregar .env
  - Validar configurações
- [ ] Atualizar servidor/cliente para usar Config
- [ ] Criar `tests/test_protocol.py`:
  - Test Message serialization
  - Test Message deserialization
  - Test validation
- [ ] Criar `tests/test_crypto.py`:
  - Test encryption
  - Test decryption
  - Test key generation
- [ ] Criar `tests/test_server.py`:
  - Test connection
  - Test authentication
  - Test broadcast
- [ ] Rodar testes:
  ```bash
  pytest tests/ -v
  ```
- [ ] Criar scripts:
  - `scripts/run_server.sh`
  - `scripts/run_client.sh`
  - `scripts/test_all.sh`
  - `scripts/setup.sh`
- [ ] Commit: "feat: tests and configuration system"

**Entregável do Dia:** Sistema totalmente containerizado e com testes.

**Critério de Sucesso:**
```bash
# Docker funciona
$ docker-compose up
[✓] Server container started
[✓] Client can connect

# Testes passam
$ pytest tests/ -v
tests/test_protocol.py::test_message_creation PASSED
tests/test_crypto.py::test_encryption PASSED
tests/test_server.py::test_connection PASSED
======================== 10 passed ======================

# Scripts funcionam
$ ./scripts/run_server.sh
[INFO] Starting server on port 5000...
```

---

### 📅 DIA 5 - DOCUMENTAÇÃO E REFINAMENTO (6-8 horas)
**Data:** Dia 5/5

#### Objetivos:
- ✅ README completo e profissional
- ✅ Documentação técnica escrita
- ✅ Código revisado e comentado
- ✅ Demo gravado

#### Checklist Detalhado:

**Manhã (3-4h):**
- [ ] Escrever `README.md` completo:
  - Badge de status
  - Descrição do projeto
  - Features
  - Arquitetura (com diagrama)
  - Instalação (local e Docker)
  - Uso
  - Exemplos
  - Testes
  - Licença
- [ ] Criar `docs/ARCHITECTURE.md`:
  - Diagrama de componentes
  - Fluxo de dados
  - Decisões arquiteturais
- [ ] Criar `docs/PROTOCOL.md`:
  - Especificação completa
  - Exemplos de mensagens
  - Fluxos de comunicação
- [ ] Criar diagrams:
  - Architecture diagram (draw.io ou Mermaid)
  - Sequence diagram
- [ ] Commit: "docs: complete documentation"

**Tarde (3-4h):**
- [ ] Code review completo:
  - Adicionar docstrings faltantes
  - Melhorar comentários
  - Remover código não usado
  - Verificar PEP 8
- [ ] Refactoring final:
  - Extrair constantes
  - Melhorar nomes
  - Simplificar lógica complexa
- [ ] Gravar demo:
  - Terminal com 3 clientes
  - Mostrar mensagens em tempo real
  - Mostrar logs
  - Mostrar Docker
  - Converter para GIF (30s max)
- [ ] Adicionar demo no README
- [ ] Criar LICENSE (MIT recomendado)
- [ ] Atualizar requirements.txt (freeze)
- [ ] Tag de release:
  ```bash
  git tag -a v1.0.0 -m "Release 1.0.0"
  git push origin v1.0.0
  ```
- [ ] Commit final: "chore: release v1.0.0"

**Entregável do Dia:** Projeto 100% completo e pronto para entrega.

**Critério de Sucesso:**
- [ ] README abre no GitHub e está bonito
- [ ] Diagramas renderizam corretamente
- [ ] Demo GIF é smooth e impressionante
- [ ] Código está limpo e comentado
- [ ] Todos os testes passam
- [ ] Docker sobe sem erros
- [ ] Não há TODOs ou FIXMEs no código

---

## 8. TESTES E VALIDAÇÃO

### 8.1 Estratégia de Testes

#### Pirâmide de Testes:
```
        /\
       /  \      E2E (1-2 testes)
      /____\
     /      \    Integration (5-10 testes)
    /________\
   /          \  Unit (20-30 testes)
  /____________\
```

### 8.2 Casos de Teste Detalhados

#### TESTE 1: Conexão Básica
```python
def test_basic_connection():
    """
    Testa se cliente consegue conectar ao servidor.
    """
    # Arrange
    server = ChatServer(host='localhost', port=5555)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
    time.sleep(1)  # Aguarda servidor iniciar
    
    # Act
    client = ChatClient(host='localhost', port=5555, username='test_user')
    connected = client.connect()
    
    # Assert
    assert connected == True
    assert client.socket is not None
    
    # Cleanup
    client.disconnect()
    server.shutdown()
```

#### TESTE 2: Autenticação
```python
def test_authentication_success():
    """
    Testa autenticação bem-sucedida.
    """
    # Setup server
    server = setup_test_server()
    
    # Client autentica
    client = ChatClient(username='joao123')
    client.connect()
    auth_result = client.authenticate()
    
    assert auth_result == True
    assert client.username in server.usernames
```

#### TESTE 3: Username Duplicado
```python
def test_duplicate_username():
    """
    Testa rejeição de username duplicado.
    """
    server = setup_test_server()
    
    # Primeiro cliente
    client1 = ChatClient(username='joao')
    client1.connect()
    client1.authenticate()
    
    # Segundo cliente com mesmo username
    client2 = ChatClient(username='joao')
    client2.connect()
    auth_result = client2.authenticate()
    
    assert auth_result == False
```

#### TESTE 4: Broadcast de Mensagem
```python
def test_message_broadcast():
    """
    Testa se mensagem é recebida por todos os clientes.
    """
    server = setup_test_server()
    
    # Conecta 3 clientes
    clients = [
        ChatClient(username='alice'),
        ChatClient(username='bob'),
        ChatClient(username='charlie')
    ]
    
    for client in clients:
        client.connect()
        client.authenticate()
    
    # Alice envia mensagem
    clients[0].send_message("Hello everyone!")
    
    time.sleep(0.5)  # Aguarda propagação
    
    # Bob e Charlie devem receber
    assert "Hello everyone!" in clients[1].received_messages
    assert "Hello everyone!" in clients[2].received_messages
    assert "Hello everyone!" not in clients[0].received_messages  # Alice não recebe própria msg
```

#### TESTE 5: Criptografia
```python
def test_encryption_decryption():
    """
    Testa criptografia e descriptografia.
    """
    crypto = CryptoManager()
    
    original = "Mensagem secreta"
    encrypted = crypto.encrypt(original)
    decrypted = crypto.decrypt(encrypted)
    
    assert encrypted != original.encode()  # Está criptografado
    assert decrypted == original  # Descriptografa corretamente
```

#### TESTE 6: Múltiplos Clientes Simultâneos
```python
def test_multiple_clients():
    """
    Testa servidor com 10 clientes simultâneos.
    """
    server = setup_test_server()
    
    clients = []
    for i in range(10):
        client = ChatClient(username=f'user{i}')
        client.connect()
        client.authenticate()
        clients.append(client)
    
    # Todos conectados
    assert len(server.clients) == 10
    
    # Cleanup
    for client in clients:
        client.disconnect()
```

#### TESTE 7: Reconexão Automática
```python
def test_automatic_reconnection():
    """
    Testa reconexão automática do cliente.
    """
    server = setup_test_server()
    client = ChatClient(username='reconnect_test')
    client.connect()
    
    # Simula queda de conexão
    server.shutdown()
    
    # Cliente deve tentar reconectar
    time.sleep(2)
    
    # Reinicia servidor
    server = setup_test_server()
    
    # Cliente deve reconectar
    time.sleep(3)
    assert client.connected == True
```

#### TESTE 8: Shutdown Gracioso
```python
def test_graceful_shutdown():
    """
    Testa encerramento gracioso do servidor.
    """
    server = setup_test_server()
    
    clients = [ChatClient(username=f'user{i}') for i in range(3)]
    for client in clients:
        client.connect()
        client.authenticate()
    
    # Envia SIGINT
    server.shutdown()
    
    # Verifica se todos os clientes foram notificados
    for client in clients:
        assert client.received_disconnect_notification == True
        assert client.connected == False
```

#### TESTE 9: Validação de Mensagens
```python
def test_message_validation():
    """
    Testa validação de mensagens malformadas.
    """
    # Mensagem válida
    valid_msg = Message(
        type=MessageType.MESSAGE,
        sender='alice',
        payload={'content': 'Hello'}
    )
    assert valid_msg.validate() == True
    
    # Mensagem sem type
    invalid_msg = Message(
        sender='alice',
        payload={'content': 'Hello'}
    )
    assert invalid_msg.validate() == False
```

#### TESTE 10: Keep-Alive (PING/PONG)
```python
def test_keepalive():
    """
    Testa sistema de keep-alive.
    """
    server = setup_test_server()
    client = ChatClient(username='ping_test')
    client.connect()
    client.authenticate()
    
    # Aguarda PING
    time.sleep(31)  # PING_INTERVAL = 30s
    
    # Verifica se cliente ainda está conectado
    assert client.connected == True
    assert client.last_pong_time is not None
```

### 8.3 Executando Testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas testes de servidor
pytest tests/test_server.py -v

# Com coverage
pytest tests/ --cov=src --cov-report=html

# Testes em modo watch (desenvolvimento)
pytest-watch tests/

# Testes com marcadores
pytest -m "not slow" tests/
```

### 8.4 Métricas de Sucesso

**Performance:**
- ✅ 10+ clientes simultâneos sem degradação
- ✅ Latência < 100ms em rede local
- ✅ Latência < 500ms em internet (mesma região)
- ✅ Throughput: 100+ mensagens/segundo

**Confiabilidade:**
- ✅ 0 mensagens perdidas em operação normal
- ✅ 0 crashes com tratamento de erro adequado
- ✅ Reconexão automática funciona em 90%+ dos casos
- ✅ Graceful shutdown sempre funciona

**Qualidade:**
- ✅ Code coverage > 70%
- ✅ Todos os testes unitários passam
- ✅ Logs estruturados e legíveis
- ✅ Docker build e run sem erros
- ✅ PEP 8 compliance > 90%

---

## 9. DOCUMENTAÇÃO NECESSÁRIA

### 9.1 README.md (Template Completo)

```markdown
# 🚀 Sistema de Chat TCP/IP com Criptografia

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

Sistema cliente-servidor de chat em tempo real utilizando sockets TCP/IP, com criptografia end-to-end e arquitetura containerizada.

![Demo](docs/images/demo.gif)

## 📖 Sobre o Projeto

Este projeto foi desenvolvido para a disciplina de **Infraestrutura de Redes** do curso de Engenharia de Software. Implementa um sistema completo de comunicação cliente-servidor demonstrando conceitos fundamentais de:

- 🔌 Programação com Sockets (TCP/IP)
- 🧵 Concorrência e Threading
- 🔐 Criptografia End-to-End (Fernet/AES-128)
- 🐳 Containerização com Docker
- 📊 Logging Estruturado
- 🛡️ Tratamento Robusto de Erros

## ✨ Features

### Funcionalidades Principais
- ✅ Chat em tempo real com múltiplos usuários
- ✅ Mensagens criptografadas (Fernet/AES-128)
- ✅ Autenticação por username
- ✅ Broadcast de mensagens
- ✅ Reconexão automática
- ✅ Keep-alive (detecção de desconexão)
- ✅ Graceful shutdown
- ✅ Logs estruturados em JSON

### Infraestrutura
- ✅ Containerizado com Docker
- ✅ Docker Compose para orquestração
- ✅ Health checks
- ✅ Configuração via variáveis de ambiente
- ✅ Testes automatizados

## 🏗️ Arquitetura

[Inserir diagrama de arquitetura aqui]

O sistema utiliza arquitetura cliente-servidor com comunicação TCP/IP. O servidor gerencia múltiplas conexões simultâneas usando threading, enquanto cada cliente mantém threads separadas para envio e recebimento de mensagens.

Para detalhes completos, veja [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🚀 Como Usar

### Pré-requisitos

- Python 3.11+
- Docker e Docker Compose (opcional)
- Git

### Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/chat-system.git
cd chat-system
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite .env conforme necessário
```

4. Inicie o servidor:
```bash
python -m src.server.server
```

5. Em outro terminal, inicie o cliente:
```bash
python -m src.client.client
```

### Usando Docker 🐳

1. Build das imagens:
```bash
docker-compose build
```

2. Inicie o servidor:
```bash
docker-compose up server
```

3. Em outro terminal, inicie um cliente:
```bash
docker-compose run client
```

## 📡 Protocolo de Comunicação

O sistema utiliza um protocolo JSON customizado. Exemplo de mensagem:

```json
{
  "version": "1.0",
  "type": "MESSAGE",
  "timestamp": "2024-02-26T10:30:15.123456",
  "sender": "joao123",
  "recipient": "all",
  "payload": {
    "content": "Olá pessoal!",
    "encrypted": true
  }
}
```

Para especificação completa, veja [PROTOCOL.md](docs/PROTOCOL.md).

## 🔐 Segurança

- **Criptografia**: Fernet (AES-128 em modo CBC com HMAC)
- **Chaves**: Geradas aleatoriamente por cliente
- **Integridade**: Checksum SHA-256 em cada mensagem
- **Autenticação**: Username único por conexão

⚠️ **Nota**: Este é um projeto educacional. Para uso em produção, considere implementar TLS/SSL e autenticação mais robusta.

## 🧪 Testes

Execute os testes com:

```bash
# Todos os testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=src --cov-report=html
```

## 📊 Performance

Testado com:
- ✅ 50+ clientes simultâneos
- ✅ Latência < 100ms (rede local)
- ✅ Throughput: 100+ mensagens/segundo
- ✅ 0 mensagens perdidas em operação normal

## 📁 Estrutura do Projeto

```
chat-system/
├── src/
│   ├── server/          # Módulo do servidor
│   ├── client/          # Módulo do cliente
│   └── common/          # Código compartilhado
├── tests/               # Testes automatizados
├── docs/                # Documentação técnica
├── docker/              # Arquivos Docker
└── scripts/             # Scripts auxiliares
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Add nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**[Seu Nome]**
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Perfil](https://linkedin.com/in/seu-perfil)
- Email: seu-email@example.com

## 🙏 Agradecimentos

- Professor [Nome] pela orientação
- Documentação Python para referências de socket
- Biblioteca Cryptography pelos exemplos
- Comunidade open source

---

⭐ Se este projeto te ajudou, considere dar uma estrela!
```

### 9.2 ARCHITECTURE.md (Estrutura)

```markdown
# Arquitetura do Sistema

## Visão Geral
[Diagrama de alto nível]

## Componentes

### 1. Servidor
[Descrição detalhada]

### 2. Cliente
[Descrição detalhada]

### 3. Protocolo
[Descrição detalhada]

## Fluxo de Dados
[Sequência de comunicação]

## Decisões Arquiteturais

### Por que TCP e não UDP?
[Explicação]

### Por que Threading e não Asyncio?
[Explicação]

### Por que Fernet e não RSA?
[Explicação]

## Escalabilidade
[Limitações e melhorias]

## Segurança
[Considerações e riscos]
```

### 9.3 PROTOCOL.md (Estrutura)

```markdown
# Especificação do Protocolo

## Formato de Mensagem
[JSON schema]

## Tipos de Mensagem
[Todos os tipos com exemplos]

## Fluxos
[Diagramas de sequência]

## Códigos de Erro
[Tabela de erros]

## Versionamento
[Como lidar com versões]
```

---

## 10. CHECKLIST FINAL DE ENTREGA

### ✅ Código Funcional

- [ ] Servidor aceita múltiplos clientes
- [ ] Broadcast de mensagens funciona
- [ ] Criptografia implementada e testada
- [ ] Autenticação por username
- [ ] Logs estruturados gerados
- [ ] Graceful shutdown funciona
- [ ] Reconexão automática funciona
- [ ] Tratamento de erros robusto
- [ ] Código está limpo e comentado
- [ ] Segue PEP 8 (verificado com pylint/black)

### ✅ Infraestrutura

- [ ] Docker builds sem erros
- [ ] docker-compose up funciona
- [ ] Health checks configurados
- [ ] Variáveis de ambiente funcionando
- [ ] Scripts de execução criados e testados
- [ ] .dockerignore configurado
- [ ] .gitignore configurado

### ✅ Testes

- [ ] Testes unitários escritos (10+ testes)
- [ ] Testes de integração escritos (5+ testes)
- [ ] Todos os testes passam
- [ ] Coverage > 70%
- [ ] Testes documentados

### ✅ Documentação

- [ ] README.md completo e profissional
- [ ] ARCHITECTURE.md escrito
- [ ] PROTOCOL.md escrito
- [ ] Código tem docstrings
- [ ] Diagramas criados e renderizam
- [ ] Demo GIF/vídeo criado
- [ ] LICENSE adicionada

### ✅ GitHub

- [ ] Repositório público criado
- [ ] Nome descritivo e profissional
- [ ] Description e topics configurados
- [ ] README renderiza bem na página
- [ ] Commits são semânticos e claros
- [ ] Branches organizadas (se aplicável)
- [ ] Tags de versão (v1.0.0)
- [ ] Issues/Projects (opcional mas bom)

### ✅ Apresentação

- [ ] Slides preparados (se necessário)
- [ ] Demo funciona perfeitamente
- [ ] Consigo explicar arquitetura
- [ ] Consigo explicar decisões técnicas
- [ ] Consigo rodar ao vivo sem problemas

---

## 11. CRITÉRIOS DE AVALIAÇÃO ESPERADOS

### Funcionalidade (30 pontos)
- **25-30pts:** Tudo funciona perfeitamente, múltiplos clientes, mensagens chegam
- **20-24pts:** Funciona com pequenos bugs
- **15-19pts:** Funciona parcialmente
- **10-14pts:** Funcionalidade básica apenas
- **0-9pts:** Não funciona adequadamente

### Infraestrutura (25 pontos)
- **22-25pts:** Docker + logs + tratamento de erros + extras
- **18-21pts:** Docker funciona, logs básicos
- **14-17pts:** Apenas configuração manual, sem Docker
- **10-13pts:** Difícil de executar
- **0-9pts:** Não roda facilmente

### Segurança (20 pontos)
- **18-20pts:** Criptografia + validações + checksum
- **14-17pts:** Criptografia funcional
- **10-13pts:** Tentativa de criptografia
- **5-9pts:** Menção a segurança mas não implementado
- **0-4pts:** Nenhuma consideração de segurança

### Qualidade do Código (15 pontos)
- **14-15pts:** Código limpo, comentado, PEP 8, modular
- **11-13pts:** Código organizado e legível
- **8-10pts:** Código funcional mas desorganizado
- **5-7pts:** Código difícil de entender
- **0-4pts:** Código muito confuso

### Documentação (10 pontos)
- **9-10pts:** README completo + docs técnicos + diagramas
- **7-8pts:** README bom com instruções claras
- **5-6pts:** README básico
- **3-4pts:** Documentação mínima
- **0-2pts:** Sem documentação adequada

**TOTAL: 100 pontos**

---

## 12. RECURSOS E REFERÊNCIAS

### 📚 Documentação Oficial

**Python:**
- [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
- [Threading Documentation](https://docs.python.org/3/library/threading.html)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)

**Criptografia:**
- [Cryptography Library](https://cryptography.io/en/latest/)
- [Fernet Specification](https://github.com/fernet/spec/)

**Docker:**
- [Docker Python Guide](https://docs.docker.com/language/python/)
- [Docker Compose](https://docs.docker.com/compose/)

### 📖 Tutoriais Recomendados

- **Real Python - Socket Programming**: Excelente tutorial passo-a-passo
- **Beej's Guide to Network Programming**: Referência clássica (C, mas conceitos aplicam)
- **PyCon Talks sobre Networking**: Vídeos educativos

### 🔗 RFCs Relevantes

- **RFC 793**: Transmission Control Protocol (TCP)
- **RFC 1122**: Requirements for Internet Hosts
- **RFC 5246**: TLS 1.2 (referência sobre criptografia)

### 💻 Repositórios de Referência

Procure no GitHub por:
- `python tcp chat`
- `socket programming python`
- `encrypted chat python`

**Bons exemplos:**
- twisted/twisted
- zeromq/pyzmq
- pallets/flask (para ver bom código Python)

### 🎥 Vídeos Educativos

- "Socket Programming in Python" - Tech With Tim
- "Build a Chat Application" - Corey Schafer
- "Understanding TCP/IP" - Hussein Nasser

### 🛠️ Ferramentas Úteis

**Desenvolvimento:**
- VS Code / PyCharm
- Git / GitHub Desktop
- Postman (para testar APIs se evoluir)

**Testing:**
- pytest
- pytest-cov
- pytest-watch

**Qualidade:**
- pylint
- black (formatador)
- mypy (type checking)

**Monitoramento:**
- netcat (nc)
- tcpdump / Wireshark (analisar pacotes)
- htop (monitorar processos)

**Diagramas:**
- draw.io
- Mermaid
- PlantUML

---

## 13. DICAS IMPORTANTES

### 💡 Para o Desenvolvimento

1. **Comece simples**: Faça funcionar antes de adicionar features
2. **Teste constantemente**: Não acumule código sem testar
3. **Commit frequente**: Histórico detalhado é valioso
4. **Documente durante**: Não deixe docs para o final
5. **Peça ajuda**: Comunidade, colegas, professor

### 🎯 Para a Apresentação

1. **Prepare demo ensaiado**: Murphy's Law - se pode dar errado, vai dar
2. **Tenha backup**: Screenshot, vídeo gravado
3. **Explique decisões**: "Por que escolhi X em vez de Y?"
4. **Mostre o processo**: Logs, commits, evolução
5. **Seja honesto**: "Limitações conhecidas" é melhor que "funciona tudo"

### 🚨 Armadilhas Comuns

1. **Port já em uso**: Sempre check se a porta está livre
2. **Encoding issues**: UTF-8 everywhere
3. **Thread safety**: Use locks quando necessário
4. **Buffer overflow**: Defina BUFFER_SIZE adequado
5. **Zombie threads**: Sempre faça cleanup
6. **Docker networking**: localhost != server no docker

### ✨ Para se Destacar

1. **Add-ons impressionantes**:
   - Wireshark capture mostrando criptografia
   - Métricas de performance
   - Load test com 100 clientes
   - CI/CD com GitHub Actions

2. **Documentação extra**:
   - Video tour do código
   - Blog post explicando o projeto
   - Apresentação no LinkedIn

3. **Código exemplar**:
   - Type hints em tudo
   - Docstrings completas
   - Testes com > 90% coverage
   - Zero warnings do pylint

---

## 14. CONTATO E SUPORTE

### 🆘 Se Precisar de Ajuda

**Durante o desenvolvimento:**
- Stack Overflow (tag: [python] [socket])
- Reddit: r/learnpython
- Discord: Python Community

**Problemas específicos:**
- Cryptography: GitHub Issues
- Docker: Docker Community Forums
- Networking: Network Engineering Stack Exchange

### 📝 Relatando Problemas

Se encontrar bugs ou problemas:
1. Verifique se não é problema conhecido (Issues)
2. Crie Issue detalhada com:
   - Descrição do problema
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Logs relevantes
   - Sistema operacional e versão Python

---

## 15. PRÓXIMOS PASSOS (PÓS-ENTREGA)

Depois de entregar o projeto, considere:

### Melhorias Futuras

**V2.0 - Features Avançadas:**
- [ ] Interface gráfica (Tkinter/PyQt)
- [ ] Salas de chat (canais)
- [ ] Mensagens privadas (DM)
- [ ] Histórico de mensagens (banco de dados)
- [ ] Transferência de arquivos
- [ ] Emojis e reações
- [ ] Status (online/offline/ausente)

**V2.1 - Segurança Avançada:**
- [ ] TLS/SSL
- [ ] Criptografia assimétrica (RSA)
- [ ] Autenticação com senha (hashing bcrypt)
- [ ] Rate limiting
- [ ] Proteção contra DOS

**V2.2 - Escalabilidade:**
- [ ] Redis para mensagens
- [ ] Load balancer
- [ ] Kubernetes deployment
- [ ] Microservices architecture

### Portfólio

- Adicione no LinkedIn
- Escreva artigo no Medium/Dev.to
- Faça fork e continue desenvolvendo
- Use como base para outros projetos

---

## APÊNDICE A: Comandos Úteis

```bash
# Git
git init
git add .
git commit -m "feat: initial commit"
git remote add origin <url>
git push -u origin main

# Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip freeze > requirements.txt

# Docker
docker build -t chat-server .
docker run -p 5000:5000 chat-server
docker-compose up
docker-compose down
docker-compose logs -f server

# Testing
pytest tests/ -v
pytest tests/ --cov=src
pytest tests/ -k "test_server"
pytest-watch tests/

# Code Quality
pylint src/
black src/
mypy src/

# Networking
netstat -tulpn | grep 5000
lsof -i :5000
tcpdump -i lo port 5000
```

---

## APÊNDICE B: Troubleshooting

**Problema:** "Address already in use"
```python
# Adicione no servidor
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

**Problema:** "Broken pipe"
```python
# Sempre trate excepções de socket
try:
    socket.send(data)
except BrokenPipeError:
    # Cliente desconectou
    handle_disconnect()
```

**Problema:** Docker não conecta
```yaml
# Use nome do serviço, não localhost
environment:
  - SERVER_HOST=server  # não localhost
```

**Problema:** UTF-8 encoding errors
```python
# Sempre especifique encoding
message.encode('utf-8')
data.decode('utf-8')
```

---

**FIM DO PDR**

---

**IMPORTANTE:** Este documento é um guia vivo. Ajuste conforme necessário durante o desenvolvimento, mas mantenha o escopo controlado para garantir entrega em 5 dias. Foco na qualidade, não na quantidade de features.

Boa sorte no desenvolvimento! 🚀
