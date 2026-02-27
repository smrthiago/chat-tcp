"""
Testes do módulo de criptografia (src/common/crypto.py).
"""
import pytest
from src.common.crypto import CryptoManager, _constant_time_compare
from src.common.exceptions import CryptoError


class TestCryptoManager:
    """Testa geração de chaves, encrypt e decrypt."""

    def test_generates_key_on_init(self):
        """CryptoManager sem argumento deve gerar chave automaticamente."""
        crypto = CryptoManager()
        key = crypto.get_key_b64()
        assert key is not None
        assert len(key) > 0
        assert isinstance(key, str)

    def test_different_instances_have_different_keys(self):
        """Duas instâncias independentes devem ter chaves diferentes."""
        c1 = CryptoManager()
        c2 = CryptoManager()
        assert c1.get_key_b64() != c2.get_key_b64()

    def test_encrypt_produces_different_output(self):
        """Texto em claro e criptografado devem ser diferentes."""
        crypto = CryptoManager()
        plaintext = "Mensagem secreta"
        encrypted = crypto.encrypt(plaintext)
        assert encrypted != plaintext.encode("utf-8")

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypt seguido de decrypt deve retornar o texto original."""
        crypto = CryptoManager()
        original = "Olá, mundo! 🌍"
        encrypted = crypto.encrypt(original)
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == original

    def test_encrypt_decrypt_str_roundtrip(self):
        """Versões str (base64) também devem funcionar."""
        crypto = CryptoManager()
        original = "Testando versão string"
        encrypted_str = crypto.encrypt_to_str(original)
        decrypted = crypto.decrypt_from_str(encrypted_str)
        assert decrypted == original

    def test_key_export_import(self):
        """Chave exportada deve funcionar em nova instância."""
        c1 = CryptoManager()
        key_b64 = c1.get_key_b64()
        c2 = CryptoManager(key_b64=key_b64)

        original = "Mensagem cruzada entre instâncias"
        encrypted = c1.encrypt(original)
        decrypted = c2.decrypt(encrypted)
        assert decrypted == original

    def test_wrong_key_raises_crypto_error(self):
        """Chave incorreta deve levantar CryptoError."""
        c1 = CryptoManager()
        c2 = CryptoManager()  # Chave diferente

        encrypted = c1.encrypt("mensagem")
        with pytest.raises(CryptoError):
            c2.decrypt(encrypted)

    def test_corrupted_token_raises_crypto_error(self):
        """Token corrompido deve levantar CryptoError."""
        crypto = CryptoManager()
        with pytest.raises(CryptoError):
            crypto.decrypt(b"isso-nao-e-um-token-valido")

    def test_invalid_key_raises_crypto_error(self):
        """Chave inválida na construção deve levantar CryptoError."""
        with pytest.raises(CryptoError):
            CryptoManager(key_b64="chave-invalida-123")

    def test_empty_string_encryption(self):
        """String vazia deve ser criptografável."""
        crypto = CryptoManager()
        encrypted = crypto.encrypt("")
        assert crypto.decrypt(encrypted) == ""

    def test_unicode_encryption(self):
        """Caracteres Unicode (incluindo emojis) devem ser criptografados."""
        crypto = CryptoManager()
        original = "你好世界 🔐 Ünïcödé"
        assert crypto.decrypt(crypto.encrypt(original)) == original

    def test_long_message_encryption(self):
        """Mensagem longa deve ser criptografável."""
        crypto = CryptoManager()
        original = "A" * 10000
        assert crypto.decrypt(crypto.encrypt(original)) == original


class TestChecksum:
    """Testa geração e verificação de checksum SHA-256."""

    def test_checksum_deterministic(self):
        """Mesmo input deve produzir mesmo checksum."""
        data = "mensagem de teste"
        assert CryptoManager.generate_checksum(data) == CryptoManager.generate_checksum(data)

    def test_different_data_different_checksum(self):
        """Dados diferentes devem produzir checksums diferentes."""
        c1 = CryptoManager.generate_checksum("abc")
        c2 = CryptoManager.generate_checksum("abd")
        assert c1 != c2

    def test_verify_valid_checksum(self):
        """Checksum correto deve retornar True."""
        data = "teste de integridade"
        checksum = CryptoManager.generate_checksum(data)
        assert CryptoManager.verify_checksum(data, checksum) is True

    def test_verify_invalid_checksum(self):
        """Checksum incorreto deve retornar False."""
        assert CryptoManager.verify_checksum("dados", "checksum_errado") is False

    def test_checksum_is_hex_string(self):
        """Checksum deve ser string hexadecimal de 64 chars (SHA-256)."""
        checksum = CryptoManager.generate_checksum("test")
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)


class TestConstantTimeCompare:
    """Testa comparação em tempo constante (anti timing attacks)."""

    def test_equal_strings(self):
        assert _constant_time_compare("abc", "abc") is True

    def test_different_strings(self):
        assert _constant_time_compare("abc", "abd") is False

    def test_different_lengths(self):
        assert _constant_time_compare("ab", "abc") is False
