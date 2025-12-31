#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration and constants for err_x509
"""

import os
from pathlib import Path

# Project metadata
PROJECT_NAME = "err_x509"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = "Fix Clash x509 SSL certificate errors by adding skip-cert-verify"
PROJECT_AUTHOR = "13winged"
PROJECT_URL = "https://github.com/13winged/err_x509"
PROJECT_LICENSE = "MIT"

# File patterns and extensions
YAML_EXTENSIONS = [".yaml", ".yml"]
CONFIG_PATTERNS = ["*.yaml", "*.yml"]
DEFAULT_INPUT_FILES = ["x509_no_fix.yaml", "config.yaml", "clash.yaml"]

# Clash configuration constants
CLASH_REQUIRED_FIELDS = ["port", "socks-port", "redir-port"]
CLASH_OPTIONAL_FIELDS = ["allow-lan", "mode", "log-level", "external-controller"]
CLASH_PROXY_TYPES = ["trojan", "ss", "ssr", "vmess", "vless", "http", "socks5", "snell"]

# SSL/TLS related constants
SSL_FIX_FIELD = "skip-cert-verify"
SSL_FIX_VALUE = True
SSL_WARNING = """# ===========================================================================
# Security Warning:
# skip-cert-verify: true disables SSL certificate validation.
# Use only with trusted servers in non-sensitive contexts.
# ==========================================================================="""

# Regex patterns for parsing
REGEX_PATTERNS = {
    "proxy_start": r"^\s*-\s*\{",
    "proxy_inline": r"-\s*\{[^}]+\}",
    "proxy_multiline_start": r"^\s*-\s*$",
    "proxy_field": r"^\s+[a-zA-Z][a-zA-Z0-9_-]*:",
    "skip_cert_verify": r"skip-cert-verify:\s*(true|false)",
    "yaml_key_value": r"^([a-zA-Z0-9_-]+):\s*(.+)$",
}

# Default settings
DEFAULT_SETTINGS = {
    "verbose": False,
    "backup": False,
    "force": False,
    "dry_run": False,
    "output_suffix": "_fixed",
    "backup_suffix": ".backup",
    "encoding": "utf-8",
    "max_file_size_mb": 10,  # Maximum file size to process
}

# Color codes for CLI output (compatible with click)
COLORS = {
    "success": "green",
    "error": "red",
    "warning": "yellow",
    "info": "blue",
    "debug": "cyan",
    "file": "magenta",
    "proxy": "white",
    "ssl": "bright_yellow",
}

# Icons for CLI output (Unicode)
ICONS = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "📝",
    "debug": "🔍",
    "file": "📁",
    "proxy": "🔗",
    "ssl": "🔒",
    "gear": "⚙️",
    "rocket": "🚀",
    "magnifier": "🔎",
    "folder": "📂",
}

# Banner templates
BANNERS = {
    "main": """
╔═══════════════════════════════════════════════╗
║            err_x509 - x509 SSL Fixer          ║
║          Fix Clash SSL certificate errors     ║
║           GitHub: 13winged/err_x509           ║
╚═══════════════════════════════════════════════╝
""",
    "success": """
╔═══════════════════════════════════════════════╗
║              SUCCESS!                         ║
║      Configuration fixed successfully         ║
╚═══════════════════════════════════════════════╝
""",
    "batch": """
╔═══════════════════════════════════════════════╗
║            BATCH PROCESSING                   ║
║      Processing multiple configuration files  ║
╚═══════════════════════════════════════════════╝
""",
}

# Error messages
ERROR_MESSAGES = {
    "file_not_found": "File not found: {file}",
    "permission_denied": "Permission denied: {file}",
    "invalid_yaml": "Invalid YAML format in: {file}",
    "no_proxies": "No 'proxies' section found in configuration",
    "file_too_large": "File too large (> {size}MB): {file}",
    "output_exists": "Output file already exists: {file}",
    "directory_not_found": "Directory not found: {dir}",
    "no_yaml_files": "No YAML files found in: {dir}",
}

# Success messages
SUCCESS_MESSAGES = {
    "file_processed": "Successfully processed: {file}",
    "proxies_fixed": "Fixed {count} proxies in: {file}",
    "backup_created": "Backup created: {file}",
    "batch_complete": "Batch processing complete: {success}/{total} files",
}

