import argparse
import selectors
import socket
import sys
from functions import handshake_server, SecureChannel, send_frame, recv_frame

def set_tcp_keepalive(sock: socket.socket):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    except OSError:
        pass

def serve(host: str, port: int, psk: str | None, message_callback=None, error_callback=None):
    ls = socket.create_server((host, port), reuse_port=True)
    set_tcp_keepalive(ls)
    print(f"listening on {host}:{port}", file=sys.stderr)
    
    conn, addr = ls.accept()
    print(f"connection from {addr[0]}:{addr[1]}", file=sys.stderr)
    set_tcp_keepalive(conn)

    try:
        chan: SecureChannel = handshake_server(conn, psk)
    except Exception as e:
        if error_callback:
            error_callback(f"Handshake failed: {e}")
        conn.close()
        ls.close()
        raise

    if message_callback is not None:
        ls.close()
        return conn, chan

    sel = selectors.DefaultSelector()
    sel.register(conn, selectors.EVENT_READ)
    sel.register(sys.stdin, selectors.EVENT_READ)

    try:
        while True:
            for key, _ in sel.select():
                if key.fileobj is conn:
                    try:
                        data = recv_frame(conn)
                    except Exception:
                        return
                    try:
                        msg = chan.decrypt(data)
                    except Exception:
                        return
                    sys.stdout.buffer.write(msg)
                    sys.stdout.flush()
                else:
                    buf = sys.stdin.buffer.read1(65536) if hasattr(sys.stdin.buffer, "read1") else sys.stdin.buffer.read(65536)
                    if not buf:
                        return
                    ct = chan.encrypt(buf)
                    send_frame(conn, ct)
    finally:
        try:
            conn.close()
        except Exception:
            pass
        try:
            ls.close()
        except Exception:
            pass

def main():
    ap = argparse.ArgumentParser(description="Encrypted nc-like server")
    ap.add_argument("-l", "--listen", default="0.0.0.0", help="host to listen on (default 0.0.0.0)")
    ap.add_argument("-p", "--port", type=int, required=True, help="port to listen on")
    ap.add_argument("--psk", default=None, help="optional pre-shared key (or set ANON_PSK env)")
    args = ap.parse_args()
    serve(args.listen, args.port, args.psk)

if __name__ == "__main__":
    main()