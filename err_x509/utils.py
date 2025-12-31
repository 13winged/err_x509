#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for err_x509
"""

import os
import sys
import platform
import re
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import click

from . import config


def get_platform_info() -> Dict[str, str]:
    """Get detailed platform information"""
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
    }
    return info


def detect_clash_directories() -> List[Path]:
    """Detect common Clash configuration directories"""
    os_type = platform.system().lower()
    directories = []
    
    if os_type == 'windows':
        possible_dirs = [
            Path(os.environ.get('APPDATA', '')) / 'Clash',
            Path(os.environ.get('LOCALAPPDATA', '')) / 'Clash',
            Path(os.environ.get('USERPROFILE', '')) / 'Desktop',
            Path(os.environ.get('USERPROFILE', '')) / 'Documents',
            Path(os.environ.get('USERPROFILE', '')) / 'Downloads',
        ]
    elif os_type == 'darwin':  # macOS
        possible_dirs = [
            Path.home() / '.config' / 'clash',
            Path.home() / 'Library/Application Support/Clash',
            Path.home() / 'Downloads',
            Path.home() / 'Desktop',
        ]
    else:  # Linux and others
        possible_dirs = [
            Path.home() / '.config' / 'clash',
            Path('/etc/clash'),
            Path.home() / 'Downloads',
            Path.home() / 'Desktop',
        ]
    
    # Filter to existing directories
    directories = [d for d in possible_dirs if d.exists() and d.is_dir()]
    
    return directories


def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
    """Calculate file hash for caching/verification"""
    hash_func = getattr(hashlib, algorithm)()
    
    with open(file_path, 'rb') as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def validate_proxy_url(url: str) -> bool:
    """Validate proxy server URL"""
    patterns = [
        r'^[a-zA-Z0-9.-]+$',  # hostname
        r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',  # IPv4
        r'^\[[a-fA-F0-9:]+\]$',  # IPv6 in brackets
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False


def extract_proxy_info(proxy: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and format proxy information"""
    info = {
        'name': proxy.get('name', 'Unknown'),
        'type': proxy.get('type', 'unknown'),
        'server': proxy.get('server', ''),
        'port': proxy.get('port', ''),
        'has_ssl_verify': 'skip-cert-verify' in proxy,
        'ssl_verify_value': proxy.get('skip-cert-verify', None),
    }
    
    # Add additional fields if present
    for key in ['password', 'cipher', 'uuid', 'network', 'tls']:
        if key in proxy:
            info[key] = proxy[key]
    
    return info


def create_backup_file(original_path: Path, suffix: str = None) -> Path:
    """Create a timestamped backup of a file"""
    if suffix is None:
        suffix = config.DEFAULT_SETTINGS['backup_suffix']
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = original_path.with_suffix(f'.{timestamp}{suffix}{original_path.suffix}')
    
    import shutil
    shutil.copy2(original_path, backup_path)
    
    return backup_path


def find_yaml_files(directory: Path, recursive: bool = False) -> List[Path]:
    """Find YAML files in directory"""
    patterns = config.CONFIG_PATTERNS
    files = []
    
    for pattern in patterns:
        if recursive:
            files.extend(directory.rglob(pattern))
        else:
            files.extend(directory.glob(pattern))
    
    # Remove duplicates and sort
    files = sorted(set(files))
    
    return files


def safe_yaml_load(content: str, loader=None):
    """Safely load YAML with error handling"""
    import yaml
    
    try:
        if loader:
            return yaml.load(content, Loader=loader)
        else:
            return yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parsing error: {e}")
    except Exception as e:
        raise ValueError(f"Error loading YAML: {e}")


def safe_yaml_dump(data: Any, **kwargs) -> str:
    """Safely dump YAML with error handling"""
    import yaml
    
    try:
        return yaml.dump(data, **kwargs)
    except Exception as e:
        raise ValueError(f"Error dumping YAML: {e}")


def progress_bar(iterable, length: int = 50, label: str = "Processing"):
    """Simple progress bar generator"""
    total = len(iterable)
    
    for i, item in enumerate(iterable):
        percent = (i + 1) / total
        filled = int(length * percent)
        bar = '█' * filled + '░' * (length - filled)
        
        click.echo(f"\r{label}: [{bar}] {percent:.1%}", nl=False)
        yield item
    
    click.echo()  # New line after completion


def print_table(headers: List[str], rows: List[List[str]], max_width: int = 80):
    """Print formatted table"""
    if not rows:
        return
    
    # Calculate column widths
    col_widths = []
    for i in range(len(headers)):
        max_len = max(
            len(str(headers[i])),
            max(len(str(row[i])) for row in rows if i < len(row))
        )
        col_widths.append(min(max_len, max_width // len(headers)))
    
    # Print header
    header_row = " | ".join(
        str(h).ljust(w)[:w] for h, w in zip(headers, col_widths)
    )
    click.echo(header_row)
    click.echo("-" * len(header_row))
    
    # Print rows
    for row in rows:
        row_str = " | ".join(
            str(cell).ljust(w)[:w] for cell, w in zip(row, col_widths)
        )
        click.echo(row_str)


def get_terminal_size() -> Tuple[int, int]:
    """Get terminal width and height"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except (AttributeError, OSError):
        return 80, 24  # Default fallback


def wrap_text(text: str, width: int = None) -> str:
    """Wrap text to specified width"""
    if width is None:
        width, _ = get_terminal_size()
    
    import textwrap
    return textwrap.fill(text, width=width)


def confirm_overwrite(file_path: Path) -> bool:
    """Ask user to confirm file overwrite"""
    if not file_path.exists():
        return True
    
    click.echo(click.style(f"⚠️  File exists: {file_path}", fg='yellow'))
    return click.confirm("Overwrite?", default=False)


def setup_logging(verbose: bool = False, log_file: str = None):
    """Setup logging configuration"""
    import logging
    
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[]
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    logging.getLogger().addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    
    return logging.getLogger(__name__)


def is_valid_ip_address(ip: str) -> bool:
    """Check if string is a valid IP address"""
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    if re.match(ipv4_pattern, ip):
        # Validate IPv4 octets
        octets = ip.split('.')
        if len(octets) != 4:
            return False
        for octet in octets:
            if not (0 <= int(octet) <= 255):
                return False
        return True
    
    if re.match(ipv6_pattern, ip):
        return True
    
    return False


def get_relative_time(dt: datetime) -> str:
    """Get human-readable relative time"""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"


def cleanup_old_files(directory: Path, pattern: str, keep_count: int = 5):
    """Clean up old files, keeping only the newest ones"""
    files = sorted(directory.glob(pattern), key=os.path.getmtime, reverse=True)
    
    for file in files[keep_count:]:
        try:
            file.unlink()
        except OSError as e:
            logging.warning(f"Failed to delete {file}: {e}")


__all__ = [
    'get_platform_info',
    'detect_clash_directories',
    'calculate_file_hash',
    'format_file_size',
    'format_duration',
    'validate_proxy_url',
    'extract_proxy_info',
    'create_backup_file',
    'find_yaml_files',
    'safe_yaml_load',
    'safe_yaml_dump',
    'progress_bar',
    'print_table',
    'get_terminal_size',
    'wrap_text',
    'confirm_overwrite',
    'setup_logging',
    'is_valid_ip_address',
    'get_relative_time',
    'cleanup_old_files',
]