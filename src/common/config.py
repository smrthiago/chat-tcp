"""
Configurações centralizadas do sistema de chat.
Carrega variáveis de ambiente com fallback para defaults seguros.
"""
import os
from dotenv import load_dotenv

# Carrega .env se existir (não obrigatório em produção)
load_dotenv()


class Config:
    """
    Configurações centralizadas do sistema.
    Todas as configurações são lidas do ambiente com fallback para defaults.
    """

    # ===== SERVIDOR =====
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", 5000))
    MAX_CLIENTS: int = int(os.getenv("MAX_CLIENTS", 50))

    # ===== REDE =====
    BUFFER_SIZE: int = int(os.getenv("BUFFER_SIZE", 4096))
    SOCKET_TIMEOUT: int = int(os.getenv("SOCKET_TIMEOUT", 300))
    MAX_MESSAGE_SIZE: int = int(os.getenv("MAX_MESSAGE_SIZE", 65536))  # 64 KB

    # ===== RECONEXÃO =====
    RECONNECT_ATTEMPTS: int = int(os.getenv("RECONNECT_ATTEMPTS", 5))
    RECONNECT_DELAY: float = float(os.getenv("RECONNECT_DELAY", 2.0))

    # ===== SEGURANÇA =====
    ENABLE_ENCRYPTION: bool = os.getenv("ENABLE_ENCRYPTION", "true").lower() == "true"
    PING_INTERVAL: int = int(os.getenv("PING_INTERVAL", 30))
    PING_TIMEOUT: int = int(os.getenv("PING_TIMEOUT", 90))

    # ===== LOGGING =====
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")

    # ===== PROTOCOLO =====
    PROTOCOL_VERSION: str = "1.0"
    USERNAME_MIN_LEN: int = 2
    USERNAME_MAX_LEN: int = 20

    # ===== DESENVOLVIMENTO =====
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    @classmethod
    def validate(cls) -> None:
        """
        Valida configurações críticas na inicialização.

        Raises:
            ValueError: Se alguma configuração for inválida.
        """
        if not (1024 <= cls.SERVER_PORT <= 65535):
            raise ValueError(f"SERVER_PORT inválida: {cls.SERVER_PORT}. Use 1024-65535.")

        if cls.MAX_CLIENTS < 1:
            raise ValueError(f"MAX_CLIENTS deve ser >= 1, got {cls.MAX_CLIENTS}")

        if cls.MAX_MESSAGE_SIZE < 1024:
            raise ValueError(f"MAX_MESSAGE_SIZE muito pequeno: {cls.MAX_MESSAGE_SIZE}")

        if cls.PING_TIMEOUT <= cls.PING_INTERVAL:
            raise ValueError("PING_TIMEOUT deve ser maior que PING_INTERVAL")

        # Garante que o diretório de logs existe
        os.makedirs(cls.LOG_DIR, exist_ok=True)

    @classmethod
    def display(cls) -> str:
        """Retorna string formatada com as configurações ativas."""
        return (
            f"Host={cls.SERVER_HOST}:{cls.SERVER_PORT} | "
            f"MaxClients={cls.MAX_CLIENTS} | "
            f"Encryption={'ON' if cls.ENABLE_ENCRYPTION else 'OFF'} | "
            f"Debug={'ON' if cls.DEBUG else 'OFF'}"
        )
