# err_x509 - SSL Certificate Bypass Tool

A simple utility to automatically add `skip-cert-verify: true` to all proxy entries in YAML configuration files. Designed specifically for fixing SSL/TLS certificate verification issues in proxy clients like Clash, etc.

## ✨ Features

- ✅ Automatically adds `skip-cert-verify: true` to all proxy entries
- ✅ Preserves original YAML formatting
- ✅ Works with any proxy type (trojan, vmess, shadowsocks, etc.)
- ✅ No installation required - single executable file
- ✅ Cross-platform (Windows, Linux, macOS)
- ✅ Simple and fast

## 📦 Download

### Windows Users
1. Download `err_x509.exe` from [Releases](https://github.com/13winged/err_x509/releases)
2. Place it in any folder

### From Source
```bash
git clone https://github.com/13winged/err_x509.git
cd err_x509
go build -o err_x509.exe main.go
```

## 🚀 Quick Start Guide

### For Windows Users (Easiest Method)

1. **Download** `err_x509.exe` from the Releases section
2. **Create** a file named `x509_no_fix.yaml` in the same folder as `err_x509.exe`
3. **Copy** your YAML configuration into `x509_no_fix.yaml`
4. **Run** `err_x509.exe` (double-click)
5. **Get** your fixed configuration in `x509_fixed.yaml`

### Step-by-Step Visual Guide

```
1. Folder Structure:
   📁 YourFolder/
   ├── 📄 err_x509.exe      (the program)
   ├── 📄 x509_no_fix.yaml  (your config - you create this)
   
2. After running err_x509.exe:
   📁 YourFolder/
   ├── 📄 err_x509.exe
   ├── 📄 x509_no_fix.yaml
   └── 📄 x509_fixed.yaml   (created automatically - use this!)
```

## 📝 Usage Example

### Input File (`x509_no_fix.yaml`):
```yaml
port: 7890
socks-port: 7891
proxies:
  - { name: Moldova, type: trojan, server: example.com, port: 443, password: your-password-here }
  - { name: Netherlands, type: trojan, server: example2.com, port: 443, password: your-password-here }
```

### Output File (`x509_fixed.yaml`):
```yaml
port: 7890
socks-port: 7891
proxies:
  - { name: Moldova, type: trojan, server: example.com, port: 443, password: your-password-here, skip-cert-verify: true }
  - { name: Netherlands, type: trojan, server: example2.com, port: 443, password: your-password-here, skip-cert-verify: true }
```

## 🛠 Advanced Usage

### For Developers / Linux/Mac Users

#### Build from source:
```bash
# Clone repository
git clone https://github.com/13winged/err_x509.git
cd err_x509

# Build for your platform
go build -o err_x509 main.go
```

#### Cross-compilation:
```bash
# Windows (from Linux/Mac)
GOOS=windows GOARCH=amd64 go build -o err_x509.exe main.go

# Linux
GOOS=linux GOARCH=amd64 go build -o err_x509_linux main.go

# macOS
GOOS=darwin GOARCH=amd64 go build -o err_x509_mac main.go
```

#### Command Line Usage:
```bash
# After building, run:
./err_x509    # Linux/Mac
err_x509.exe  # Windows
```

### Batch Processing (Advanced)

If you have multiple configs:
1. Create a batch file `process_all.bat`:
```batch
@echo off
for %%f in (*_no_fix.yaml) do (
    copy "%%f" "x509_no_fix.yaml"
    err_x509.exe
    move "x509_fixed.yaml" "%%~nf_fixed.yaml"
)
pause
```

## ❓ Troubleshooting

### Common Issues & Solutions:

| Problem | Solution |
|---------|----------|
| "File 'x509_no_fix.yaml' not found!" | Make sure the file exists in the same folder as err_x509.exe |
| No proxies were processed | Check your YAML format. Each proxy should be on one line like: `- { name: ..., type: ..., server: ..., port: ..., password: ... }` |
| Antivirus blocks the .exe | Add err_x509.exe to your antivirus exceptions (it's safe!) |
| "Access denied" error | Run as administrator or check folder permissions |
| Output file not created | Check if you have write permissions in the folder |

### Checking Your YAML Format:

**Correct format (will work):**
```yaml
proxies:
  - { name: Server1, type: trojan, server: s1.example.com, port: 443, password: pass1 }
```

**Incorrect format (won't work):**
```yaml
proxies:
  - name: Server1
    type: trojan
    server: s1.example.com
    port: 443
    password: pass1
```

## 🔧 Technical Details

### What does `skip-cert-verify: true` do?
This option disables SSL/TLS certificate verification for proxy connections. Use it when:
- You're getting "x509 certificate" errors
- Using self-signed certificates
- Certificate authority is not recognized
- Working in testing environments

**⚠️ Security Note:** Disabling certificate verification reduces security. Only use this for testing or with trusted proxies.

### Supported Proxy Types:
- ✅ Trojan
- ✅ VMess
- ✅ Shadowsocks
- ✅ SOCKS5
- ✅ HTTP/HTTPS
- ✅ Any other type using the same YAML format

## 📁 Project Structure

```
err_x509/
├── main.go                 # Source code
├── go.mod                 # Go module file
├── README.md              # This file
├── build.bat              # Windows build script
└── example_x509_no_fix.yaml # Example configuration
```

## Short Version (for those who want just instructions):

```markdown
# Quick Usage Guide

1. **Download** `err_x509.exe` from Releases
2. **Place** it in any folder
3. **Create** `x509_no_fix.yaml` in the same folder
4. **Copy** your YAML config into that file
5. **Run** `err_x509.exe`
6. **Use** the generated `x509_fixed.yaml`

Example input:
```yaml
proxies:
  - { name: MyServer, type: trojan, server: srv.com, port: 443, password: xxx }
```

Example output:
```yaml
proxies:
  - { name: MyServer, type: trojan, server: srv.com, port: 443, password: xxx, skip-cert-verify: true }
```
```