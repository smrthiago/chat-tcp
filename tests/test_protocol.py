"""
Testes do módulo de protocolo (src/common/protocol.py).

Cobre: serialização, desserialização, validação e TCP framing.
"""
import socket
import struct
import threading
import pytest

from src.common.protocol import (
    Message,
    MessageType,
    recv_exactly,
    recv_message,
    send_message,
    make_ping,
    make_pong,
    make_auth_request,
    make_system,
    make_error,
)
from src.common.exceptions import ProtocolError, MessageTooLargeError
from src.common.config import Config


class TestMessageSerialization:
    """Testa serialização e desserialização de mensagens."""

    def test_to_json_roundtrip(self):
        """Mensagem serializada e desserializada deve ser equivalente."""
        original = Message(
            type=MessageType.MESSAGE,
            sender="alice",
            recipient="all",
            payload={"content": "Olá!", "encrypted": True},
            checksum="abc123",
        )
        json_str = original.to_json()
        restored = Message.from_json(json_str)

        assert restored.type == MessageType.MESSAGE
        assert restored.sender == "alice"
        assert restored.recipient == "all"
        assert restored.payload["content"] == "Olá!"
        assert restored.checksum == "abc123"

    def test_timestamp_auto_generated(self):
        """Timestamp deve ser gerado automaticamente se omitido."""
        msg = Message(type=MessageType.PING)
        assert msg.timestamp is not None
        assert "T" in msg.timestamp  # Formato ISO 8601

    def test_message_type_enum_serialization(self):
        """MessageType deve serializar como string no JSON."""
        msg = make_ping()
        json_str = msg.to_json()
        assert '"type": "PING"' in json_str

    def test_from_json_invalid_type(self):
        """Tipo de mensagem desconhecido deve levantar ProtocolError."""
        import json
        bad_json = json.dumps({"type": "INVALID_TYPE", "payload": {}})
        with pytest.raises(ProtocolError):
            Message.from_json(bad_json)

    def test_from_json_malformed(self):
        """JSON malformado deve levantar ProtocolError."""
        with pytest.raises(ProtocolError):
            Message.from_json("{ isso não é json válido }")

    def test_validate_valid_message(self):
        """Mensagem com campos obrigatórios deve ser válida."""
        msg = Message(type=MessageType.MESSAGE, payload={"content": "test"})
        assert msg.validate() is True

    def test_validate_missing_payload_type(self):
        """Payload deve ser dict."""
        msg = Message(type=MessageType.MESSAGE)
        msg.payload = "string inválida"  # type: ignore
        assert msg.validate() is False

    def test_factory_auth_request(self):
        """Factory make_auth_request deve popular payload corretamente."""
        msg = make_auth_request("joao", "chave123")
        assert msg.type == MessageType.AUTH
        assert msg.payload["username"] == "joao"
        assert msg.payload["encryption_key"] == "chave123"

    def test_factory_system(self):
        """Factory make_system deve popular evento e mensagem."""
        msg = make_system("user_joined", "Alice entrou", {"username": "Alice"})
        assert msg.type == MessageType.SYSTEM
        assert msg.payload["event"] == "user_joined"
        assert msg.payload["data"]["username"] == "Alice"


class TestTCPFraming:
    """
    Testa o mecanismo de framing TCP (length-prefix).

    Por que esses testes importam:
      TCP é um protocolo de stream. Sem framing, recv() pode retornar
      dados parciais ou múltiplas mensagens concatenadas. Esses testes
      garantem que send_message/recv_message lidam corretamente com isso.
    """

    def _create_connected_pair(self):
        """Cria um par de sockets conectados para testes."""
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("127.0.0.1", 0))
        server_sock.listen(1)
        port = server_sock.getsockname()[1]

        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect(("127.0.0.1", port))
        conn_sock, _ = server_sock.accept()
        server_sock.close()

        return client_sock, conn_sock

    def test_send_recv_roundtrip(self):
        """Mensagem enviada deve ser recebida identicamente."""
        sender, receiver = self._create_connected_pair()
        try:
            original = make_ping()
            send_message(sender, original)
            received = recv_message(receiver)
            assert received.type == MessageType.PING
        finally:
            sender.close()
            receiver.close()

    def test_multiple_messages_in_sequence(self):
        """Múltiplas mensagens devem ser recebidas na ordem correta."""
        sender, receiver = self._create_connected_pair()
        messages = [make_ping(), make_pong(), make_system("test", "Hello")]
        try:
            for msg in messages:
                send_message(sender, msg)
            for expected_type in [MessageType.PING, MessageType.PONG, MessageType.SYSTEM]:
                received = recv_message(receiver)
                assert received.type == expected_type
        finally:
            sender.close()
            receiver.close()

    def test_recv_exactly_reads_all_bytes(self):
        """recv_exactly deve ler exatamente N bytes mesmo em fragmentos."""
        sender, receiver = self._create_connected_pair()
        data = b"A" * 1000
        try:
            # Envia em fragmentos pequenos para simular fragmentação TCP
            def send_fragments():
                for i in range(0, len(data), 50):
                    sender.send(data[i:i+50])

            t = threading.Thread(target=send_fragments)
            t.start()
            received = recv_exactly(receiver, 1000)
            t.join()
            assert received == data
        finally:
            sender.close()
            receiver.close()

    def test_message_too_large_raises(self):
        """Mensagem maior que MAX_MESSAGE_SIZE deve levantar MessageTooLargeError."""
        sender, receiver = self._create_connected_pair()
        try:
            # Injeta um header indicando mensagem enorme
            huge_size = Config.MAX_MESSAGE_SIZE + 1
            header = struct.pack(">I", huge_size)
            sender.sendall(header)

            with pytest.raises(MessageTooLargeError):
                recv_message(receiver)
        finally:
            sender.close()
            receiver.close()
