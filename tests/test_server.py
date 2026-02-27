"""
Testes de integração do servidor (src/server/).

Requer que o servidor esteja rodando em thread — usa fixture test_server do conftest.
"""
import socket
import time
import threading
import pytest

from src.common.crypto import CryptoManager
from src.common.protocol import (
    MessageType,
    make_auth_request,
    make_chat_message,
    make_disconnect,
    recv_message,
    send_message,
)
from src.server.auth import validate_username
from src.common.exceptions import AuthError


# ── Helpers de teste ─────────────────────────────────────────────────────────

def connect_and_auth(host: str, port: int, username: str):
    """Helper: conecta e autentica um cliente de teste."""
    crypto = CryptoManager()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.settimeout(5.0)

    auth_msg = make_auth_request(username, crypto.get_key_b64())
    send_message(sock, auth_msg)

    response = recv_message(sock)
    return sock, crypto, response


# ── Testes de Autenticação ───────────────────────────────────────────────────

class TestAuthentication:

    def test_successful_auth(self, test_server):
        """Cliente deve autenticar com sucesso e receber users_online."""
        sock, crypto, response = connect_and_auth(
            "127.0.0.1", test_server.port, "alice"
        )
        try:
            assert response.type == MessageType.AUTH
            assert response.payload.get("status") == "success"
            assert "users_online" in response.payload
        finally:
            sock.close()

    def test_duplicate_username_rejected(self, test_server):
        """Segundo cliente com mesmo username deve receber AUTH_FAILED."""
        sock1, _, _ = connect_and_auth("127.0.0.1", test_server.port, "bob")
        try:
            sock2, crypto2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM), CryptoManager()
            sock2.connect(("127.0.0.1", test_server.port))
            sock2.settimeout(5.0)

            send_message(sock2, make_auth_request("bob", crypto2.get_key_b64()))
            response = recv_message(sock2)

            assert response.type == MessageType.ERROR
            assert response.payload.get("code") == "AUTH_FAILED"
            sock2.close()
        finally:
            sock1.close()

    def test_multiple_clients_connect(self, test_server):
        """Três clientes devem conseguir se conectar simultaneamente."""
        sockets = []
        try:
            for i in range(3):
                sock, _, response = connect_and_auth(
                    "127.0.0.1", test_server.port, f"user{i}"
                )
                assert response.type == MessageType.AUTH
                sockets.append(sock)

            assert test_server.get_client_count() == 3
        finally:
            for s in sockets:
                s.close()

    def test_server_count_decreases_on_disconnect(self, test_server):
        """Ao desconectar, contagem de clientes deve diminuir."""
        sock, _, _ = connect_and_auth("127.0.0.1", test_server.port, "temp_user")
        assert test_server.get_client_count() == 1

        send_message(sock, make_disconnect("temp_user"))
        sock.close()
        time.sleep(0.3)

        assert test_server.get_client_count() == 0


# ── Testes de Broadcast ──────────────────────────────────────────────────────

class TestBroadcast:

    def test_message_reaches_other_clients(self, test_server):
        """Mensagem de Alice deve ser recebida por Bob (não por Alice)."""
        host = "127.0.0.1"
        port = test_server.port

        alice_sock, alice_crypto, _ = connect_and_auth(host, port, "alice_b")
        bob_sock, bob_crypto, _ = connect_and_auth(host, port, "bob_b")

        try:
            # Bob: aguarda na thread para não bloquear
            received = []
            def bob_receive():
                try:
                    while True:
                        msg = recv_message(bob_sock)
                        if msg.type == MessageType.MESSAGE:
                            plaintext = bob_crypto.decrypt_from_str(
                                msg.payload.get("content", "")
                            )
                            received.append(plaintext)
                            break
                        elif msg.type == MessageType.SYSTEM:
                            continue  # Ignora SYSTEM de alice entrar
                except Exception:
                    pass

            t = threading.Thread(target=bob_receive, daemon=True)
            t.start()

            # Alice: consome SYSTEM de bob entrar
            alice_sock.settimeout(2.0)
            try:
                recv_message(alice_sock)  # SYSTEM: bob entrou
            except Exception:
                pass

            alice_sock.settimeout(5.0)

            # Alice envia mensagem
            content = "Olá Bob!"
            encrypted = alice_crypto.encrypt_to_str(content)
            send_message(alice_sock, make_chat_message(
                sender="alice_b",
                content=content,
                encrypted_content=encrypted,
            ))

            t.join(timeout=3.0)
            assert content in received, f"Bob não recebeu. Recebido: {received}"

        finally:
            alice_sock.close()
            bob_sock.close()

    def test_sender_does_not_receive_own_message(self, test_server):
        """Remetente NÃO deve receber sua própria mensagem."""
        host = "127.0.0.1"
        port = test_server.port

        alice_sock, alice_crypto, _ = connect_and_auth(host, port, "alice_c")

        try:
            alice_sock.settimeout(1.0)
            content = "Mensagem própria"
            encrypted = alice_crypto.encrypt_to_str(content)
            send_message(alice_sock, make_chat_message(
                sender="alice_c", content=content,
                encrypted_content=encrypted,
            ))

            # Alice não deve receber de volta
            own_received = False
            try:
                msg = recv_message(alice_sock)
                if msg.type == MessageType.MESSAGE:
                    own_received = True
            except Exception:
                pass

            assert not own_received
        finally:
            alice_sock.close()


# ── Testes do módulo auth ────────────────────────────────────────────────────

class TestAuthValidation:
    """Testa a função validate_username isoladamente."""

    def test_valid_username(self):
        validate_username("Alice", set())  # Não deve levantar

    def test_duplicate_raises(self):
        with pytest.raises(AuthError):
            validate_username("alice", {"alice"})

    def test_case_insensitive_duplicate(self):
        with pytest.raises(AuthError):
            validate_username("ALICE", {"alice"})

    def test_too_short_raises(self):
        with pytest.raises(AuthError):
            validate_username("a", set())

    def test_too_long_raises(self):
        with pytest.raises(AuthError):
            validate_username("a" * 25, set())

    def test_special_chars_raises(self):
        with pytest.raises(AuthError):
            validate_username("user name!", set())

    def test_underscore_and_hyphen_allowed(self):
        """Underscore e hífen devem ser permitidos."""
        validate_username("user_name-01", set())  # Não deve levantar

    def test_empty_raises(self):
        with pytest.raises(AuthError):
            validate_username("", set())
