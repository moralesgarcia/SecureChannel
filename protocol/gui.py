import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from server_side import serve
from client_side import connect
from functions import send_frame, recv_frame

class NetworkThread(QThread):
    message_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connected = pyqtSignal()

    def __init__(self, is_server, host, port, psk):
        super().__init__()
        self.is_server = is_server
        self.host = host
        self.port = port
        self.psk = psk
        self.running = True
        self.conn = None
        self.chan = None

    def run(self):
        try:
            if self.is_server:
                self.conn, self.chan = serve(self.host, self.port, self.psk, 
                                           message_callback=True, error_callback=self.error_occurred.emit)
            else:
                self.conn, self.chan = connect(self.host, self.port, self.psk,
                                             message_callback=True, error_callback=self.error_occurred.emit)
            
            self.connected.emit()
            
            while self.running and self.conn:
                try:
                    self.conn.settimeout(0.5)
                    try:
                        data = recv_frame(self.conn)
                        if not data:
                            break
                        msg = self.chan.decrypt(data)
                        decoded_msg = msg.decode('utf-8', errors='replace')
                        self.message_received.emit(decoded_msg)
                    except TimeoutError:
                        continue
                    except Exception as e:
                        if self.running:
                            self.error_occurred.emit(f"Communication error: {e}")
                        break
                except Exception as e:
                    if self.running:
                        self.error_occurred.emit(f"Network error: {e}")
                    break
                    
        except Exception as e:
            self.error_occurred.emit(f"Connection failed: {e}")

    def send_message(self, message):
        if self.conn and self.chan and self.running:
            try:
                ct = self.chan.encrypt(message.encode('utf-8'))
                send_frame(self.conn, ct)
                return True
            except Exception as e:
                self.error_occurred.emit(f"Send error: {e}")
                return False
        return False

    def stop(self):
        self.running = False
        if self.conn:
            try:
                self.conn.close()
            except:
                pass

class MessengerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Secure Channel")
        self.setGeometry(100, 100, 700, 500)
        self.network_thread = None
        self.setup_styles()
        self.show_main_page()

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #2b2b2b; 
                color: #ffffff; 
                font-family: Arial, sans-serif;
            }
            QPushButton { 
                background-color: #1e90ff; 
                color: white; 
                padding: 12px 20px; 
                border-radius: 6px; 
                font-size: 14px;
                font-weight: bold;
                border: none;
                min-width: 120px;
            }
            QPushButton:hover { 
                background-color: #4682b4; 
            }
            QPushButton:pressed {
                background-color: #1c7ed6;
            }
            QLineEdit { 
                background-color: #3c3c3c; 
                color: white; 
                padding: 10px; 
                border-radius: 6px; 
                border: 1px solid #555;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #1e90ff;
            }
            QTextEdit { 
                background-color: #3c3c3c; 
                color: white; 
                border-radius: 6px; 
                border: 1px solid #555;
                font-size: 13px;
                line-height: 1.4;
            }
            QLabel { 
                font-size: 14px; 
                color: #ffffff;
            }
            QFormLayout QLabel {
                font-weight: bold;
            }
        """)

    def show_main_page(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        title = QLabel("Secure Channel")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Secure peer-to-peer communication")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #cccccc; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        server_btn = QPushButton("Start as Server")
        server_btn.clicked.connect(self.show_server_page)
        button_layout.addWidget(server_btn)

        client_btn = QPushButton("Connect as Client")
        client_btn.clicked.connect(self.show_client_page)
        button_layout.addWidget(client_btn)

        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)

    def show_server_page(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Server Configuration")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.server_port = QLineEdit("12345")
        self.server_psk = QLineEdit()
        self.server_psk.setEchoMode(QLineEdit.EchoMode.Password)
        self.server_psk.setPlaceholderText("Optional password for encryption")

        form_layout.addRow("Port:", self.server_port)
        form_layout.addRow("Password (PSK):", self.server_psk)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.show_main_page)
        back_btn.setStyleSheet("background-color: #666; min-width: 80px;")
        button_layout.addWidget(back_btn)

        start_btn = QPushButton("Start Server")
        start_btn.clicked.connect(self.start_server)
        button_layout.addWidget(start_btn)

        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)

    def show_client_page(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("💻 Client Configuration")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        self.client_ip = QLineEdit("localhost")
        self.client_port = QLineEdit("12345")
        self.client_psk = QLineEdit()
        self.client_psk.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_psk.setPlaceholderText("Optional password for encryption")

        form_layout.addRow("Server IP:", self.client_ip)
        form_layout.addRow("Port:", self.client_port)
        form_layout.addRow("Password (PSK):", self.client_psk)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.show_main_page)
        back_btn.setStyleSheet("background-color: #666; min-width: 80px;")
        button_layout.addWidget(back_btn)

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.start_client)
        button_layout.addWidget(connect_btn)

        layout.addLayout(button_layout)
        self.central_widget.setLayout(layout)

    def start_server(self):
        port_text = self.server_port.text().strip()
        psk = self.server_psk.text().strip()
        
        if not port_text:
            self.show_error("Please enter a port number")
            return
            
        try:
            port = int(port_text)
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            self.show_error(f"Invalid port number: {e}")
            return

        self.network_thread = NetworkThread(True, "0.0.0.0", port, psk if psk else None)
        self.show_chat_page("Server", f"Listening on port {port}")

    def start_client(self):
        ip = self.client_ip.text().strip()
        port_text = self.client_port.text().strip()
        psk = self.client_psk.text().strip()
        
        if not ip or not port_text:
            self.show_error("Please enter both IP address and port")
            return
            
        try:
            port = int(port_text)
            if port < 1 or port > 65535:
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            self.show_error(f"Invalid port number: {e}")
            return

        self.network_thread = NetworkThread(False, ip, port, psk if psk else None)
        self.show_chat_page("Client", f"Connecting to {ip}:{port}")

    def show_chat_page(self, mode, status_text):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        mode_label = QLabel(f"🔒 {mode} Mode")
        mode_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(mode_label)
        
        self.status_label = QLabel(status_text)
        self.status_label.setStyleSheet("color: #ffa500;")
        header_layout.addWidget(self.status_label)
        
        header_layout.addStretch()
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self.disconnect)
        disconnect_btn.setStyleSheet("background-color: #dc3545; min-width: 100px;")
        header_layout.addWidget(disconnect_btn)
        
        layout.addLayout(header_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 12))
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)
        self.central_widget.setLayout(layout)

        self.network_thread.message_received.connect(self.display_message)
        self.network_thread.error_occurred.connect(self.show_error_in_chat)
        self.network_thread.connected.connect(self.on_connected)
        self.network_thread.start()

        self.message_input.setFocus()

    def on_connected(self):
        self.status_label.setText("✅ Connected")
        self.status_label.setStyleSheet("color: #28a745;")
        self.chat_display.append("<i>Connected! You can now send messages.</i>")

    def send_message(self):
        message = self.message_input.text().strip()
        if message and self.network_thread:
            if self.network_thread.send_message(message):
                self.chat_display.append(f"<b>You:</b> {message}")
                self.message_input.clear()

    def display_message(self, message):
        self.chat_display.append(f"<b>Them:</b> {message}")

    def show_error_in_chat(self, error):
        self.chat_display.append(f"<span style='color: #dc3545;'><b>Error:</b> {error}</span>")
        self.status_label.setText("❌ Error")
        self.status_label.setStyleSheet("color: #dc3545;")

    def show_error(self, error):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(error)
        msg_box.setStyleSheet("QMessageBox { background-color: #2b2b2b; color: white; }")
        msg_box.exec()

    def disconnect(self):
        if self.network_thread:
            self.network_thread.stop()
            self.network_thread.wait(3000)
        self.show_main_page()

    def closeEvent(self, event):
        if self.network_thread:
            self.network_thread.stop()
            self.network_thread.wait(3000)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MessengerGUI()
    window.show()
    sys.exit(app.exec())