# 🔒 Secure Channel

A secure P2P messenger with military-grade end-to-end encryption. Simple to use, but cryptographically robust tool for private communication.

## ⚡ Features

- 🛡️ **End-to-End encryption** using ChaCha20-Poly1305
- 🔑 **Secure key exchange** via X25519 (Curve25519)
- 🚀 **Two operation modes**: console (CLI) and graphical (GUI)
- 🌐 **P2P connection** - no intermediary servers
- 🔐 **Optional authentication** via Pre-Shared Key (PSK)
- 💪 **Quantum-resistant** (for symmetric encryption)

## 🔐 Cryptographic Algorithms

| Component | Algorithm | Security Level |
|-----------|-----------|----------------|
| Key Exchange | X25519 (Curve25519) | ~126 bits |
| Encryption | ChaCha20-Poly1305 | 256 bits |
| Key Derivation | HKDF-SHA256 | 256 bits |
| Authentication | PSK + AEAD | Depends on PSK |

**Time to break:** With proper configuration - practically impossible with modern methods (>10^60 years).

## 📦 Installation

### Requirements
- Python 3.8+
- cryptography library
- PyQt6 (for GUI mode)

### Quick Install
```bash
git clone https://github.com/qventymr/securechannel.git
cd securechannel
pip install -r requirements.txt
```

### requirements.txt
```
pyqt6 >= 6.9.1
cryptography >= 45.0.5
```

## 🚀 Usage

### Quick Start
```bash
# Launch with GUI (recommended)
python main.py

# Or explicitly
python main.py --gui
```

### CLI Mode

**Start as server:**
```bash
python main.py -p 12345 --psk "your-secret-password"
```

**Connect as client:**
```bash
python main.py 192.168.1.100 -p 12345 --psk "your-secret-password"
```

**Without password (less secure):**
```bash
# Server
python main.py -p 12345

# Client  
python main.py 192.168.1.100 -p 12345
```

### Advanced Usage

**Using environment variables:**
```bash
export ANON_PSK="my-super-secret-key"
python main.py -p 12345
```

**Server on specific interface:**
```bash
python main.py -l 127.0.0.1 -p 12345  # localhost only
python main.py -l 0.0.0.0 -p 12345     # all interfaces
```

## 🛡️ Security

### Security Levels

#### 🟢 Maximum Security
- Use **long PSK** (16+ characters)
- Exchange PSK via **secure channel**
- Verify peer identity outside the application

#### 🟡 Medium Security  
- Use **short PSK** (8+ characters)
- Suitable for communication with trusted parties

#### 🔴 Minimal Security
- **No PSK** - protection only against passive eavesdropping
- Vulnerable to man-in-the-middle attacks

### PSK Recommendations

| Length | Characters | Security | Time to Crack* |
|--------|------------|----------|----------------|
| 6 | a-z,0-9 | Weak | ~13 minutes |
| 8 | a-z,0-9 | Low | ~8 hours |
| 12 | a-z,A-Z,0-9 | Medium | ~87 years |
| 16+ | All symbols | High | Practically impossible |

*At 10^9 attempts per second

### Secure PSK Generation
```python
import secrets
import string

# Generate random PSK
alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
psk = ''.join(secrets.choice(alphabet) for _ in range(20))
print(f"Your PSK: {psk}")
```


## ⚠️ Limitations and Warnings

### What the application does NOT protect:
- ❌ Connection metadata (IP addresses, timing)
- ❌ Traffic analysis by message size
- ❌ Endpoint compromise
- ❌ Keyloggers and other malware

### Important Notes:
- 🔒 **PSK must remain secret**
- 🌐 **Use VPN/Tor** to hide IP addresses
- 💻 **Check devices** for malware
- 🔄 **Regularly change PSK**

## 🏗️ Architecture

```
┌─────────────────┐    Handshake      ┌─────────────────┐
│     Client      │◄──────────────────┤     Server      │
│                 │                   │                 │
│ ┌─────────────┐ │   Encrypted Data  │ ┌─────────────┐ │
│ │ X25519 Keys │ │◄──────────────────┤ │ X25519 Keys │ │
│ └─────────────┘ │                   │ └─────────────┘ │
│ ┌─────────────┐ │    ChaCha20-      │ ┌─────────────┐ │
│ │ChaCha20-    │ │    Poly1305       │ │ChaCha20-    │ │
│ │Poly1305     │ │                   │ │Poly1305     │ │
│ └─────────────┘ │                   │ └─────────────┘ │
└─────────────────┘                   └─────────────────┘
```

### Parameters:
- `HOST` - Server IP address (omit for server mode)
- `-p, --port` - Port number (required for CLI mode)
- `-l, --listen` - Listen address for server (default: 0.0.0.0)
- `--psk` - Pre-shared key for authentication
- `--gui` - Force GUI mode
- `--no-banner` - Hide startup banner

## 🔍 Security Analysis

### Cryptographic Strength:
- **X25519**: Equivalent to 3072-bit RSA
- **ChaCha20-Poly1305**: 256-bit security, AEAD construction
- **HKDF-SHA256**: Proper key derivation with salt support

### Attack Vectors:
1. **Weak PSK** - Use strong passwords (16+ chars)
2. **Man-in-the-Middle** - Verify peer identity out-of-band
3. **Traffic Analysis** - Use VPN/Tor for metadata protection
4. **Endpoint Security** - Keep systems updated and malware-free

### Threat Model:
- ✅ **Passive Eavesdropping**: Fully protected
- ✅ **Active Network Attacks**: Protected with strong PSK
- ⚠️ **Nation-State Adversaries**: Additional precautions needed
- ❌ **Quantum Computers**: X25519 vulnerable (ChaCha20 resistant)

## ⚖️ License

MIT License - free for any use.

## 🔗 Useful Links

- 📚 [Cryptography Library Documentation](https://cryptography.io/)
- 🔐 [X25519 Specification (RFC 7748)](https://tools.ietf.org/html/rfc7748)
- 🛡️ [ChaCha20-Poly1305 (RFC 8439)](https://tools.ietf.org/html/rfc8439)
- 🔑 [HKDF Standard (RFC 5869)](https://tools.ietf.org/html/rfc5869)
- 🎓 [Signal Protocol Documentation](https://signal.org/docs/)

## ⚠️ Disclaimer

This software is intended for educational and research purposes. The authors are not responsible for illegal use. Always comply with local laws when using cryptographic tools.

**Remember:** Absolute security does not exist. Use common sense and additional security measures.

---

<div align="center">

**💡 If this project was helpful, please give it a ⭐ star!**

**🛡️ Stay secure, stay private**

Made with ❤️ for privacy advocates worldwide

</div>