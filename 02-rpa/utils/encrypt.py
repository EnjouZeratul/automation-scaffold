from __future__ import annotations

import base64
import json
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def decrypt_params(encrypted: str, key: str | None = None) -> dict:
    key = key or os.getenv("RPA_ENCRYPT_KEY", "")
    if not key:
        raise ValueError("未提供加密密钥")
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
    aesgcm = AESGCM(key_bytes)
    raw = base64.b64decode(encrypted)
    nonce = raw[:12]
    ct = raw[12:]
    plaintext = aesgcm.decrypt(nonce, ct, None)
    return json.loads(plaintext.decode("utf-8"))


def encrypt_params(data: dict, key: str | None = None) -> str:
    key = key or os.getenv("RPA_ENCRYPT_KEY", "")
    if not key:
        raise ValueError("未提供加密密钥")
    key_bytes = key.encode("utf-8")[:32].ljust(32, b"\0")
    aesgcm = AESGCM(key_bytes)
    plaintext = json.dumps(data, ensure_ascii=False).encode("utf-8")
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ct).decode("utf-8")
