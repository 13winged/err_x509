err_x509 v1.1 - SSL Certificate Bypass Tool

A simple, safe, and reliable utility to automatically add `skip-cert-verify: true` to all proxy entries in YAML configuration files. Perfect for fixing SSL/TLS certificate verification issues in Clash, NekoBox, V2RayXS and other proxy clients.

- ✅ **TLS Safe**: Preserves all TLS/SSL parameters (sni, alpn, fingerprint, etc.)
- ✅ **Smart Processing**: Handles both compact `{ ... }` and multi-line formats
- ✅ **Backup Creation**: Automatically creates backup of original file
- ✅ **Statistics**: Shows detailed processing statistics
- ✅ **No Format Corruption**: Maintains original YAML structure
- ✅ **Simple**: Single executable, no installation required
- ✅ **Fast**: Processes even large configs in milliseconds

## 🚀 Quick Start

### For Windows Users
1. **Download** `err_x509.exe` from [Releases](https://github.com/13winged/err_x509/releases)
2. **Create** a file named `x509_no_fix.yaml` in the same folder
3. **Copy** your YAML configuration into it
4. **Run** `err_x509.exe` (double-click)
5. **Use** the generated `x509_fixed.yaml`

### Step-by-Step Visual Guide
BEFORE: AFTER:
📁 YourFolder/ 📁 YourFolder/
├── 📄 err_x509.exe ├── 📄 err_x509.exe
└── 📄 x509_no_fix.yaml ├── 📄 x509_no_fix.yaml
├── 📄 x509_fixed.yaml ← USE THIS!
└── 📄 x509_no_fix.yaml.backup

text

## 📝 Usage Example

### Input (`x509_no_fix.yaml`):
```yaml
port: 7890
proxies:
  - { name: Server1, type: trojan, server: s1.com, port: 443, password: pass1, sni: s1.com, alpn: ["h2"] }
  - { name: Server2, type: vmess, server: s2.com, port: 443, uuid: xxxxx, tls: true }
Output (x509_fixed.yaml):
yaml
port: 7890
proxies:
  - { name: Server1, type: trojan, server: s1.com, port: 443, password: pass1, sni: s1.com, alpn: ["h2"], skip-cert-verify: true }
  - { name: Server2, type: vmess, server: s2.com, port: 443, uuid: xxxxx, tls: true, skip-cert-verify: true }
Notice: All original TLS parameters (sni:, alpn:) are preserved!

🛠 Advanced Usage
Build from Source
bash
# Clone repository
git clone https://github.com/13winged/err_x509.git
cd err_x509

# Build for Windows
go build -o err_x509.exe main.go

# Build for Linux
GOOS=linux GOARCH=amd64 go build -o err_x509_linux main.go

# Build for macOS
GOOS=darwin GOARCH=amd64 go build -o err_x509_mac main.go
Batch Processing
Create process.bat:

batch
@echo off
for %%f in (*.yaml) do (
    if not "%%f"=="x509_fixed.yaml" (
        copy "%%f" "x509_no_fix.yaml"
        err_x509.exe
        move "x509_fixed.yaml" "%%~nf_fixed.yaml"
    )
)
🔧 Technical Details
What Does It Do?
Adds skip-cert-verify: true to all proxy entries while:

Preserving existing TLS parameters

Maintaining YAML structure

Creating backups

Showing processing statistics

Supported Proxy Types
✅ Trojan (with all TLS options)
✅ VMess (with TLS/WS settings)
✅ Shadowsocks
✅ SOCKS5/HTTP
✅ Any YAML proxy format

Preserved TLS Parameters
sni: - Server Name Indication

alpn: - Application-Layer Protocol Negotiation

fingerprint: - TLS fingerprint

client-fingerprint: - Client fingerprint

ws-opts: - WebSocket options

network: - Transport protocol

All other proxy parameters

📊 Version History
v1.1 (Current)
TLS Safe: Preserves all TLS/SSL parameters

Backup system: Creates .backup files

Statistics: Shows processing details

Improved detection: Better proxy recognition

Bug fixes: Various edge cases handled

v1.0 (Initial)
Basic functionality

Compact format support

Simple processing

❓ FAQ
Q: Does it modify my original file?
A: No! It creates a new file x509_fixed.yaml. Original file is backed up as x509_no_fix.yaml.backup.

Q: What if a proxy already has skip-cert-verify?
A: It skips it and shows in statistics. No duplicate entries.

Q: Does it work with Clash.Meta?
A: Yes! Preserves all Clash.Meta specific parameters.

Q: Is it safe?
A: Absolutely. It only adds one parameter, doesn't remove or modify existing ones.

Q: What if I have 100+ proxies?
A: Works perfectly. Processes all proxies quickly.

🐛 Troubleshooting
Problem	Solution
"File not found"	Ensure x509_no_fix.yaml exists in same folder
"No proxies processed"	Check your YAML format (use compact { ... } format)
Antivirus warning	Add to exclusions (open-source, safe code)
Output file missing	Run as Administrator or check permissions