# Usage examples for help text
USAGE_EXAMPLES = [
    "err_x509 fix config.yaml",
    "err_x509 fix input.yaml output_fixed.yaml",
    "err_x509 fix -v -b my_config.yaml",
    "err_x509 batch ./configs/",
    "err_x509 preview config.yaml",
    "err_x509 check",
]


# Platform-specific configurations
def get_platform_config():
    """Get platform-specific configuration"""
    import platform

    system = platform.system().lower()

    config = {
        "windows": {
            "shell": "cmd",
            "newline": "\r\n",
            "config_dirs": [
                Path(os.environ.get("APPDATA", "")) / "Clash",
                Path(os.environ.get("USERPROFILE", "")) / "Desktop",
                Path(os.environ.get("USERPROFILE", "")) / "Documents",
            ],
            "python_cmd": "python",
        },
        "linux": {
            "shell": "bash",
            "newline": "\n",
            "config_dirs": [
                Path.home() / ".config" / "clash",
                Path("/etc/clash"),
                Path.home() / "Downloads",
            ],
            "python_cmd": "python3",
        },
        "darwin": {
            "shell": "bash",
            "newline": "\n",
            "config_dirs": [
                Path.home() / ".config" / "clash",
                Path.home() / "Library/Application Support/Clash",
                Path.home() / "Downloads",
            ],
            "python_cmd": "python3",
        },
    }

    return config.get(system, config["linux"])


# Default output templates
OUTPUT_TEMPLATES = {
    "header": """# ===========================================================================
# Clash Configuration with SSL Verification Disabled
# Generated by {tool_name} v{version}
# GitHub: {github_url}
# Source: {source_file}
# Generated: {timestamp}
# ===========================================================================
""",
    "footer": """# ===========================================================================
# Statistics
# Total proxies processed: {proxy_count}
# SSL verification disabled for all servers
# Output file: {output_file
{security_warning}
# ===========================================================================
""",
    "security_warning": """# Security Warning:
# skip-cert-verify: true disables SSL certificate validation.
# Use only with trusted servers in non-sensitive contexts.
# """,
}

# Validation rules for Clash configurations
VALIDATION_RULES = {
    "port": {
        "type": int,
        "min": 1,
        "max": 65535,
        "required": True,
    },
    "socks-port": {
        "type": int,
        "min": 1,
        "max": 65535,
        "required": True,
    },
    "proxies": {
        "type": list,
        "required": True,
        "min_length": 1,
    },
    "skip-cert-verify": {
        "type": bool,
        "default": True,
        "required": False,
    },
}

# Cache settings (for future optimization)
CACHE_SETTINGS = {
    "enabled": False,
    "max_size": 100,  # Max cached files
    "ttl": 3600,  # Time to live in seconds
}

# Performance settings
PERFORMANCE_SETTINGS = {
    "chunk_size": 8192,  # Bytes to read at once
    "max_proxies_per_file": 10000,  # Safety limit
    "timeout_seconds": 30,  # Processing timeout
}

# Export all configuration
__all__ = [
    "PROJECT_NAME",
    "PROJECT_VERSION",
    "PROJECT_DESCRIPTION",
    "PROJECT_AUTHOR",
    "PROJECT_URL",
    "YAML_EXTENSIONS",
    "CONFIG_PATTERNS",
    "DEFAULT_INPUT_FILES",
    "CLASH_REQUIRED_FIELDS",
    "CLASH_OPTIONAL_FIELDS",
    "CLASH_PROXY_TYPES",
    "SSL_FIX_FIELD",
    "SSL_FIX_VALUE",
    "SSL_WARNING",
    "REGEX_PATTERNS",
    "DEFAULT_SETTINGS",
    "COLORS",
    "ICONS",
    "BANNERS",
    "ERROR_MESSAGES",
    "SUCCESS_MESSAGES",
    "USAGE_EXAMPLES",
    "get_platform_config",
    "OUTPUT_TEMPLATES",
    "VALIDATION_RULES",
    "CACHE_SETTINGS",
    "PERFORMANCE_SETTINGS",
]
