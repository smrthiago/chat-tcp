"""
Servidor TCP multi-cliente para chat em tempo real.

Uso:
    # Via módulo
    python -m src.server.server

    # Com argumentos
    python -m src.server.server --host 0.0.0.0 --port 5000

    # Variáveis de ambiente
    SERVER_PORT=8080 python -m src.server.server
"""
import argparse
import signal
import socket
import sys
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional

from src.common.config import Config
from src.common.logger import setup_logger
from src.common.protocol import make_system, send_message

logger = setup_logger("server")


@dataclass
class ClientInfo:
    """
    Dados de um cliente conectado.

    Attributes:
        socket:         Socket TCP da conexão.
        address:        Tupla (ip, port) do cliente.
        username:       Nome de usuário escolhido.
        encryption_key: Chave Fernet em base64 (gerada pelo cliente).
        connected_at:   Timestamp de conexão.
        last_ping:      Timestamp da última mensagem recebida (keep-alive).
        thread:         Thread que gerencia este cliente.
    """
    socket: socket.socket
    address: tuple
    username: str
    encryption_key: str
    connected_at: datetime
    last_ping: datetime
    thread: threading.Thread


class ChatServer:
    """
    Servidor TCP multi-cliente para chat em tempo real.

    Arquitetura de concorrência:
      - Thread principal: accept loop (aguarda novas conexões)
      - Uma thread por cliente: handle_client (recebe e roteia mensagens)
      - Lock global: protege o dicionário 'clients' de race conditions

    Gerenciamento de estado:
      - self.clients: {socket → ClientInfo} — clientes ativos
      - self.usernames: {str} — usernames únicos (lookup rápido O(1))
    """

    def __init__(self, host: str = None, port: int = None, max_clients: int = None):
        self.host = host or Config.SERVER_HOST
        self.port = port or Config.SERVER_PORT
        self.max_clients = max_clients or Config.MAX_CLIENTS

        self.clients: Dict[socket.socket, ClientInfo] = {}
        self.usernames: set = set()
        self.lock = threading.Lock()
        self.running = False
        self._server_socket: Optional[socket.socket] = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """
        Inicializa o socket, configura signal handlers e inicia o accept loop.

        Raises:
            OSError: Se não conseguir fazer bind na porta especificada.
        """
        Config.validate()
        self._setup_socket()
        self._setup_signal_handlers()
        self.running = True

        logger.info(
            f"🚀 Servidor iniciado em {self.host}:{self.port} | "
            f"Max clientes: {self.max_clients} | "
            f"Criptografia: {'ON' if Config.ENABLE_ENCRYPTION else 'OFF'}",
            extra={"data": {"host": self.host, "port": self.port}},
        )
        print(f"\n{'='*60}")
        print(f"  Chat TCP Server v1.0")
        print(f"  Endereço : {self.host}:{self.port}")
        print(f"  Clientes : máximo {self.max_clients}")
        print(f"  Cripto   : {'✅ Fernet AES-128' if Config.ENABLE_ENCRYPTION else '❌ Desativada'}")
        print(f"{'='*60}\n")

        self._accept_loop()

    def _setup_socket(self) -> None:
        """Cria e configura o socket do servidor."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR: permite reusar a porta imediatamente após restart
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(self.max_clients)
        self._server_socket.settimeout(1.0)  # Timeout para checar self.running

    def _setup_signal_handlers(self) -> None:
        """
        Configura handlers para SIGINT (Ctrl+C) e SIGTERM (kill).

        signal.signal() só funciona na thread principal do interpretador.
        Em testes, o servidor roda em thread secundária — registramos
        os handlers apenas quando estamos na main thread para evitar ValueError.
        """
        import threading as _threading
        if _threading.current_thread() is not _threading.main_thread():
            logger.debug("Servidor em thread secundária — signal handlers ignorados")
            return

        def _handle_signal(signum, frame):
            print("\n")
            logger.info(f"Sinal {signum} recebido. Iniciando shutdown gracioso...")
            self.shutdown()

        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

    def _accept_loop(self) -> None:
        """
        Loop principal que aceita novas conexões TCP.
        Cria uma thread dedicada para cada cliente que se conecta.
        """
        from src.server.client_handler import handle_client

        logger.info("Aguardando conexões...")

        while self.running:
            try:
                client_socket, address = self._server_socket.accept()
                logger.info(
                    f"Nova conexão: {address}",
                    extra={"data": {"address": str(address)}},
                )

                # Thread daemon: encerra automaticamente quando o servidor fecha
                thread = threading.Thread(
                    target=handle_client,
                    args=(self, client_socket, address),
                    daemon=True,
                    name=f"client-{address[0]}:{address[1]}",
                )
                thread.start()

            except socket.timeout:
                # Timeout esperado — apenas checa self.running e volta
                continue
            except OSError:
                if self.running:
                    logger.error("Erro ao aceitar conexão", exc_info=True)
                break

    # ── Shutdown ─────────────────────────────────────────────────────────────

    def shutdown(self) -> None:
        """
        Encerra o servidor graciosamente:
          1. Para o accept loop
          2. Notifica todos os clientes
          3. Fecha todas as conexões
          4. Libera o socket do servidor
        """
        if not self.running:
            return

        self.running = False
        logger.info("Iniciando shutdown...")

        # Notifica clientes
        self._notify_shutdown()

        # Fecha conexões
        with self.lock:
            sockets = list(self.clients.keys())

        for sock in sockets:
            try:
                sock.close()
            except Exception:
                pass

        # Fecha socket do servidor
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass

        logger.info(f"Servidor encerrado. {len(sockets)} conexão(ões) fechada(s).")
        print("\n✅ Servidor encerrado com sucesso.\n")

    def _notify_shutdown(self) -> None:
        """Envia mensagem de shutdown para todos os clientes conectados."""
        shutdown_msg = make_system(
            event="server_shutdown",
            message="⚠️  Servidor sendo encerrado. Até logo!",
        )
        with self.lock:
            sockets = list(self.clients.keys())

        for sock in sockets:
            try:
                send_message(sock, shutdown_msg)
            except Exception:
                pass

    # ── Helpers ──────────────────────────────────────────────────────────────

    def get_users_online(self) -> list:
        """Retorna lista de usernames conectados."""
        with self.lock:
            return [info.username for info in self.clients.values()]

    def get_client_count(self) -> int:
        """Retorna número de clientes conectados."""
        with self.lock:
            return len(self.clients)


# ── Entrypoint ───────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chat TCP Server — Infraestrutura de Redes"
    )
    parser.add_argument("--host", default=Config.SERVER_HOST,
                        help=f"Endereço de bind (default: {Config.SERVER_HOST})")
    parser.add_argument("--port", type=int, default=Config.SERVER_PORT,
                        help=f"Porta de escuta (default: {Config.SERVER_PORT})")
    parser.add_argument("--max-clients", type=int, default=Config.MAX_CLIENTS,
                        help=f"Máximo de clientes simultâneos (default: {Config.MAX_CLIENTS})")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ChatServer(host=args.host, port=args.port, max_clients=args.max_clients)
    server.start()


if __name__ == "__main__":
    main()
