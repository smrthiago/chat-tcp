"""
Exceções customizadas do sistema de chat TCP.
"""


class ChatError(Exception):
    """Exceção base do sistema de chat."""
    pass


class AuthError(ChatError):
    """Erro de autenticação (username inválido, duplicado, etc.)."""
    pass


class CryptoError(ChatError):
    """Erro de criptografia (chave inválida, mensagem corrompida, etc.)."""
    pass


class ConnectionError(ChatError):
    """Erro de conexão TCP (falha ao conectar, socket fechado, etc.)."""
    pass


class MessageTooLargeError(ChatError):
    """Mensagem excede o tamanho máximo permitido."""
    def __init__(self, size: int, max_size: int):
        self.size = size
        self.max_size = max_size
        super().__init__(
            f"Mensagem de {size} bytes excede o limite de {max_size} bytes"
        )


class ProtocolError(ChatError):
    """Mensagem com formato inválido ou versão incompatível."""
    pass


class ServerFullError(ChatError):
    """Servidor atingiu número máximo de clientes."""
    pass
