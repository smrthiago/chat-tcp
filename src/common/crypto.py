"""
Sistema de criptografia do chat — Fernet (AES-128-CBC + HMAC-SHA256).

## O que é Fernet?

Fernet é um esquema de criptografia simétrica da biblioteca `cryptography`.
Por baixo dos panos ele combina:
  - AES-128 em modo CBC         → confidencialidade
  - HMAC-SHA256                 → autenticidade (verifica que não foi alterado)
  - Timestamp embutido          → proteção básica contra ataques de replay

## Modelo de segurança adotado

Cada cliente gera sua própria chave Fernet aleatória e a envia ao servidor
na mensagem AUTH. O servidor usa essa chave para:
  1. Descriptografar mensagens recebidas do cliente
  2. Re-criptografar para cada destinatário usando a chave de cada um

⚠️ LIMITAÇÃO CONHECIDA:
  A chave trafega em texto plano no handshake AUTH (sem TLS). Um atacante
  com acesso à rede pode interceptar a chave e descriptografar as mensagens.
  Em produção, a solução correta seria:
  - Handshake Diffie-Hellman para troca de chaves sem expor a chave
  - TLS/SSL na camada de transporte (ssl.wrap_socket)
  - Criptografia assimétrica (RSA) para o handshake inicial

  Para fins educacionais, este projeto demonstra o conceito de criptografia
  e re-criptografia por usuário, reconhecendo a limitação do handshake.
"""
import hashlib
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from src.common.exceptions import CryptoError


class CryptoManager:
    """
    Gerenciador de criptografia usando Fernet.

    Uso típico:
        # Geração no cliente
        crypto = CryptoManager()        # gera nova chave
        key_b64 = crypto.get_key_b64()  # exporta para enviar ao servidor

        # Importação no servidor
        crypto = CryptoManager(key_b64=key_b64_recebida)  # importa chave
        plain = crypto.decrypt(bytes_recebidos)
    """

    def __init__(self, key_b64: Optional[str] = None):
        """
        Inicializa o gerenciador.

        Args:
            key_b64: Chave Fernet em formato base64 URL-safe.
                     Se None, gera uma nova chave aleatória de 256 bits.
        """
        if key_b64:
            self.set_key(key_b64)
        else:
            self._key = Fernet.generate_key()
            self._cipher = Fernet(self._key)

    # ── Gerenciamento de chaves ───────────────────────────────────────────

    def get_key_b64(self) -> str:
        """
        Retorna a chave em formato base64 URL-safe (string).
        Adequado para transmissão na mensagem AUTH.

        Returns:
            str: Chave codificada em base64.
        """
        return self._key.decode("utf-8")

    def set_key(self, key_b64: str) -> None:
        """
        Importa uma chave a partir de string base64.

        Args:
            key_b64: Chave em formato base64 URL-safe.

        Raises:
            CryptoError: Se a chave for inválida.
        """
        try:
            self._key = key_b64.encode("utf-8")
            self._cipher = Fernet(self._key)
        except Exception as e:
            raise CryptoError(f"Chave inválida: {e}") from e

    # ── Criptografia / Descriptografia ───────────────────────────────────

    def encrypt(self, plaintext: str) -> bytes:
        """
        Criptografa um texto usando AES-128-CBC + HMAC-SHA256.

        Args:
            plaintext: Texto em claro (string UTF-8).

        Returns:
            bytes: Token Fernet (dados criptografados + HMAC + timestamp).

        Raises:
            CryptoError: Se a criptografia falhar.
        """
        try:
            return self._cipher.encrypt(plaintext.encode("utf-8"))
        except Exception as e:
            raise CryptoError(f"Erro ao criptografar: {e}") from e

    def encrypt_to_str(self, plaintext: str) -> str:
        """
        Criptografa e retorna como string base64 (conveniente para JSON).

        Args:
            plaintext: Texto em claro.

        Returns:
            str: Token Fernet codificado como string.
        """
        return self.encrypt(plaintext).decode("utf-8")

    def decrypt(self, token: bytes) -> str:
        """
        Descriptografa um token Fernet.

        Args:
            token: Token Fernet (bytes).

        Returns:
            str: Texto em claro original.

        Raises:
            CryptoError: Se o token for inválido, corrompido ou usar chave errada.
        """
        try:
            return self._cipher.decrypt(token).decode("utf-8")
        except InvalidToken as e:
            raise CryptoError(
                "Falha ao descriptografar: token inválido, corrompido ou "
                "chave incorreta. Possível ataque de replay ou adulteração."
            ) from e
        except Exception as e:
            raise CryptoError(f"Erro ao descriptografar: {e}") from e

    def decrypt_from_str(self, token_str: str) -> str:
        """
        Descriptografa a partir de string base64.

        Args:
            token_str: Token Fernet como string.

        Returns:
            str: Texto em claro.
        """
        return self.decrypt(token_str.encode("utf-8"))

    # ── Integridade ───────────────────────────────────────────────────────

    @staticmethod
    def generate_checksum(data: str) -> str:
        """
        Gera checksum SHA-256 de uma string.

        Usado para verificar integridade de mensagens (detecção de corrupção).
        SHA-256 produz um hash de 256 bits (64 caracteres hex).

        Args:
            data: String para calcular o hash.

        Returns:
            str: Hash SHA-256 em formato hexadecimal.
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_checksum(data: str, checksum: str) -> bool:
        """
        Verifica se o checksum corresponde aos dados.

        Args:
            data:     Dados originais.
            checksum: Checksum esperado.

        Returns:
            bool: True se o checksum é válido.
        """
        expected = hashlib.sha256(data.encode("utf-8")).hexdigest()
        # Comparação em tempo constante (evita timing attacks)
        return _constant_time_compare(expected, checksum)


def _constant_time_compare(a: str, b: str) -> bool:
    """
    Compara duas strings em tempo constante para evitar timing attacks.
    Garante que o tempo de comparação não depende de onde as strings diferem.
    """
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0
