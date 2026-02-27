"""
Cliente TCP para chat em tempo real.

Uso:
    python -m src.client.client
    python -m src.client.client --host 192.168.1.10 --port 5000 --username Alice
    python -m src.client.client --host meu-servidor.railway.app --port 5000

Comandos no chat:
    /quit            — desconecta e encerra
    /users           — lista usuários online
    /dm <user> <msg> — envia mensagem direta
    /help            — exibe ajuda
"""
import argparse
import socket
import sys
import threading
from typing import Optional

from src.common.config import Config
from src.common.crypto import CryptoManager
from src.common.logger import setup_logger
from src.common.protocol import (
    MessageType,
    make_auth_request,
    make_chat_message,
    make_dm_message,
    make_disconnect,
    make_ping,
    recv_message,
    send_message,
)
from src.common.exceptions import CryptoError, ProtocolError
from src.client.ui import ChatUI
from src.client.connection_manager import ConnectionManager

logger = setup_logger("client")


class ChatClient:
    """
    Cliente TCP para o sistema de chat.

    Arquitetura de threads:
      - Thread principal: input_loop (aguarda input do usuário)
      - receive_thread:  receive_loop (aguarda mensagens do servidor)

    As duas threads rodam em paralelo, permitindo que o usuário
    receba mensagens enquanto digita, sem bloqueio.
    """

    def __init__(self, host: str = None, port: int = None, username: str = None):
        self.host = host or "localhost"
        self.port = port or Config.SERVER_PORT
        self.username = username

        self._socket: Optional[socket.socket] = None
        self._crypto = CryptoManager()     # Gera chave única para esta sessão
        self._running = False
        self._connected = False
        self._users_online: list = []

    # ── Conexão e Autenticação ───────────────────────────────────────────────

    def start(self) -> None:
        """Ponto de entrada do cliente."""
        # Pede username se não fornecido
        if not self.username:
            self.username = self._prompt_username()

        ChatUI.print_connecting(self.host, self.port)

        if not self._connect():
            ChatUI.print_error(f"Não foi possível conectar a {self.host}:{self.port}")
            sys.exit(1)

        if not self._authenticate():
            ChatUI.print_error("Autenticação falhou.")
            self._close_socket()
            sys.exit(1)

        self._running = True
        self._connected = True

        ChatUI.print_welcome(self.username, self._users_online)

        # Inicia thread de recebimento
        recv_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True,
            name="receive",
        )
        recv_thread.start()

        # Loop de input na thread principal
        self._input_loop()

    def _prompt_username(self) -> str:
        """Solicita username ao usuário via prompt interativo."""
        print("\n" + "═" * 60)
        print("  Chat TCP/IP  •  Infraestrutura de Redes")
        print("═" * 60)
        while True:
            username = input("  Digite seu username: ").strip()
            if Config.USERNAME_MIN_LEN <= len(username) <= Config.USERNAME_MAX_LEN:
                return username
            print(f"  Username deve ter entre {Config.USERNAME_MIN_LEN} "
                  f"e {Config.USERNAME_MAX_LEN} caracteres.")

    def _connect(self) -> bool:
        """
        Estabelece conexão TCP com o servidor.

        Returns:
            bool: True se conectado com sucesso.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((self.host, self.port))
            sock.settimeout(None)
            self._socket = sock
            logger.info(
                f"Conectado a {self.host}:{self.port}",
                extra={"data": {"host": self.host, "port": self.port}},
            )
            return True
        except Exception as e:
            logger.error(f"Falha ao conectar: {e}")
            return False

    def _authenticate(self) -> bool:
        """
        Envia credenciais de autenticação ao servidor e aguarda resposta.

        Returns:
            bool: True se autenticado com sucesso.
        """
        try:
            auth_msg = make_auth_request(
                username=self.username,
                encryption_key=self._crypto.get_key_b64(),
            )
            send_message(self._socket, auth_msg)

            response = recv_message(self._socket)

            if response.type == MessageType.AUTH:
                status = response.payload.get("status")
                if status == "success":
                    self._users_online = response.payload.get("users_online", [])
                    logger.info(f"Autenticado como '{self.username}'")
                    return True

            # AUTH falhou
            reason = response.payload.get("message", "Erro desconhecido")
            ChatUI.print_error(f"Autenticação rejeitada: {reason}")
            return False

        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            ChatUI.print_error(f"Erro na autenticação: {e}")
            return False

    # ── Loops de execução ────────────────────────────────────────────────────

    def _receive_loop(self) -> None:
        """
        Loop executado em thread separada para receber mensagens do servidor.
        Trata todos os tipos de mensagem e atualiza a UI.
        """
        while self._running:
            try:
                msg = recv_message(self._socket)
                self._handle_incoming(msg)
            except ConnectionError:
                if self._running:
                    ChatUI.print_disconnected()
                    self._running = False
                    self._connected = False
                    self._try_reconnect()
                break
            except ProtocolError as e:
                logger.warning(f"Protocolo inválido recebido: {e}")
            except Exception as e:
                if self._running:
                    logger.error(f"Erro no receive_loop: {e}", exc_info=True)
                break

    def _handle_incoming(self, msg) -> None:
        """Processa mensagem recebida do servidor."""
        if msg.type == MessageType.MESSAGE:
            encrypted = msg.payload.get("content", "")
            is_dm = msg.payload.get("is_dm", False)
            try:
                plaintext = self._crypto.decrypt_from_str(encrypted)
                # Verifica checksum se presente
                if msg.checksum:
                    from src.common.crypto import CryptoManager as CM
                    if not CM.verify_checksum(plaintext, msg.checksum):
                        ChatUI.print_error("⚠ Integridade comprometida (checksum inválido)")
                        return
                ChatUI.print_message(
                    sender=msg.sender or "?",
                    content=plaintext,
                    own_username=self.username,
                    timestamp=msg.timestamp,
                    is_dm=is_dm,
                )
            except CryptoError:
                ChatUI.print_error("Não foi possível descriptografar a mensagem.")

        elif msg.type == MessageType.SYSTEM:
            ChatUI.print_system(msg.payload.get("message", ""))

        elif msg.type == MessageType.USER_LIST:
            users = msg.payload.get("users", [])
            ChatUI.print_user_list(users)

        elif msg.type == MessageType.ERROR:
            code = msg.payload.get("code", "ERROR")
            message = msg.payload.get("message", "")
            ChatUI.print_error(f"[{code}] {message}")

        elif msg.type == MessageType.PONG:
            logger.debug("PONG recebido")

        elif msg.type == MessageType.SYSTEM and \
                msg.payload.get("event") == "server_shutdown":
            ChatUI.print_system(msg.payload.get("message", "Servidor encerrado"))
            self._running = False

    def _input_loop(self) -> None:
        """
        Loop de input na thread principal.
        Captura o que o usuário digita e envia ao servidor.
        """
        while self._running:
            try:
                text = input(ChatUI.prompt(self.username)).strip()
                if not text:
                    continue

                if text.startswith("/"):
                    self._handle_command(text)
                else:
                    self._send_chat(text)

            except (EOFError, KeyboardInterrupt):
                self._disconnect()
                break

    def _handle_command(self, command: str) -> None:
        """
        Processa comandos especiais.

        Comandos disponíveis:
            /quit              — desconecta
            /users             — lista usuários online
            /dm <user> <msg>   — mensagem direta
            /help              — exibe ajuda
        """
        parts = command.split(maxsplit=2)
        cmd = parts[0].lower()

        if cmd == "/quit":
            self._disconnect()

        elif cmd == "/users":
            self._request_user_list()

        elif cmd == "/dm":
            if len(parts) < 3:
                ChatUI.print_error("Uso: /dm <username> <mensagem>")
                return
            target_user = parts[1]
            message_text = parts[2]
            self._send_dm(target_user, message_text)

        elif cmd == "/help":
            ChatUI.print_help()

        else:
            ChatUI.print_error(f"Comando desconhecido: {cmd}. Digite /help.")

    # ── Envio de mensagens ───────────────────────────────────────────────────

    def _send_chat(self, content: str) -> None:
        """Criptografa e envia mensagem de broadcast."""
        try:
            encrypted = self._crypto.encrypt_to_str(content)
            checksum = CryptoManager.generate_checksum(content)
            msg = make_chat_message(
                sender=self.username,
                content=content,
                encrypted_content=encrypted,
                checksum=checksum,
            )
            send_message(self._socket, msg)
            logger.debug(f"Mensagem enviada ({len(content)} chars)")
        except Exception as e:
            ChatUI.print_error(f"Erro ao enviar mensagem: {e}")

    def _send_dm(self, recipient: str, content: str) -> None:
        """Criptografa e envia mensagem direta (DM)."""
        try:
            encrypted = self._crypto.encrypt_to_str(content)
            checksum = CryptoManager.generate_checksum(content)
            msg = make_dm_message(
                sender=self.username,
                recipient=recipient,
                encrypted_content=encrypted,
                checksum=checksum,
            )
            send_message(self._socket, msg)
            # Exibe a própria mensagem enviada
            ChatUI.print_message(
                sender=self.username,
                content=f"→ {recipient}: {content}",
                own_username=self.username,
                is_dm=True,
            )
        except Exception as e:
            ChatUI.print_error(f"Erro ao enviar DM: {e}")

    def _request_user_list(self) -> None:
        """Solicita lista de usuários ao servidor."""
        from src.common.protocol import make_user_list, MessageType, Message
        try:
            msg = Message(type=MessageType.USER_LIST, payload={})
            send_message(self._socket, msg)
        except Exception as e:
            ChatUI.print_error(f"Erro ao solicitar lista: {e}")

    # ── Desconexão e Reconexão ───────────────────────────────────────────────

    def _disconnect(self) -> None:
        """Desconecta graciosamente do servidor."""
        self._running = False
        self._connected = False
        try:
            send_message(self._socket, make_disconnect(self.username))
        except Exception:
            pass
        self._close_socket()
        print(f"\n  Desconectado. Até logo, {self.username}! 👋\n")
        logger.info(f"Cliente '{self.username}' desconectou")

    def _try_reconnect(self) -> None:
        """Tenta reconectar usando backoff exponencial."""
        manager = ConnectionManager(
            host=self.host,
            port=self.port,
            on_reconnecting=lambda a, m, d: ChatUI.print_reconnecting(a, m, d),
        )
        new_socket = manager.attempt()

        if new_socket:
            self._socket = new_socket
            if self._authenticate():
                self._running = True
                self._connected = True
                ChatUI.print_info("Reconectado com sucesso! ✅")
                # Reinicia receive loop
                recv_thread = threading.Thread(
                    target=self._receive_loop, daemon=True, name="receive"
                )
                recv_thread.start()
            else:
                ChatUI.print_error("Não foi possível reautenticar.")
        else:
            ChatUI.print_error("Reconexão falhou. Encerrando.")
            sys.exit(1)

    def _close_socket(self) -> None:
        """Fecha o socket TCP."""
        if self._socket:
            try:
                self._socket.close()
            except Exception:
                pass
            self._socket = None


# ── Entrypoint ───────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chat TCP Client — Infraestrutura de Redes"
    )
    parser.add_argument(
        "--host", default=None,
        help=f"Endereço do servidor (default: localhost ou SERVER_HOST do .env)"
    )
    parser.add_argument(
        "--port", type=int, default=Config.SERVER_PORT,
        help=f"Porta do servidor (default: {Config.SERVER_PORT})"
    )
    parser.add_argument(
        "--username", "-u", default=None,
        help="Username (solicita interativamente se omitido)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    host = args.host or Config.SERVER_HOST.replace("0.0.0.0", "localhost")
    client = ChatClient(host=host, port=args.port, username=args.username)
    client.start()


if __name__ == "__main__":
    main()
