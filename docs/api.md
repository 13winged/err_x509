# API Documentation

This document describes the err_x509 Python API for programmatic use.

## Table of Contents

- [Overview](#overview)
- [Core Classes](#core-classes)
- [Utility Functions](#utility-functions)
- [Configuration](#configuration)
- [Examples](#examples)
- [Error Handling](#error-handling)

## Overview

err_x509 provides both a command-line interface and a Python API. The API allows you to integrate SSL certificate fixing functionality into your own applications.

## Installation for API Use

```bash
pip install err-x509
```

## Core Classes

### `X509Fixer`

The main class for fixing SSL certificate errors in Clash configurations.

#### Constructor

```python
from err_x509 import X509Fixer

fixer = X509Fixer(verbose=False, backup=False)
```

**Parameters:**
- `verbose` (bool): Enable verbose output
- `backup` (bool): Create backups of original files

#### Methods

##### `fix_file(input_file, output_file=None)`

Fix a single configuration file.

```python
success, output_path, proxy_count = fixer.fix_file(
    "config.yaml",
    "config_fixed.yaml"
)
```

**Parameters:**
- `input_file` (str): Path to input configuration file
- `output_file` (str, optional): Path to output file

**Returns:** Tuple of (success: bool, output_path: str, proxy_count: int)

##### `fix_directory(directory, pattern="*.yaml")`

Fix all configuration files in a directory.

```python
results = fixer.fix_directory("./configs/", "*.yaml")
```

**Parameters:**
- `directory` (str): Directory path
- `pattern` (str): File pattern to match

**Returns:** Dict mapping input files to (success, output_path, proxy_count)

##### `normalize_config(content)`

Normalize configuration format (single-line to multi-line).

```python
normalized = fixer.normalize_config(yaml_content)
```

**Parameters:**
- `content` (str): YAML content

**Returns:** str (normalized YAML)

##### `create_backup(file_path)`

Create a backup of a file.

```python
backup_path = fixer.create_backup("config.yaml")
```

**Returns:** str or None (backup file path)

#### Properties

- `proxy_count` (int): Number of proxies processed in last operation
- `processed_count` (int): Total files processed
- `verbose` (bool): Verbose mode status
- `backup` (bool): Backup mode status

## Utility Functions

The `err_x509.utils` module provides helper functions:

### File Operations

```python
from err_x509.utils import (
    find_yaml_files,
    create_backup_file,
    calculate_file_hash,
    format_file_size,
)

# Find YAML files
files = find_yaml_files(Path("./configs/"), recursive=True)

# Create backup
backup = create_backup_file(Path("config.yaml"))

# Calculate file hash
file_hash = calculate_file_hash("config.yaml", "sha256")

# Format file size
size_str = format_file_size(1024 * 1024)  # "1.00 MB"
```

### Validation

```python
from err_x509.utils import (
    validate_proxy_url,
    is_valid_ip_address,
    safe_yaml_load,
    safe_yaml_dump,
)

# Validate proxy URL
is_valid = validate_proxy_url("example.com")

# Validate IP address
is_ip = is_valid_ip_address("192.168.1.1")

# Safe YAML operations
data = safe_yaml_load(yaml_content)
yaml_str = safe_yaml_dump(data, default_flow_style=False)
```

### Formatting

```python
from err_x509.utils import (
    format_duration,
    print_table,
    progress_bar,
    wrap_text,
)

# Format duration
duration = format_duration(125.5)  # "2m 5s"

# Print table
headers = ["Name", "Server", "Port"]
rows = [
    ["Proxy1", "s1.example.com", "443"],
    ["Proxy2", "s2.example.com", "443"],
]
print_table(headers, rows)

# Progress bar
for item in progress_bar(items, label="Processing"):
    process_item(item)

# Wrap text
wrapped = wrap_text("Long text here", width=80)
```

## Configuration

The `err_x509.config` module contains all configuration constants:

```python
from err_x509 import config

# Project info
print(config.PROJECT_NAME)      # "err_x509"
print(config.PROJECT_VERSION)   # "1.0.0"

# File patterns
print(config.YAML_EXTENSIONS)   # ['.yaml', '.yml']

# SSL settings
print(config.SSL_FIX_FIELD)     # "skip-cert-verify"
print(config.SSL_FIX_VALUE)     # True

# Platform config
platform_cfg = config.get_platform_config()
print(platform_cfg['shell'])    # "bash", "cmd", etc.
```

## Examples

### Example 1: Basic Programmatic Use

```python
#!/usr/bin/env python3
"""Programmatic use of err_x509"""

from err_x509 import X509Fixer
from pathlib import Path

def fix_configurations(config_dir, output_dir):
    """Fix all configurations in a directory"""
    
    # Create fixer instance
    fixer = X509Fixer(verbose=True, backup=True)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Process each YAML file
    for config_file in Path(config_dir).glob("*.yaml"):
        output_file = output_dir / f"{config_file.stem}_fixed.yaml"
        
        success, out_path, count = fixer.fix_file(
            str(config_file),
            str(output_file)
        )
        
        if success:
            print(f"✅ Fixed {config_file.name}: {count} proxies")
        else:
            print(f"❌ Failed to fix {config_file.name}")
    
    print(f"\n📊 Total files processed: {fixer.processed_count}")
    print(f"🔗 Total proxies fixed: {fixer.proxy_count}")

if __name__ == "__main__":
    fix_configurations("./configs", "./fixed_configs")
```

### Example 2: Custom Processing Pipeline

```python
#!/usr/bin/env python3
"""Custom processing with err_x509"""

import yaml
from err_x509 import X509Fixer
from err_x509.utils import extract_proxy_info, validate_proxy_url

def analyze_and_fix(config_file):
    """Analyze configuration before fixing"""
    
    # Load configuration
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Analyze proxies
    proxies = config.get('proxies', [])
    print(f"Found {len(proxies)} proxies")
    
    for proxy in proxies:
        info = extract_proxy_info(proxy)
        
        # Check server validity
        if not validate_proxy_url(info['server']):
            print(f"⚠️  Invalid server: {info['server']}")
        
        # Check if already has SSL verify disabled
        if info['has_ssl_verify'] and info['ssl_verify_value']:
            print(f"ℹ️  Already has SSL disabled: {info['name']}")
    
    # Fix configuration
    fixer = X509Fixer()
    success, out_path, count = fixer.fix_file(config_file)
    
    return success, out_path, count

# Usage
success, output_file, count = analyze_and_fix("config.yaml")
```

### Example 3: Integration with Web Service

```python
#!/usr/bin/env python3
"""Web service using err_x509 API"""

from flask import Flask, request, jsonify
from err_x509 import X509Fixer
import tempfile
import os

app = Flask(__name__)
fixer = X509Fixer()

@app.route('/fix', methods=['POST'])
def fix_configuration():
    """Fix configuration via API"""
    
    # Get YAML content from request
    yaml_content = request.json.get('yaml', '')
    
    if not yaml_content:
        return jsonify({'error': 'No YAML content provided'}), 400
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        input_file = f.name
    
    try:
        # Fix configuration
        success, output_file, count = fixer.fix_file(input_file)
        
        if success:
            # Read fixed content
            with open(output_file, 'r') as f:
                fixed_content = f.read()
            
            return jsonify({
                'success': True,
                'proxies_fixed': count,
                'fixed_yaml': fixed_content
            })
        else:
            return jsonify({'error': 'Failed to fix configuration'}), 500
            
    finally:
        # Cleanup temporary files
        for file in [input_file, output_file]:
            if os.path.exists(file):
                os.unlink(file)

if __name__ == '__main__':
    app.run(debug=True)
```

## Error Handling

err_x509 raises standard Python exceptions. Here's how to handle them:

```python
from err_x509 import X509Fixer
import yaml

fixer = X509Fixer()

try:
    success, output_file, count = fixer.fix_file("config.yaml")
    
    if success:
        print(f"Fixed {count} proxies")
    else:
        print("Failed to fix configuration")
        
except FileNotFoundError as e:
    print(f"File not found: {e}")
except yaml.YAMLError as e:
    print(f"Invalid YAML: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Custom Error Classes

```python
from err_x509.core import X509Fixer

class ConfigurationError(Exception):
    """Base class for configuration errors"""
    pass

class InvalidProxyError(ConfigurationError):
    """Invalid proxy configuration"""
    pass

def validate_configuration(config):
    """Custom validation"""
    if 'proxies' not in config:
        raise ConfigurationError("No proxies section")
    
    for proxy in config.get('proxies', []):
        if 'server' not in proxy:
            raise InvalidProxyError("Proxy missing server")
    
    return True
```

## Testing with err_x509

```python
#!/usr/bin/env python3
"""Testing err_x509 in your application"""

import pytest
from unittest.mock import Mock, patch
from err_x509 import X509Fixer

def test_fix_file():
    """Test file fixing functionality"""
    fixer = X509Fixer(verbose=False)
    
    # Create test configuration
    test_yaml = """
    port: 7890
    proxies:
      - {name: test, server: example.com, port: 443}
    """
    
    # Write to temporary file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(test_yaml)
        test_file = f.name
    
    try:
        success, output_file, count = fixer.fix_file(test_file)
        
        assert success == True
        assert count == 1
        assert output_file.endswith('_fixed.yaml')
        
        # Verify SSL fix was added
        with open(output_file, 'r') as f:
            content = f.read()
            assert 'skip-cert-verify: true' in content
            
    finally:
        import os
        for file in [test_file, output_file]:
            if os.path.exists(file):
                os.unlink(file)

# Run with: pytest test_myapp.py
```

## Performance Considerations

### Large Files

For large configuration files, consider:

```python
# Process in chunks for very large files
def process_large_file(file_path, chunk_size=1000):
    fixer = X509Fixer()
    
    with open(file_path, 'r') as f:
        # Read and process in chunks if needed
        content = f.read()
    
    success, output_file, count = fixer.fix_file(file_path)
    return success, output_file, count
```

### Memory Usage

Monitor memory usage for batch processing:

```python
import psutil
from err_x509 import X509Fixer

def batch_process_with_memory_monitor(directory):
    """Process files with memory monitoring"""
    fixer = X509Fixer()
    process = psutil.Process()
    
    for file in Path(directory).glob("*.yaml"):
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        success, output_file, count = fixer.fix_file(str(file))
        
        memory_after = process.memory_info().rss / 1024 / 1024
        memory_used = memory_after - memory_before
        
        print(f"Processed {file.name}: {count} proxies, used {memory_used:.2f}MB")
```

---

Next: [Advanced Usage](advanced.md) → [Usage Guide](usage.md)