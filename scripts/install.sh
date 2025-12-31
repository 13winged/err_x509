#!/bin/bash

# err_x509 installation script
# Works on Linux, macOS, and Windows (with WSL/Git Bash)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Icons
CHECK="✅"
CROSS="❌"
INFO="📦"
WARNING="⚠️"
ROCKET="🚀"

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════╗"
echo "║            err_x509 Installer                 ║"
echo "║          Fix Clash SSL certificate errors     ║"
echo "╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print colored messages
print_status() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}${WARNING} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO} $1${NC}"
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS="Linux" ;;
        Darwin*)    OS="macOS" ;;
        CYGWIN*|MINGW*) OS="Windows" ;;
        *)          OS="Unknown" ;;
    esac
    echo "$OS"
}

# Check Python installation
check_python() {
    print_info "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        print_status "Python $PYTHON_VERSION found"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
        PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        if [[ $PYTHON_VERSION == 3.* ]]; then
            print_status "Python $PYTHON_VERSION found"
        else
            print_error "Python 3 is required. Found Python $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python not found!"
        return 1
    fi
    return 0
}

# Check pip installation
check_pip() {
    print_info "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
        print_status "pip3 found"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
        print_status "pip found"
    else
        print_warning "pip not found. Attempting to install..."
        if [ "$OS" = "Linux" ]; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif [ "$OS" = "macOS" ]; then
            brew install python3
        elif [ "$OS" = "Windows" ]; then
            print_error "Please install pip manually from https://pip.pypa.io"
            return 1
        fi
        PIP_CMD="pip3"
    fi
    return 0
}

# Install err_x509
install_err_x509() {
    print_info "Installing err_x509..."
    
    # Check if we're in the project directory
    if [ -f "pyproject.toml" ] && [ -d "err_x509" ]; then
        print_info "Installing from source..."
        $PIP_CMD install -e .
    else
        print_info "Installing from PyPI..."
        $PIP_CMD install err-x509
    fi
    
    # Verify installation
    if command -v err_x509 &> /dev/null || $PYTHON_CMD -m err_x509 --version &> /dev/null; then
        print_status "err_x509 installed successfully!"
    else
        print_error "Installation verification failed"
        return 1
    fi
    return 0
}

# Create launcher scripts
create_launchers() {
    print_info "Creating launcher scripts..."
    
    # Create scripts directory if it doesn't exist
    mkdir -p scripts
    
    # Linux/macOS shell script
    cat > scripts/err_x509.sh << 'EOF'
#!/bin/bash
python3 -m err_x509 "$@"
EOF
    chmod +x scripts/err_x509.sh
    
    # Windows batch script
    cat > scripts/err_x509.bat << 'EOF'
@echo off
python -m err_x509 %*
EOF
    
    # Windows PowerShell script
    cat > scripts/err_x509.ps1 << 'EOF'
#Requires -Version 3.0
python -m err_x509 @args
EOF
    
    print_status "Launcher scripts created in scripts/ directory"
}

# Setup shell completion
setup_completion() {
    print_info "Setting up shell completion..."
    
    # Detect shell
    SHELL_NAME=$(basename "$SHELL")
    
    case "$SHELL_NAME" in
        bash)
            COMPLETION_DIR="$HOME/.bash_completion.d"
            mkdir -p "$COMPLETION_DIR"
            _ERR_X509_COMPLETE=bash_source err_x509 > "$COMPLETION_DIR/err_x509-completion.bash"
            echo "source $COMPLETION_DIR/err_x509-completion.bash" >> "$HOME/.bashrc" 2>/dev/null
            print_status "Bash completion installed"
            ;;
        zsh)
            COMPLETION_DIR="$HOME/.zsh/completions"
            mkdir -p "$COMPLETION_DIR"
            _ERR_X509_COMPLETE=zsh_source err_x509 > "$COMPLETION_DIR/_err_x509"
            echo "fpath=($COMPLETION_DIR \$fpath)" >> "$HOME/.zshrc" 2>/dev/null
            echo "autoload -U compinit && compinit" >> "$HOME/.zshrc" 2>/dev/null
            print_status "Zsh completion installed"
            ;;
        fish)
            mkdir -p "$HOME/.config/fish/completions"
            _ERR_X509_COMPLETE=fish_source err_x509 > "$HOME/.config/fish/completions/err_x509.fish"
            print_status "Fish completion installed"
            ;;
        *)
            print_warning "Shell completion not configured for $SHELL_NAME"
            ;;
    esac
}

# Show usage examples
show_examples() {
    echo -e "\n${BLUE}${ROCKET} Usage Examples:${NC}"
    echo "  err_x509 fix config.yaml"
    echo "  err_x509 fix -v -b my_config.yaml"
    echo "  err_x509 batch ./configs/"
    echo "  err_x509 preview config.yaml"
    echo "  err_x509 --help"
}

# Show next steps
show_next_steps() {
    echo -e "\n${GREEN}${CHECK} Installation Complete!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Try: err_x509 --version"
    echo "2. Try: err_x509 --help"
    echo "3. Fix your first config: err_x509 fix config.yaml"
    echo -e "\n${YELLOW}Documentation: https://github.com/13winged/err_x509${NC}"
}

# Main installation process
main() {
    OS=$(detect_os)
    print_info "Detected OS: $OS"
    
    # Check dependencies
    if ! check_python; then
        print_error "Python 3 is required. Please install it first."
        echo "Download from: https://www.python.org/downloads/"
        exit 1
    fi
    
    if ! check_pip; then
        exit 1
    fi
    
    # Install err_x509
    if ! install_err_x509; then
        exit 1
    fi
    
    # Create launchers if installing from source
    if [ -f "pyproject.toml" ]; then
        create_launchers
    fi
    
    # Setup completion
    if [ "$1" = "--with-completion" ]; then
        setup_completion
    fi
    
    # Show information
    show_examples
    show_next_steps
    
    print_status "Installation successful! ${ROCKET}"
}

# Run main function
main "$@"