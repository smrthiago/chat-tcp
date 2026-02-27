"""
Handler de cliente — executado em thread separada para cada conexão.

Cada cliente conectado recebe sua própria thread rodando esta função.
Responsabilidades:
  1. Autenticar o cliente (username + chave de criptografia)
  2. Loop de recebimento de mensagens
  3. Roteamento: broadcast ou DM
  4. Responder PING com PONG (keep-alive)
  5. Limpar recursos ao desconectar
"""
import logging
import socket
import threading
from datetime import datetime, timezone

from src.common.config import Config
from src.common.crypto import CryptoManager
from src.common.exceptions import AuthError, CryptoError, ProtocolError
from src.common.protocol import (
    MessageType,
    make_auth_success,
    make_auth_error,
    make_pong,
    make_user_list,
    make_error,
    recv_message,
    send_message,
)
from src.server.auth import validate_username
from src.server.message_broker import broadcast, broadcast_system

logger = logging.getLogger("server")


def handle_client(server, client_socket: socket.socket, address: tuple) -> None:
    """
    Ponto de entrada da thread de cada cliente.

    Args:
        server:        Instância do ChatServer.
        client_socket: Socket TCP da conexão.
        address:       Tupla (ip, port) do cliente.
    """
    username = None

    try:
        # ── Autenticação ────────────────────────────────────────────────────
        client_info = _authenticate(server, client_socket, address)
        if client_info is None:
            return  # Falha na autenticação — socket já fechado
        username = client_info.username

        # ── Loop principal de recebimento ───────────────────────────────────
        _message_loop(server, client_socket, client_info)

    except ConnectionError:
        logger.info(f"Conexão encerrada por {address} ({username or 'não autenticado'})")
    except Exception as e:
        logger.error(
            f"Erro não tratado no handler de {address}: {e}",
            exc_info=True,
            extra={"data": {"address": str(address), "username": username}},
        )
    finally:
        _cleanup(server, client_socket, username)


def _authenticate(server, client_socket: socket.socket, address: tuple):
    """
    Aguarda e valida a mensagem AUTH do cliente.

    Returns:
        ClientInfo se autenticado, None se falhar.
    """
    from src.server.server import ClientInfo  # import local para evitar circular

    try:
        msg = recv_message(client_socket)

        if msg.type != MessageType.AUTH:
            send_message(client_socket, make_error("PROTOCOL_ERROR", "Esperado AUTH"))
            client_socket.close()
            return None

        username = msg.payload.get("username", "").strip()
        encryption_key = msg.payload.get("encryption_key", "")

        # Valida username
        with server.lock:
            active = set(server.usernames)

        validate_username(username, active)

        # Verifica limite de clientes
        with server.lock:
            if len(server.clients) >= Config.MAX_CLIENTS:
                send_message(client_socket, make_error(
                    "SERVER_FULL",
                    f"Servidor lotado. Máximo: {Config.MAX_CLIENTS} clientes."
                ))
                client_socket.close()
                return None

        # Cria info do cliente
        client_info = ClientInfo(
            socket=client_socket,
            address=address,
            username=username,
            encryption_key=encryption_key,
            connected_at=datetime.now(timezone.utc),
            last_ping=datetime.now(timezone.utc),
            thread=threading.current_thread(),
        )

        # Registra no servidor
        with server.lock:
            server.clients[client_socket] = client_info
            server.usernames.add(username)
            users_online = [
                info.username for info in server.clients.values()
                if info.username != username
            ]

        # Responde com sucesso
        send_message(client_socket, make_auth_success(users_online))

        logger.info(
            f"Cliente autenticado: {username} @ {address}",
            extra={"data": {"username": username, "address": str(address)}},
        )

        # Notifica outros clientes
        broadcast_system(
            server,
            event="user_joined",
            message=f"🟢 {username} entrou no chat",
            data={"username": username},
            exclude_socket=client_socket,
        )

        return client_info

    except AuthError as e:
        logger.warning(f"Autenticação falhou em {address}: {e}")
        try:
            send_message(client_socket, make_auth_error(str(e)))
        except Exception:
            pass
        client_socket.close()
        return None

    except Exception as e:
        logger.error(f"Erro na autenticação de {address}: {e}", exc_info=True)
        client_socket.close()
        return None


