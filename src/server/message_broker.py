"""
Message Broker — broadcast thread-safe para todos os clientes conectados.

## Por que precisamos de snapshot no broadcast?

O dict `server.clients` é modificado por múltiplas threads simultaneamente:
- Thread de accept adiciona clientes
- Thread de handler remove clientes ao desconectar

Se iterarmos diretamente sobre `server.clients` enquanto outra thread
remove um elemento, temos um RuntimeError: "dictionary changed size during iteration".

Solução: tirar um snapshot (list) dos clientes sob o lock, depois iterar
fora do lock. Isso garante que:
1. Não iteramos sobre estrutura em modificação
2. O lock é liberado rapidamente (não seguramos durante envio de dados)
"""
import logging
import socket
from typing import TYPE_CHECKING

from src.common.crypto import CryptoManager
from src.common.protocol import Message, MessageType, make_chat_message, make_dm_message

if TYPE_CHECKING:
    from src.server.server import ChatServer


def broadcast(server: "ChatServer", content: str, sender_username: str,
              sender_socket: socket.socket, recipient: str = "all",
              is_dm: bool = False) -> int:
    """
    Envia mensagem de chat para todos os clientes (ou para um destinatário específico).

    Fluxo:
      1. Snapshot dos clientes sob lock (thread-safe)
      2. Para cada destinatário, re-criptografa com a chave do destinatário
      3. Envia a mensagem criptografada

    Args:
        server:          Instância do ChatServer.
        content:         Conteúdo em texto plano da mensagem.
        sender_username: Username de quem enviou.
        sender_socket:   Socket do remetente (excluído no broadcast geral).
        recipient:       "all" para broadcast, ou username para DM.
        is_dm:           True se é mensagem direta.

    Returns:
        int: Número de clientes que receberam a mensagem.
    """
    logger = logging.getLogger("server")

    # ── 1. Snapshot thread-safe ──────────────────────────────────────────────
    with server.lock:
        if recipient == "all":
            # Broadcast: todos exceto o remetente
            targets = [
                (sock, info)
                for sock, info in server.clients.items()
                if sock is not sender_socket
            ]
        else:
            # DM: apenas o destinatário
            targets = [
                (sock, info)
                for sock, info in server.clients.items()
                if info.username == recipient
            ]

    if not targets and recipient != "all":
        logger.warning(f"DM falhou: usuário '{recipient}' não encontrado")
        return 0

    # ── 2 & 3. Re-criptografa e envia para cada destinatário ────────────────
    sent_count = 0
    for sock, info in targets:
        try:
            # Re-criptografa o conteúdo com a chave do *destinatário*
            dest_crypto = CryptoManager(key_b64=info.encryption_key)
            encrypted = dest_crypto.encrypt_to_str(content)
            checksum = CryptoManager.generate_checksum(content)

            if is_dm:
                msg = make_dm_message(
                    sender=sender_username,
                    recipient=info.username,
                    encrypted_content=encrypted,
                    checksum=checksum,
                )
            else:
                msg = make_chat_message(
                    sender=sender_username,
                    content=content,
                    encrypted_content=encrypted,
                    recipient="all",
                    checksum=checksum,
                )

            from src.common.protocol import send_message
            send_message(sock, msg)
            sent_count += 1

        except Exception as e:
            logger.warning(
                f"Falha ao enviar para {info.username}: {e}",
                extra={"data": {"username": info.username}},
            )
            # Não remove o cliente aqui — deixa o handler da thread fazer isso

    return sent_count


def broadcast_system(server: "ChatServer", event: str, message: str,
                     data: dict = None, exclude_socket: socket.socket = None) -> None:
    """
    Envia mensagem de sistema para todos os clientes conectados.

    Args:
        server:          Instância do ChatServer.
        event:           Tipo de evento ("user_joined", "user_left", etc.)
        message:         Texto da notificação.
        data:            Dados extras (ex: {"username": "joao"}).
        exclude_socket:  Socket a ser excluído (opcional).
    """
    from src.common.protocol import make_system, send_message

    sys_msg = make_system(event=event, message=message, data=data or {})

    with server.lock:
        targets = [
            sock for sock in server.clients
            if sock is not exclude_socket
        ]

    for sock in targets:
        try:
            send_message(sock, sys_msg)
        except Exception:
            pass  # Ignora falhas em notificações de sistema
