import os
import struct
import socket
from dataclasses import dataclass
from typing import Optional
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

PROTO_TAG = b"secure-channel"


def get_psk_bytes(psk: Optional[str]) -> bytes:
    if psk is None:
        psk = os.environ.get("ANON_PSK", "")
    if isinstance(psk, str):
        psk = psk.encode('utf-8')
    return psk

def hkdf_derive(shared_secret: bytes, psk: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=psk if psk else None,
        info=PROTO_TAG,
    )
    return hkdf.derive(shared_secret)

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed")
        buf.extend(chunk)
    return bytes(buf)

def send_frame(sock: socket.socket, payload: bytes) -> None:
    sock.sendall(struct.pack("!I", len(payload)) + payload)

def recv_frame(sock: socket.socket) -> bytes:
    (length,) = struct.unpack("!I", recv_exact(sock, 4))
    return recv_exact(sock, length)

@dataclass
class SecureChannel:
    aead: ChaCha20Poly1305
    send_ctr: int = 0
    recv_ctr: int = 0

    def _nonce(self, ctr: int) -> bytes:
        return (0).to_bytes(4, "big") + ctr.to_bytes(8, "big")

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        ct = self.aead.encrypt(self._nonce(self.send_ctr), plaintext, aad)
        self.send_ctr += 1
        return ct

    def decrypt(self, ciphertext: bytes, aad: bytes = b"") -> bytes:
        pt = self.aead.decrypt(self._nonce(self.recv_ctr), ciphertext, aad)
        self.recv_ctr += 1
        return pt

def handshake_client(sock: socket.socket, psk: Optional[str]) -> SecureChannel:
    client_priv = x25519.X25519PrivateKey.generate()
    client_pub = client_priv.public_key().public_bytes_raw()
    send_frame(sock, client_pub)

    server_pub = recv_frame(sock)
    if len(server_pub) != 32:
        raise ValueError("invalid server public key length")

    shared = client_priv.exchange(x25519.X25519PublicKey.from_public_bytes(server_pub))
    key = hkdf_derive(shared, get_psk_bytes(psk))
    return SecureChannel(ChaCha20Poly1305(key))

def handshake_server(sock: socket.socket, psk: Optional[str]) -> SecureChannel:
    client_pub = recv_frame(sock)
    if len(client_pub) != 32:
        raise ValueError("invalid client public key length")

    server_priv = x25519.X25519PrivateKey.generate()
    server_pub = server_priv.public_key().public_bytes_raw()
    send_frame(sock, server_pub)

    shared = server_priv.exchange(x25519.X25519PublicKey.from_public_bytes(client_pub))
    key = hkdf_derive(shared, get_psk_bytes(psk))
    return SecureChannel(ChaCha20Poly1305(key))