def _message_loop(server, client_socket: socket.socket, client_info) -> None:
    """
    Loop principal de recebimento de mensagens de um cliente autenticado.
    """
    client_crypto = CryptoManager(key_b64=client_info.encryption_key)

    while server.running:
        try:
            msg = recv_message(client_socket)
        except ConnectionError:
            break

        # Atualiza timestamp de atividade
        client_info.last_ping = datetime.now(timezone.utc)

        if msg.type == MessageType.MESSAGE:
            _handle_chat(server, client_socket, client_info, client_crypto, msg)

        elif msg.type == MessageType.PING:
            _handle_ping(client_socket)

        elif msg.type == MessageType.DISCONNECT:
            logger.info(
                f"{client_info.username} desconectou voluntariamente",
                extra={"data": {"username": client_info.username}},
            )
            break

        elif msg.type == MessageType.USER_LIST:
            _handle_user_list(server, client_socket)

        else:
            logger.debug(f"Tipo de mensagem não tratado: {msg.type}")


def _handle_chat(server, client_socket, client_info, client_crypto, msg) -> None:
    """Processa e roteia mensagem de chat."""
    encrypted_content = msg.payload.get("content", "")

    try:
        # Descriptografa com a chave do remetente
        plaintext = client_crypto.decrypt_from_str(encrypted_content)
    except CryptoError as e:
        logger.warning(f"Falha ao descriptografar mensagem de {client_info.username}: {e}")
        try:
            send_message(client_socket, make_error("DECRYPT_ERROR", "Mensagem corrompida"))
        except Exception:
            pass
        return

    recipient = msg.recipient or "all"
    is_dm = msg.payload.get("is_dm", False) or (recipient not in ("all", None, ""))

    if is_dm and recipient != "all":
        # Mensagem direta
        count = broadcast(
            server, plaintext, client_info.username,
            client_socket, recipient=recipient, is_dm=True
        )
        if count == 0:
            try:
                send_message(
                    client_socket,
                    make_error("USER_NOT_FOUND", f"Usuário '{recipient}' não está online")
                )
            except Exception:
                pass
        logger.info(
            f"DM: {client_info.username} → {recipient}",
            extra={"data": {"from": client_info.username, "to": recipient}},
        )
    else:
        # Broadcast para todos
        count = broadcast(
            server, plaintext, client_info.username, client_socket
        )
        logger.info(
            f"[{client_info.username}]: broadcast para {count} cliente(s)",
            extra={"data": {"sender": client_info.username, "recipients": count}},
        )


def _handle_ping(client_socket: socket.socket) -> None:
    """Responde PING com PONG (keep-alive)."""
    try:
        send_message(client_socket, make_pong())
    except Exception:
        pass


def _handle_user_list(server, client_socket: socket.socket) -> None:
    """Envia lista de usuários online."""
    with server.lock:
        users = [
            {"username": info.username,
             "connected_at": info.connected_at.isoformat()}
            for info in server.clients.values()
        ]
    try:
        send_message(client_socket, make_user_list(users))
    except Exception:
        pass


def _cleanup(server, client_socket: socket.socket, username: str) -> None:
    """Remove cliente do servidor e fecha o socket."""
    removed = False
    with server.lock:
        if client_socket in server.clients:
            del server.clients[client_socket]
            removed = True
        if username and username in server.usernames:
            server.usernames.discard(username)

    if removed and username:
        logger.info(
            f"Cliente removido: {username}",
            extra={"data": {"username": username}},
        )
        broadcast_system(
            server,
            event="user_left",
            message=f"🔴 {username} saiu do chat",
            data={"username": username},
        )

    try:
        client_socket.close()
    except Exception:
        pass
