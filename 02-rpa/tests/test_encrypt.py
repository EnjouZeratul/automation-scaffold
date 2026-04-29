import os
import json

from utils.encrypt import encrypt_params, decrypt_params


def test_encrypt_decrypt_roundtrip():
    os.environ["RPA_ENCRYPT_KEY"] = "test-secret-key-for-aes"
    data = {"user": "test", "token": "abc123"}
    encrypted = encrypt_params(data)
    decrypted = decrypt_params(encrypted)
    assert decrypted == data
