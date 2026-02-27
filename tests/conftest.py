"""
Fixtures compartilhados e configurações do pytest.

Fixtures:
    - fast_config: sobrescreve PING_INTERVAL para testes rápidos
    - test_server: servidor em porta aleatória com lifecycle gerenciado
"""
import os
import tempfile
import threading
import time
import pytest
import socket as _socket

# Ambiente de teste — desativa logs de arquivo (usa temp dir cross-platform)
_TEST_LOG_DIR = os.path.join(tempfile.gettempdir(), "chat_test_logs")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("LOG_DIR", _TEST_LOG_DIR)
os.environ.setdefault("PING_INTERVAL", "1")
os.environ.setdefault("PING_TIMEOUT", "3")
os.environ.setdefault("SERVER_PORT", "15000")


def find_free_port() -> int:
    """Retorna uma porta livre no sistema."""
    with _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture
def free_port():
    """Fornece uma porta TCP livre para cada teste."""
    return find_free_port()


@pytest.fixture
def test_server(free_port):
    """
    Inicia um ChatServer em thread separada para testes de integração.
    Para o servidor ao encerrar o teste (teardown automático).
    """
    from src.server.server import ChatServer

    server = ChatServer(host="127.0.0.1", port=free_port, max_clients=20)
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()
    time.sleep(0.3)  # Aguarda o servidor iniciar

    yield server

    server.shutdown()
    time.sleep(0.1)
