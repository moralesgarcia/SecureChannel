import argparse
import selectors
import socket
import sys
from functions import handshake_client, SecureChannel, send_frame, recv_frame

def set_tcp_keepalive(sock: socket.socket):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    except OSError:
        pass

def connect(host: str, port: int, psk: str | None, message_callback=None, error_callback=None):
    s = socket.create_connection((host, port))
    set_tcp_keepalive(s)

    try:
        chan: SecureChannel = handshake_client(s, psk)
    except Exception as e:
        if error_callback:
            error_callback(f"Handshake failed: {e}")
        s.close()
        raise

    if message_callback is not None:
        return s, chan

    sel = selectors.DefaultSelector()
    sel.register(s, selectors.EVENT_READ)
    sel.register(sys.stdin, selectors.EVENT_READ)

    try:
        while True:
            for key, _ in sel.select():
                if key.fileobj is s:
                    try:
                        data = recv_frame(s)
                    except Exception:
                        return
                    try:
                        msg = chan.decrypt(data)
                    except Exception as e:
                        print(f"Decryption error: {e}", file=sys.stderr)
                        return
                    sys.stdout.buffer.write(msg)
                    sys.stdout.flush()
                else:
                    buf = sys.stdin.buffer.read1(65536) if hasattr(sys.stdin.buffer, "read1") else sys.stdin.buffer.read(65536)
                    if not buf:
                        return
                    ct = chan.encrypt(buf)
                    send_frame(s, ct)
    finally:
        try:
            s.close()
        except Exception:
            pass

def main():
    ap = argparse.ArgumentParser(description="Encrypted nc-like client")
    ap.add_argument("host", help="server host")
    ap.add_argument("-p", "--port", type=int, required=True, help="server port")
    ap.add_argument("--psk", default=None, help="optional pre-shared key (or set ANON_PSK env)")
    args = ap.parse_args()
    connect(args.host, args.port, args.psk)

if __name__ == "__main__":
    main()