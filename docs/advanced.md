# Advanced Usage

This guide covers advanced features and customization options for err_x509.

## Table of Contents

- [Custom Configuration](#custom-configuration)
- [Integration Examples](#integration-examples)
- [Performance Tuning](#performance-tuning)
- [Security Considerations](#security-considerations)
- [Custom Output Formats](#custom-output-formats)
- [Plugin System](#plugin-system)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting Advanced Issues](#troubleshooting-advanced-issues)

## Custom Configuration

### Environment Variables

err_x509 can be configured using environment variables:

```bash
# Set default verbosity
export ERR_X509_VERBOSE=1

# Set backup default
export ERR_X509_BACKUP=1

# Custom output suffix
export ERR_X509_OUTPUT_SUFFIX=".ssl_fixed"

# Max file size (MB)
export ERR_X509_MAX_FILE_SIZE=50
```

### Configuration File

Create a configuration file at `~/.config/err_x509/config.yaml`:

```yaml
# err_x509 configuration
defaults:
  verbose: false
  backup: true
  force: false
  output_suffix: "_ssl_fixed"

directories:
  config_dir: ~/.config/clash
  backup_dir: ~/.local/share/err_x509/backups
  cache_dir: ~/.cache/err_x509

performance:
  max_file_size_mb: 100
  chunk_size: 8192
  cache_enabled: true
  cache_ttl: 3600

security:
  warn_on_ssl_disable: true
  allow_localhost_only: false
  validate_proxy_urls: true

logging:
  level: INFO
  file: ~/.local/share/err_x509/err_x509.log
  max_size_mb: 10
  backup_count: 5
```

Load configuration in your code:

```python
from err_x509 import X509Fixer
import yaml
import os

def load_config():
    """Load configuration from file"""
    config_path = os.path.expanduser("~/.config/err_x509/config.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()
fixer = X509Fixer(
    verbose=config.get('defaults', {}).get('verbose', False),
    backup=config.get('defaults', {}).get('backup', False)
)
```

## Integration Examples

### Integration with Clash Auto-Config

```python
#!/usr/bin/env python3
"""Automatically fix and reload Clash configuration"""

import time
import yaml
from pathlib import Path
from err_x509 import X509Fixer
import requests  # For Clash API

class ClashAutoFixer:
    def __init__(self, config_dir, clash_api_url="http://127.0.0.1:9090"):
        self.config_dir = Path(config_dir)
        self.clash_api_url = clash_api_url
        self.fixer = X509Fixer(verbose=True, backup=True)
        
    def watch_and_fix(self, interval=60):
        """Watch for new configurations and fix them"""
        print(f"👀 Watching {self.config_dir} for new configurations...")
        
        known_files = set(self.config_dir.glob("*.yaml"))
        
        while True:
            current_files = set(self.config_dir.glob("*.yaml"))
            new_files = current_files - known_files
            
            for file in new_files:
                print(f"🆕 New file detected: {file.name}")
                self.process_file(file)
            
            known_files = current_files
            time.sleep(interval)
    
    def process_file(self, config_file):
        """Process and reload configuration"""
        # Fix configuration
        success, fixed_file, count = self.fixer.fix_file(str(config_file))
        
        if not success:
            print(f"❌ Failed to fix {config_file.name}")
            return
        
        print(f"✅ Fixed {config_file.name} ({count} proxies)")
        
        # Reload in Clash
        self.reload_clash_config(fixed_file)
    
    def reload_clash_config(self, config_file):
        """Reload configuration in Clash"""
        try:
            # Read fixed configuration
            with open(config_file, 'r') as f:
                config_content = f.read()
            
            # Update via Clash API
            response = requests.put(
                f"{self.clash_api_url}/configs",
                json={"path": str(config_file)}
            )
            
            if response.status_code == 204:
                print(f"🔄 Clash configuration reloaded")
            else:
                print(f"⚠️  Failed to reload Clash: {response.text}")
                
        except Exception as e:
            print(f"❌ Error reloading Clash: {e}")

# Usage
fixer = ClashAutoFixer("~/clash_configs")
fixer.watch_and_fix(interval=30)  # Check every 30 seconds
```

### Integration with CI/CD Pipeline

```yaml
# .github/workflows/fix-configs.yml
name: Fix Clash Configurations

on:
  push:
    paths:
      - 'configs/**'
  pull_request:
    paths:
      - 'configs/**'

jobs:
  fix-configs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install err_x509
      run: pip install err-x509
    
    - name: Fix configurations
      run: |
        mkdir -p fixed_configs
        for file in configs/*.yaml; do
          err_x509 fix "$file" "fixed_configs/$(basename "$file")"
        done
    
    - name: Upload fixed configurations
      uses: actions/upload-artifact@v3
      with:
        name: fixed-configs
        path: fixed_configs/
    
    - name: Create PR with fixed configs
      uses: peter-evans/create-pull-request@v5
      with:
        title: "Fix SSL certificate verification"
        body: |
          Automatically fixed SSL certificate verification by adding `skip-cert-verify: true`
          
          **Changes made:**
          - Added `skip-cert-verify: true` to all proxy servers
          - Preserved all original configuration
          - Created backups of original files
        branch: fix-ssl-verification
        commit-message: "fix: add skip-cert-verify to proxy configurations"
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Install err_x509
RUN pip install err-x509

# Create working directory
WORKDIR /app

# Copy configuration files
COPY configs/ /app/configs/

# Create entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD err_x509 --version || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
```

```bash
#!/bin/bash
# entrypoint.sh

# Fix all configurations on startup
err_x509 batch /app/configs/ --verbose

# Keep container running
tail -f /dev/null
```

## Performance Tuning

### Caching Mechanism

```python
from err_x509 import X509Fixer
import hashlib
import pickle
from pathlib import Path
import time

class CachedX509Fixer(X509Fixer):
    """X509Fixer with caching support"""
    
    def __init__(self, cache_dir="~/.cache/err_x509", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fix_file(self, input_file, output_file=None):
        """Fix file with caching"""
        # Calculate file hash for cache key
        file_hash = self._calculate_file_hash(input_file)
        cache_file = self.cache_dir / f"{file_hash}.cache"
        
        # Check cache
        if cache_file.exists():
            cache_data = self._load_cache(cache_file)
            
            # Check if cache is still valid
            if self._is_cache_valid(cache_data, input_file):
                self.log(f"Using cached result for {Path(input_file).name}", "debug")
                return cache_data['result']
        
        # Process file
        result = super().fix_file(input_file, output_file)
        
        # Save to cache
        cache_data = {
            'timestamp': time.time(),
            'input_file': input_file,
            'result': result
        }
        self._save_cache(cache_file, cache_data)
        
        return result
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _load_cache(self, cache_file):
        """Load data from cache file"""
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    
    def _save_cache(self, cache_file, data):
        """Save data to cache file"""
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    
    def _is_cache_valid(self, cache_data, input_file):
        """Check if cache is still valid"""
        # Check if input file hasn't changed
        current_hash = self._calculate_file_hash(input_file)
        cached_hash = self._calculate_file_hash(cache_data['input_file'])
        
        return current_hash == cached_hash

# Usage
fixer = CachedX509Fixer(verbose=True)
success, output_file, count = fixer.fix_file("config.yaml")
```

### Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from err_x509 import X509Fixer
from pathlib import Path

def batch_process_parallel(directory, max_workers=4):
    """Process files in parallel"""
    fixer = X509Fixer()
    files = list(Path(directory).glob("*.yaml"))
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks
        future_to_file = {
            executor.submit(process_single_file, fixer, file): file
            for file in files
        }
        
        # Process results as they complete
        for future in as_completed(future_to_file):
            file = future_to_file[future]
            try:
                success, output_file, count = future.result()
                results[str(file)] = (success, output_file, count)
            except Exception as e:
                print(f"❌ Error processing {file}: {e}")
                results[str(file)] = (False, None, 0)
    
    return results

def process_single_file(fixer, file):
    """Process single file (worker function)"""
    output_file = file.with_suffix('.fixed.yaml')
    return fixer.fix_file(str(file), str(output_file))

# Usage
results = batch_process_parallel("./configs", max_workers=4)
```

## Security Considerations

### Proxy Validation

```python
from err_x509 import X509Fixer
import re

class ValidatingX509Fixer(X509Fixer):
    """X509Fixer with enhanced security validation"""
    
    def process_proxy(self, proxy):
        """Process proxy with validation"""
        # Validate proxy before processing
        self.validate_proxy(proxy)
        
        # Call parent method
        return super().process_proxy(proxy)
    
    def validate_proxy(self, proxy):
        """Validate proxy security"""
        # Check for required fields
        required_fields = ['name', 'type', 'server']
        for field in required_fields:
            if field not in proxy:
                raise ValueError(f"Proxy missing required field: {field}")
        
        # Validate server
        server = proxy['server']
        if not self.is_valid_server(server):
            raise ValueError(f"Invalid server address: {server}")
        
        # Warn about local servers with SSL disabled
        if self.is_local_server(server) and proxy.get('skip-cert-verify', False):
            self.log(f"⚠️  Warning: Local server {server} with SSL disabled", "warning")
    
    def is_valid_server(self, server):
        """Validate server address"""
        patterns = [
            r'^[a-zA-Z0-9.-]+$',  # Domain
            r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',  # IPv4
            r'^\[[a-fA-F0-9:]+\]$',  # IPv6
            r'^localhost$',
        ]
        
        return any(re.match(p, server) for p in patterns)
    
    def is_local_server(self, server):
        """Check if server is local"""
        local_patterns = [
            'localhost',
            '127.0.0.1',
            '192.168.',
            '10.',
            '172.16.',
            '172.17.',
            '172.18.',
            '172.19.',
            '172.20.',
            '172.21.',
            '172.22.',
            '172.23.',
            '172.24.',
            '172.25.',
            '172.26.',
            '172.27.',
            '172.28.',
            '172.29.',
            '172.30.',
            '172.31.',
        ]
        
        return any(server.startswith(pattern) for pattern in local_patterns)

# Usage
secure_fixer = ValidatingX509Fixer(verbose=True)
success, output_file, count = secure_fixer.fix_file("config.yaml")
```

## Custom Output Formats

### JSON Output

```python
from err_x509 import X509Fixer
import json
import yaml
from datetime import datetime

class JsonOutputFixer(X509Fixer):
    """X509Fixer with JSON output support"""
    
    def fix_file(self, input_file, output_file=None, format='yaml'):
        """Fix file with custom output format"""
        # Call parent method to get YAML result
        success, yaml_output_file, count = super().fix_file(input_file, output_file)
        
        if not success:
            return success, yaml_output_file, count
        
        if format == 'json':
            # Convert YAML to JSON
            json_output_file = yaml_output_file.replace('.yaml', '.json')
            self.convert_yaml_to_json(yaml_output_file, json_output_file)
            return success, json_output_file, count
        
        return success, yaml_output_file, count
    
    def convert_yaml_to_json(self, yaml_file, json_file):
        """Convert YAML file to JSON"""
        with open(yaml_file, 'r') as f:
            yaml_content = f.read()
        
        # Parse YAML
        data = yaml.safe_load(yaml_content)
        
        # Add metadata
        metadata = {
            'generated_by': 'err_x509',
            'generated_at': datetime.now().isoformat(),
            'format': 'json'
        }
        
        data['_metadata'] = metadata
        
        # Write JSON
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.log(f"Converted to JSON: {json_file}", "info")

# Usage
fixer = JsonOutputFixer()
success, output_file, count = fixer.fix_file("config.yaml", format='json')
```

### Template-Based Output

```python
from string import Template
from err_x509 import X509Fixer
import yaml

class TemplateOutputFixer(X509Fixer):
    """X509Fixer with template-based output"""
    
    def __init__(self, template_file=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_file = template_file
    
    def add_metadata(self, content, input_file, output_file):
        """Add metadata using template"""
        if self.template_file:
            return self._apply_template(content, input_file, output_file)
        return super().add_metadata(content, input_file, output_file)
    
    def _apply_template(self, content, input_file, output_file):
        """Apply custom template"""
        with open(self.template_file, 'r') as f:
            template_content = f.read()
        
        # Parse configuration for template variables
        config = yaml.safe_load(content)
        proxy_count = len(config.get('proxies', []))
        
        # Prepare template variables
        variables = {
            'content': content.strip(),
            'input_file': Path(input_file).name,
            'output_file': Path(output_file).name,
            'proxy_count': proxy_count,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'generator': 'err_x509',
            'year': datetime.now().year,
        }
        
        # Apply template
        template = Template(template_content)
        return template.safe_substitute(variables)

# Custom template (template.txt)
template_content = """
# ===========================================
# Fixed Configuration
# File: $input_file -> $output_file
# Generated: $timestamp
# Proxies: $proxy_count
# ===========================================

$content

# ===========================================
# End of file
# ===========================================
"""

# Usage
with open("template.txt", "w") as f:
    f.write(template_content)

fixer = TemplateOutputFixer(template_file="template.txt", verbose=True)
success, output_file, count = fixer.fix_file("config.yaml")
```

## Plugin System

### Creating Plugins

```python
# plugins/security_audit.py
from err_x509 import X509Fixer

class SecurityAuditPlugin:
    """Plugin for security auditing"""
    
    def __init__(self, fixer):
        self.fixer = fixer
        self.audit_results = []
    
    def before_fix(self, input_file):
        """Called before fixing"""
        self.audit_results.append({
            'file': input_file,
            'timestamp': datetime.now().isoformat(),
            'action': 'start'
        })
    
    def after_fix(self, input_file, output_file, proxy_count):
        """Called after fixing"""
        self.audit_results.append({
            'file': input_file,
            'output': output_file,
            'proxy_count': proxy_count,
            'timestamp': datetime.now().isoformat(),
            'action': 'complete'
        })
    
    def get_report(self):
        """Generate audit report"""
        return {
            'audit_date': datetime.now().isoformat(),
            'total_files': len([r for r in self.audit_results if r['action'] == 'complete']),
            'total_proxies': sum(r.get('proxy_count', 0) for r in self.audit_results),
            'details': self.audit_results
        }

# Usage
fixer = X509Fixer()
plugin = SecurityAuditPlugin(fixer)

# Monkey patch to add plugin hooks
original_fix_file = fixer.fix_file

def hooked_fix_file(input_file, output_file=None):
    plugin.before_fix(input_file)
    success, out_file, count = original_fix_file(input_file, output_file)
    if success:
        plugin.after_fix(input_file, out_file, count)
    return success, out_file, count

fixer.fix_file = hooked_fix_file

# Process files
fixer.fix_file("config.yaml")

# Get report
report = plugin.get_report()
print(json.dumps(report, indent=2))
```

## Monitoring and Logging

### Structured Logging

```python
import logging
import json
from err_x509 import X509Fixer

class StructuredLogger:
    """Structured JSON logger"""
    
    def __init__(self, log_file="err_x509.log"):
        self.log_file = log_file
        self.setup_logging()
    
    def setup_logging(self):
        """Setup structured logging"""
        logger = logging.getLogger('err_x509')
        logger.setLevel(logging.INFO)
        
        # File handler with JSON formatter
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(console_handler)
    
    def log_operation(self, operation, **kwargs):
        """Log structured operation"""
        logger = logging.getLogger('err_x509')
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            **kwargs
        }
        logger.info(json.dumps(log_data))

class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    def format(self, record):
        try:
            log_data = json.loads(record.getMessage())
            log_data.update({
                'level': record.levelname,
                'logger': record.name,
            })
            return json.dumps(log_data)
        except json.JSONDecodeError:
            return super().format(record)

# Usage
logger = StructuredLogger()
fixer = X509Fixer()

# Log operations
logger.log_operation('file_processing_start', file='config.yaml')
success, output_file, count = fixer.fix_file("config.yaml")
logger.log_operation('file_processing_complete', 
                     file='config.yaml', 
                     success=success, 
                     proxies=count)
```

### Metrics Collection

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List
import statistics

@dataclass
class OperationMetrics:
    """Metrics for a single operation"""
    start_time: datetime
    end_time: datetime
    file_size: int
    proxy_count: int
    success: bool
    
    @property
    def duration(self):
        return (self.end_time - self.start_time).total_seconds()

class MetricsCollector:
    """Collect and analyze metrics"""
    
    def __init__(self):
        self.metrics: List[OperationMetrics] = []
    
    def record_operation(self, metrics: OperationMetrics):
        """Record operation metrics"""
        self.metrics.append(metrics)
    
    def generate_report(self):
        """Generate metrics report"""
        if not self.metrics:
            return {}
        
        successful = [m for m in self.metrics if m.success]
        failed = [m for m in self.metrics if not m.success]
        
        return {
            'total_operations': len(self.metrics),
            'successful_operations': len(successful),
            'failed_operations': len(failed),
            'success_rate': len(successful) / len(self.metrics) if self.metrics else 0,
            'total_proxies': sum(m.proxy_count for m in successful),
            'avg_proxies_per_file': statistics.mean([m.proxy_count for m in successful]) if successful else 0,
            'avg_duration': statistics.mean([m.duration for m in successful]) if successful else 0,
            'total_duration': sum(m.duration for m in successful),
            'avg_file_size': statistics.mean([m.file_size for m in self.metrics]) if self.metrics else 0,
        }

# Usage in your application
collector = MetricsCollector()

def fix_with_metrics(fixer, input_file):
    """Fix file with metrics collection"""
    start_time = datetime.now()
    
    # Get file size
    file_size = Path(input_file).stat().st_size
    
    # Fix file
    success, output_file, count = fixer.fix_file(input_file)
    
    end_time = datetime.now()
    
    # Record metrics
    metrics = OperationMetrics(
        start_time=start_time,
        end_time=end_time,
        file_size=file_size,
        proxy_count=count,
        success=success
    )
    collector.record_operation(metrics)
    
    return success, output_file, count

# Generate report
report = collector.generate_report()
print(json.dumps(report, indent=2))
```

## Troubleshooting Advanced Issues

### Memory Leaks

```python
import tracemalloc
from err_x509 import X509Fixer

def debug_memory_usage():
    """Debug memory usage"""
    tracemalloc.start()
    
    fixer = X509Fixer()
    
    # Take snapshot before
    snapshot1 = tracemalloc.take_snapshot()
    
    # Process files
    for i in range(10):
        fixer.fix_file(f"config_{i}.yaml")
    
    # Take snapshot after
    snapshot2 = tracemalloc.take_snapshot()
    
    # Compare snapshots
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("Memory allocation differences:")
    for stat in top_stats[:10]:
        print(stat)
    
    tracemalloc.stop()

# Run memory debugging
debug_memory_usage()
```

### Performance Profiling

```python
import cProfile
import pstats
from err_x509 import X509Fixer

def profile_fix_operation():
    """Profile fix operation"""
    profiler = cProfile.Profile()
    profiler.enable()
    
    fixer = X509Fixer()
    fixer.fix_file("large_config.yaml")
    
    profiler.disable()
    
    # Save stats
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    # Save to file
    stats.dump_stats('profile_results.prof')

# Usage
profile_fix_operation()
```

---

This advanced guide covers customization, integration, and optimization techniques for err_x509. For more specific use cases or additional help, check the [GitHub repository](https://github.com/13winged/err_x509) or create an issue.