"""
Smoke test local — verifica que servidor e cliente funcionam de ponta-a-ponta.
Roda sem interação do usuário: conecta 2 clientes, troca mensagens, desconecta.
"""
import socket
import sys
import time
import threading

from src.common.crypto import CryptoManager
from src.common.protocol import (
    MessageType,
    make_auth_request,
    make_chat_message,
    make_disconnect,
    recv_message,
    send_message,
)

PORT = 15099
HOST = "127.0.0.1"
PASS_MARK = "[OK]"
FAIL_MARK = "[FAIL]"
results = []


def log(ok: bool, name: str, detail: str = ""):
    icon = PASS_MARK if ok else FAIL_MARK
    results.append(ok)
    detail_str = f" -- {detail}" if detail else ""
    print(f"  {icon} {name}{detail_str}")


def connect_and_auth(username: str):
    crypto = CryptoManager()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5.0)
    sock.connect((HOST, PORT))
    send_message(sock, make_auth_request(username, crypto.get_key_b64()))
    resp = recv_message(sock)
    return sock, crypto, resp


def start_server():
    from src.server.server import ChatServer
    server = ChatServer(host=HOST, port=PORT, max_clients=10)
    t = threading.Thread(target=server.start, daemon=True)
    t.start()
    time.sleep(0.5)
    return server


def main():
    print()
    print("=" * 55)
    print("  Chat TCP -- Smoke Test Local")
    print("=" * 55)
    print()

    # 1. Inicia servidor
    print("Iniciando servidor...")
    server = start_server()
    log(True, "Servidor iniciado", f"{HOST}:{PORT}")

    # ── 2. Conecta cliente Alice ──────────────────────────────────
    try:
        alice_sock, alice_crypto, alice_resp = connect_and_auth("Alice")
        ok = alice_resp.type == MessageType.AUTH and \
             alice_resp.payload.get("status") == "success"
        log(ok, "Alice autenticou", "status=success")
    except Exception as e:
        log(False, "Alice autenticou", str(e))
        return

    # ── 3. Conecta cliente Bob ───────────────────────────────────
    try:
        bob_sock, bob_crypto, bob_resp = connect_and_auth("Bob")
        ok = bob_resp.type == MessageType.AUTH and \
             bob_resp.payload.get("status") == "success"
        log(ok, "Bob autenticou", "status=success")
    except Exception as e:
        log(False, "Bob autenticou", str(e))
        return

    time.sleep(0.2)

    # ── 4. Alice envia mensagem de broadcast ─────────────────────
    try:
        bob_received = []

        def bob_listen():
            bob_sock.settimeout(3.0)
            try:
                while True:
                    msg = recv_message(bob_sock)
                    if msg.type == MessageType.MESSAGE:
                        plain = bob_crypto.decrypt_from_str(msg.payload.get("content", ""))
                        bob_received.append(plain)
                        break
                    elif msg.type == MessageType.SYSTEM:
                        continue
            except Exception:
                pass

        t = threading.Thread(target=bob_listen, daemon=True)
        t.start()

        # Alice consome SYSTEM de Bob entrar
        alice_sock.settimeout(1.0)
        try:
            recv_message(alice_sock)
        except Exception:
            pass
        alice_sock.settimeout(5.0)

        # Alice envia mensagem de broadcast
        content = "Ola Bob! Criptografia Fernet AES-128"
        encrypted = alice_crypto.encrypt_to_str(content)
        send_message(alice_sock, make_chat_message(
            sender="Alice", content=content, encrypted_content=encrypted
        ))
        t.join(timeout=3.0)

        ok = content in bob_received
        log(ok, "Broadcast: Alice -> Bob (criptografado)", f"'{content[:36]}'") 
    except Exception as e:
        log(False, "Broadcast Alice → Bob", str(e))

    # ── 5. Username duplicado é rejeitado ─────────────────────────
    try:
        dup_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dup_sock.settimeout(5.0)
        dup_sock.connect((HOST, PORT))
        dup_crypto = CryptoManager()
        send_message(dup_sock, make_auth_request("Alice", dup_crypto.get_key_b64()))
        resp = recv_message(dup_sock)
        ok = resp.type == MessageType.ERROR and resp.payload.get("code") == "AUTH_FAILED"
        log(ok, "Username duplicado rejeitado", "AUTH_FAILED recebido")
        dup_sock.close()
    except Exception as e:
        log(False, "Username duplicado rejeitado", str(e))

    # 6. Criptografia Fernet roundtrip
    try:
        c = CryptoManager()
        original = "Mensagem unicode e especial: Ola!"
        decrypted = c.decrypt(c.encrypt(original))
        log(decrypted == original, "Criptografia Fernet roundtrip", "AES-128-CBC + HMAC")
    except Exception as e:
        log(False, "Criptografia Fernet roundtrip", str(e))

    # ── 7. Checksum integridade ──────────────────────────────────
    try:
        data = "integridade"
        cs = CryptoManager.generate_checksum(data)
        valid = CryptoManager.verify_checksum(data, cs)
        invalid = not CryptoManager.verify_checksum(data, "checksum_errado")
        log(valid and invalid, "Checksum SHA-256", "verifica válido e inválido")
    except Exception as e:
        log(False, "Checksum SHA-256", str(e))

    # ── 8. Desconexão limpa ───────────────────────────────────────
    try:
        send_message(alice_sock, make_disconnect("Alice"))
        alice_sock.close()
        bob_sock.close()
        time.sleep(0.4)
        count = server.get_client_count()
        log(count == 0, "Desconexão limpa", f"{count} clientes restantes após close")
    except Exception as e:
        log(False, "Desconexão limpa", str(e))

    # ── 9. Shutdown do servidor ──────────────────────────────────
    try:
        server.shutdown()
        time.sleep(0.2)
        log(not server.running, "Graceful shutdown", "server.running = False")
    except Exception as e:
        log(False, "Graceful shutdown", str(e))

    # ── Resultado final ──────────────────────────────────────────
    total = len(results)
    passed = sum(results)
    failed = total - passed

    print()
    print("=" * 55)
    if failed == 0:
        print(f"  SUCESSO: {passed}/{total} testes passaram -- TUDO OK!")
    else:
        print(f"  ATENCAO: {passed}/{total} passaram -- {failed} FALHOU")
    print("=" * 55)
    print()
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
