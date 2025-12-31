#!/bin/bash

echo ""
echo "╔═══════════════════════════════════════════════╗"
echo "║            err_x509 - x509 SSL Fixer          ║"
echo "║          Fix Clash SSL certificate errors     ║"
echo "╚═══════════════════════════════════════════════╝"
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  macOS: brew install python"
    echo "  Arch: sudo pacman -S python"
    exit 1
fi

# Run err_x509
python3 -m err_x509 "$@"

exit_code=$?
echo ""

if [ $exit_code -eq 0 ]; then
    echo "✅ Operation completed successfully!"
else
    echo "❌ Operation failed!"
fi

exit $exit_code