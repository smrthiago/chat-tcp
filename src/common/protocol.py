"""
Protocolo de comunicação do sistema de chat TCP.

## Por que precisamos de framing?

TCP é um protocolo de *stream* — não de *mensagens*. Isso significa que:
  - Uma mensagem de 6.000 bytes pode chegar em 2 chamadas recv()
  - Duas mensagens pequenas podem chegar "coladas" na mesma chamada recv()

Solução: LENGTH-PREFIX FRAMING
  - Cada mensagem é precedida por 4 bytes (big-endian) com seu comprimento
  - O receptor lê os 4 bytes → sabe exatamente quantos bytes ler a seguir
  - Garante entrega de mensagens completas e atômicas

Formato no fio (wire format):
  ┌──────────────────┬─────────────────────────────────────┐
  │  4 bytes (uint32) │  N bytes (JSON UTF-8)               │
  │  comprimento N    │  conteúdo da mensagem               │
  └──────────────────┴─────────────────────────────────────┘
"""
import json
import struct
import socket as _socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from src.common.config import Config
from src.common.exceptions import MessageTooLargeError, ProtocolError


# ── Tipos de mensagem ────────────────────────────────────────────────────────

class MessageType(str, Enum):
    """
    Tipos de mensagem do protocolo v1.0.

    Herda de str para que json.dumps() serialize corretamente sem precisar
    de um encoder customizado.
    """
    AUTH = "AUTH"
    MESSAGE = "MESSAGE"
    PING = "PING"
    PONG = "PONG"
    DISCONNECT = "DISCONNECT"
    USER_LIST = "USER_LIST"
    SYSTEM = "SYSTEM"
    ERROR = "ERROR"


# ── Estrutura de mensagem ────────────────────────────────────────────────────

