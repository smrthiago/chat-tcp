"""
Módulo de autenticação — validação e registro de usuários.
"""
import re

from src.common.config import Config
from src.common.exceptions import AuthError

# Regex: apenas letras, números, underscore e hífen
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


def validate_username(username: str, active_usernames: set) -> None:
    """
    Valida um username antes de registrar o cliente.

    Args:
        username:         Username enviado pelo cliente.
        active_usernames: Conjunto de usernames já registrados no servidor.

    Raises:
        AuthError: Com mensagem descritiva se a validação falhar.
    """
    if not username or not isinstance(username, str):
        raise AuthError("Username não pode ser vazio.")

    username = username.strip()

    if len(username) < Config.USERNAME_MIN_LEN:
        raise AuthError(
            f"Username muito curto. Mínimo: {Config.USERNAME_MIN_LEN} caracteres."
        )

    if len(username) > Config.USERNAME_MAX_LEN:
        raise AuthError(
            f"Username muito longo. Máximo: {Config.USERNAME_MAX_LEN} caracteres."
        )

    if not _USERNAME_RE.match(username):
        raise AuthError(
            "Username inválido. Use apenas letras, números, _ ou -."
        )

    if username.lower() in {u.lower() for u in active_usernames}:
        raise AuthError(f"Username '{username}' já está em uso. Escolha outro.")
