#!/usr/bin/env python3
import sys
import os
import argparse
from typing import Optional

sys.path.append(os.path.join(os.path.dirname(__file__), 'protocol'))

def check_dependencies():
    missing = []
    try:
        import cryptography
    except ImportError:
        missing.append("cryptography")
    gui_available = True
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError:
        gui_available = False
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install them with: pip install -r requirements.txt")
        sys.exit(1)
    return gui_available

def launch_gui():
    try:
        from protocol import gui
        from PyQt6.QtWidgets import QApplication
        print("Starting GUI mode...")
        app = QApplication(sys.argv)
        window = gui.MessengerGUI()
        window.show()
        sys.exit(app.exec())
    except ImportError as e:
        print(f"GUI launch error: {e}")
        print("Install PyQt6: pip install PyQt6")
        sys.exit(1)

def launch_server(listen_host: str, port: int, psk: Optional[str]):
    try:
        from protocol import server_side
        print(f"Starting server on {listen_host}:{port}")
        if psk:
            print("PSK authentication enabled")
        else:
            print("PSK not set - connection is less secure")
        server_side.serve(listen_host, port, psk)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

def launch_client(host: str, port: int, psk: Optional[str]):
    try:
        from protocol import client_side
        print(f"Connecting to {host}:{port}")
        if psk:
            print("PSK authentication enabled")
        else:
            print("PSK not set - connection is less secure")
        client_side.connect(host, port, psk)
    except KeyboardInterrupt:
        print("\nConnection closed by user")
    except Exception as e:
        print(f"Connection error: {e}")
        sys.exit(1)

def show_banner():
    import pyfiglet
    banner = pyfiglet.figlet_format("Secure Channel")
    print(banner)

def main():
    gui_available = check_dependencies()
    parser = argparse.ArgumentParser(
        description="Encrypted P2P Messenger",
        epilog="Examples:\n"
               "  %(prog)s --gui                    # GUI mode\n"
               "  %(prog)s -p 12345                 # Server on port 12345\n"
               "  %(prog)s 192.168.1.100 -p 12345  # Client to server\n"
               "  %(prog)s -p 12345 --psk secret123 # Server with PSK",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("host",
                       nargs='?',
                       default=None,
                       help="Server IP to connect (if not specified - server mode)")
    parser.add_argument("-p", "--port",
                       type=int,
                       help="Port to connect/listen")
    parser.add_argument("-l", "--listen",
                       default="0.0.0.0",
                       help="Server listen address (default: 0.0.0.0)")
    parser.add_argument("--psk",
                       default=None,
                       help="Pre-shared key for additional security")
    parser.add_argument("--gui",
                       action="store_true",
                       help="Start graphical interface")
    parser.add_argument("--no-banner",
                       action="store_true",
                       help="Hide banner")
    parser.add_argument("--version",
                       action="version",
                       version="%(prog)s 1.0.0")
    args = parser.parse_args()
    if not args.no_banner:
        show_banner()
    if args.gui:
        if not gui_available:
            print("GUI not available. Install PyQt6: pip install PyQt6")
            print("Or use CLI mode without --gui flag")
            sys.exit(1)
        launch_gui()
    elif args.port is None:
        if gui_available:
            print("Port not specified. Starting GUI mode...")
            print("For CLI mode specify port: python main.py -p 12345")
            launch_gui()
        else:
            print("Specify port for CLI mode: python main.py -p 12345")
            parser.print_help()
            sys.exit(1)
    elif args.host is None:
        psk = args.psk or os.environ.get("ANON_PSK")
        launch_server(args.listen, args.port, psk)
    else:
        psk = args.psk or os.environ.get("ANON_PSK")
        launch_client(args.host, args.port, psk)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)
