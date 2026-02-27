"""
Gerenciador de reconexão automática com backoff exponencial.

## Backoff Exponencial

Quando a conexão cai, não tentamos reconectar imediatamente em loop
(isso sobrecarregaria o servidor). Usamos backoff exponencial:

  Tentativa 1: aguarda 2s
  Tentativa 2: aguarda 4s
  Tentativa 3: aguarda 8s
  Tentativa 4: aguarda 16s
  Tentativa 5: aguarda 32s (cap de 60s)

Esse padrão é amplamente usado em sistemas distribuídos para evitar
thundering herd (todos os clientes tentando reconectar ao mesmo tempo).
"""
import time
import socket
import logging

from src.common.config import Config

logger = logging.getLogger("client")


class ConnectionManager:
    """
    Gerencia tentativas de reconexão com backoff exponencial.

    Attributes:
        host:              Endereço do servidor.
        port:              Porta do servidor.
        max_attempts:      Número máximo de tentativas antes de desistir.
        base_delay:        Delay inicial em segundos.
        max_delay:         Delay máximo (cap do backoff).
        on_reconnecting:   Callback chamado a cada tentativa (UI feedback).
    """

    def __init__(
        self,
        host: str,
        port: int,
        max_attempts: int = None,
        base_delay: float = None,
        max_delay: float = 60.0,
        on_reconnecting=None,
    ):
        self.host = host
        self.port = port
        self.max_attempts = max_attempts or Config.RECONNECT_ATTEMPTS
        self.base_delay = base_delay or Config.RECONNECT_DELAY
        self.max_delay = max_delay
        self.on_reconnecting = on_reconnecting  # callback(attempt, max, delay)

    def attempt(self) -> socket.socket | None:
        """
        Tenta reconectar ao servidor com backoff exponencial.

        Returns:
            socket.socket: Socket conectado, ou None se todas as tentativas falharam.
        """
        delay = self.base_delay

        for attempt in range(1, self.max_attempts + 1):
            if self.on_reconnecting:
                self.on_reconnecting(attempt, self.max_attempts, delay)

            logger.info(
                f"Tentativa de reconexão {attempt}/{self.max_attempts} "
                f"em {self.host}:{self.port}",
                extra={"data": {"attempt": attempt, "host": self.host, "port": self.port}},
            )

            sock = self._try_connect()
            if sock:
                logger.info(f"Reconectado com sucesso na tentativa {attempt}")
                return sock

            # Aguarda antes da próxima tentativa (cap no max_delay)
            time.sleep(delay)
            delay = min(delay * 2, self.max_delay)

        logger.error(
            f"Reconexão falhou após {self.max_attempts} tentativas",
            extra={"data": {"host": self.host, "port": self.port}},
        )
        return None

    def _try_connect(self) -> socket.socket | None:
        """
        Tenta uma única conexão TCP.

        Returns:
            socket.socket | None: Socket conectado ou None em caso de falha.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # Timeout por tentativa
            sock.connect((self.host, self.port))
            sock.settimeout(None)  # Remove timeout após conectar
            return sock
        except (ConnectionRefusedError, TimeoutError, OSError):
            return None