@dataclass
class Message:
    """
    Representação de uma mensagem do protocolo.

    Attributes:
        version:   Versão do protocolo (sempre "1.0")
        type:      Tipo da mensagem (MessageType)
        timestamp: ISO 8601 UTC gerado automaticamente
        sender:    Username do remetente (None em mensagens do sistema)
        recipient: Destinatário ("all" ou username específico)
        payload:   Dados da mensagem (dict livre)
        checksum:  SHA-256 do conteúdo (opcional, para integridade)
    """
    type: MessageType
    payload: dict = field(default_factory=dict)
    sender: Optional[str] = None
    recipient: str = "all"
    checksum: Optional[str] = None
    version: str = Config.PROTOCOL_VERSION
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_json(self) -> str:
        """Serializa a mensagem para uma string JSON."""
        data = {
            "version": self.version,
            "type": self.type.value if isinstance(self.type, MessageType) else self.type,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "checksum": self.checksum,
        }
        return json.dumps(data, ensure_ascii=False)

    def to_bytes(self) -> bytes:
        """Serializa a mensagem para bytes UTF-8."""
        return self.to_json().encode("utf-8")

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """
        Desserializa mensagem a partir de string JSON.

        Args:
            json_str: String JSON da mensagem.

        Returns:
            Message: Objeto mensagem populado.

        Raises:
            ProtocolError: Se o JSON for inválido ou campos obrigatórios ausentes.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ProtocolError(f"JSON inválido: {e}") from e

        try:
            msg_type = MessageType(data["type"])
        except (KeyError, ValueError) as e:
            raise ProtocolError(f"Campo 'type' ausente ou inválido: {e}") from e

        return cls(
            version=data.get("version", Config.PROTOCOL_VERSION),
            type=msg_type,
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            sender=data.get("sender"),
            recipient=data.get("recipient", "all"),
            payload=data.get("payload", {}),
            checksum=data.get("checksum"),
        )

    def validate(self) -> bool:
        """
        Valida estrutura básica da mensagem.

        Returns:
            bool: True se a mensagem é válida.
        """
        if not self.type or not self.version:
            return False
        if not isinstance(self.payload, dict):
            return False
        return True


# ── Funções de transporte (TCP framing) ─────────────────────────────────────

def recv_exactly(sock: _socket.socket, n: int) -> bytes:
    """
    Lê exatamente `n` bytes do socket, bloqueando até completar.

    TCP pode fragmentar dados — essa função garante que o número
    correto de bytes seja lido antes de retornar.

    Args:
        sock: Socket TCP conectado.
        n:    Número exato de bytes a ler.

    Returns:
        bytes: Exatamente `n` bytes lidos.

    Raises:
        ConnectionError: Se o socket fechar antes de `n` bytes chegarem.
    """
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Conexão encerrada pelo par remoto")
        data += chunk
    return data


def send_message(sock: _socket.socket, message: Message) -> None:
    """
    Envia uma mensagem pelo socket com length-prefix framing.

    Wire format: [4 bytes big-endian uint32 = comprimento] + [N bytes JSON]

    Args:
        sock:    Socket TCP conectado.
        message: Objeto Message a ser enviado.

    Raises:
        MessageTooLargeError: Se a mensagem exceder MAX_MESSAGE_SIZE.
        OSError: Se o envio falhar (socket fechado, rede indisponível).
    """
    raw = message.to_bytes()
    size = len(raw)

    if size > Config.MAX_MESSAGE_SIZE:
        raise MessageTooLargeError(size, Config.MAX_MESSAGE_SIZE)

    # Prefixo de 4 bytes com o tamanho da payload
    header = struct.pack(">I", size)
    sock.sendall(header + raw)


def recv_message(sock: _socket.socket) -> Message:
    """
    Recebe uma mensagem completa do socket usando length-prefix framing.

    Lê os 4 bytes de cabeçalho para descobrir o comprimento, depois
    lê exatamente esse número de bytes para montar a mensagem.

    Args:
        sock: Socket TCP conectado.

    Returns:
        Message: Objeto mensagem desserializado.

    Raises:
        ConnectionError:    Se o socket fechar durante a leitura.
        MessageTooLargeError: Se o tamanho anunciado exceder MAX_MESSAGE_SIZE.
        ProtocolError:      Se o JSON for inválido.
    """
    # Lê os 4 bytes do cabeçalho de comprimento
    raw_header = recv_exactly(sock, 4)
    (msg_size,) = struct.unpack(">I", raw_header)

    if msg_size > Config.MAX_MESSAGE_SIZE:
        raise MessageTooLargeError(msg_size, Config.MAX_MESSAGE_SIZE)

    # Lê exatamente msg_size bytes
    raw_body = recv_exactly(sock, msg_size)
    return Message.from_json(raw_body.decode("utf-8"))


# ── Factories de mensagens comuns ────────────────────────────────────────────

def make_auth_request(username: str, encryption_key: str) -> Message:
    """Cria mensagem de solicitação de autenticação."""
    return Message(
        type=MessageType.AUTH,
        payload={"username": username, "encryption_key": encryption_key},
    )


def make_auth_success(users_online: list) -> Message:
    """Cria mensagem de autenticação bem-sucedida."""
    return Message(
        type=MessageType.AUTH,
        payload={"status": "success", "users_online": users_online},
    )


def make_auth_error(reason: str) -> Message:
    """Cria mensagem de falha na autenticação."""
    return Message(
        type=MessageType.ERROR,
        payload={"code": "AUTH_FAILED", "message": reason},
    )


def make_chat_message(sender: str, content: str,
                      encrypted_content: str, recipient: str = "all",
                      checksum: str = None) -> Message:
    """Cria mensagem de chat."""
    return Message(
        type=MessageType.MESSAGE,
        sender=sender,
        recipient=recipient,
        payload={"content": encrypted_content, "encrypted": True},
        checksum=checksum,
    )


def make_dm_message(sender: str, recipient: str,
                    encrypted_content: str, checksum: str = None) -> Message:
    """Cria mensagem direta (DM) entre dois usuários."""
    return Message(
        type=MessageType.MESSAGE,
        sender=sender,
        recipient=recipient,
        payload={"content": encrypted_content, "encrypted": True, "is_dm": True},
        checksum=checksum,
    )


def make_system(event: str, message: str, data: dict = None) -> Message:
    """Cria mensagem de sistema (entrada/saída de usuário, etc.)."""
    return Message(
        type=MessageType.SYSTEM,
        payload={"event": event, "message": message, "data": data or {}},
    )


def make_ping() -> Message:
    """Cria mensagem de PING (keep-alive)."""
    return Message(type=MessageType.PING, payload={})


def make_pong() -> Message:
    """Cria mensagem de PONG (resposta ao keep-alive)."""
    return Message(type=MessageType.PONG, payload={})


def make_user_list(users: list) -> Message:
    """Cria mensagem com lista de usuários online."""
    return Message(
        type=MessageType.USER_LIST,
        payload={"users": users, "count": len(users)},
    )


def make_error(code: str, message: str, details: dict = None) -> Message:
    """Cria mensagem de erro genérico."""
    return Message(
        type=MessageType.ERROR,
        payload={"code": code, "message": message, "details": details or {}},
    )


def make_disconnect(sender: str, reason: str = "user_quit") -> Message:
    """Cria mensagem de desconexão."""
    return Message(
        type=MessageType.DISCONNECT,
        sender=sender,
        payload={"reason": reason},
    )
