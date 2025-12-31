#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core functionality for err_x509 - Fix Clash x509 SSL errors
"""

import re
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import click

# Импортируем конфигурации
from . import config


class X509Fixer:
    """Main class for fixing x509 SSL errors in Clash configurations"""
    
    def __init__(self, verbose: bool = False, backup: bool = False):
        self.verbose = verbose
        self.backup = backup
        self.proxy_count = 0
        self.processed_count = 0
        
    def log(self, message: str, level: str = "info", color: str = None):
        """Log messages with colors and icons"""
        if not self.verbose and level == "debug":
            return
            
        icon = config.ICONS.get(level, "📝")
        color = color or config.COLORS.get(level, "white")
        
        if self.verbose or level in ["success", "error", "warning"]:
            click.echo(click.style(f"{icon} {message}", fg=color))
    
    def normalize_config(self, content: str) -> str:
        """Normalize configuration format (single-line to multi-line)"""
        if self.verbose:
            self.log("Normalizing configuration format...", "debug")
        
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # Split proxies if they are in one line
        patterns = [
            (r' - \{', r'\n  - {'),  # Split proxy start
            (r'\}\s*-\s*\{', r'}\n  - {'),  # Split multiple proxies
            (r'^proxies:\s*', 'proxies:\n'),  # Ensure newline after proxies:
            # Add newlines after main sections
            (r'(port:|socks-port:|redir-port:|allow-lan:|mode:|log-level:|external-controller:)', r'\n\1'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        # Remove excessive empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip() + '\n'
    
    def create_backup(self, file_path: str) -> Optional[str]:
        """Create backup of original file"""
        if not self.backup:
            return None
            
        path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_suffix = config.DEFAULT_SETTINGS['backup_suffix']
        backup_path = path.with_suffix(f'.{timestamp}{backup_suffix}{path.suffix}')
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            self.log(f"Created backup: {backup_path.name}", "file", "yellow")
            return str(backup_path)
        except Exception as e:
            self.log(f"Failed to create backup: {e}", "warning")
            return None
    
    def process_proxy(self, proxy: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single proxy dictionary"""
        self.proxy_count += 1
        
        # Add or update skip-cert-verify
        proxy[config.SSL_FIX_FIELD] = config.SSL_FIX_VALUE
        
        if self.verbose:
            name = proxy.get('name', f'proxy_{self.proxy_count}')
            self.log(f"Processing proxy: {name}", "proxy", "cyan")
        
        return proxy
    
    def fix_with_yaml(self, content: str) -> Tuple[str, int]:
        """Fix configuration using PyYAML parser"""
        try:
            config_data = yaml.safe_load(content)
            
            if not isinstance(config_data, dict):
                raise ValueError("Configuration is not a dictionary")
            
            # Process proxies section
            if 'proxies' in config_data and isinstance(config_data['proxies'], list):
                config_data['proxies'] = [self.process_proxy(p) for p in config_data['proxies']]
            
            # Convert back to YAML with nice formatting
            result = yaml.dump(
                config_data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=1000  # Prevent line wrapping
            )
            
            return result, self.proxy_count
            
        except yaml.YAMLError as e:
            self.log(f"YAML parsing error: {e}", "warning")
            raise
    
    def fix_manually(self, content: str) -> Tuple[str, int]:
        """Fallback manual processing for malformed YAML"""
        self.log("Using manual processing for malformed YAML", "warning")
        
        lines = content.split('\n')
        result_lines = []
        in_proxies = False
        proxy_buffer = []
        in_proxy_object = False
        
        for line in lines:
            stripped = line.strip()
            
            # Detect proxies section start
            if stripped == 'proxies:' or stripped.startswith('proxies:'):
                in_proxies = True
                result_lines.append(line)
                continue
            
            # In proxies section
            if in_proxies:
                # Start of a new proxy
                if stripped.startswith('-'):
                    # Process previous proxy if exists
                    if proxy_buffer:
                        processed = self._process_proxy_buffer(proxy_buffer)
                        result_lines.extend(processed)
                        proxy_buffer = []
                    
                    proxy_buffer.append(line)
                    in_proxy_object = True
                
                # Continuation of proxy object
                elif in_proxy_object and (stripped.startswith('  ') or stripped.startswith('\t')):
                    proxy_buffer.append(line)
                
                # End of proxies section
                elif stripped and not stripped.startswith('#') and not stripped.startswith('-'):
                    in_proxies = False
                    in_proxy_object = False
                    # Process last proxy
                    if proxy_buffer:
                        processed = self._process_proxy_buffer(proxy_buffer)
                        result_lines.extend(processed)
                        proxy_buffer = []
                    result_lines.append(line)
                
                else:
                    result_lines.append(line)
            else:
                result_lines.append(line)
        
        # Process any remaining proxy
        if proxy_buffer:
            processed = self._process_proxy_buffer(proxy_buffer)
            result_lines.extend(processed)
        
        return '\n'.join(result_lines), self.proxy_count
    
    def _process_proxy_buffer(self, buffer: List[str]) -> List[str]:
        """Process collected proxy lines"""
        if not buffer:
            return []
        
        # Join buffer and process
        proxy_text = '\n'.join(buffer)
        
        # Check if it's inline format { ... }
        if '{' in proxy_text and '}' in proxy_text:
            # Inline format
            if config.SSL_FIX_FIELD in proxy_text:
                # Replace existing
                proxy_text = re.sub(
                    config.REGEX_PATTERNS['skip_cert_verify'],
                    f'{config.SSL_FIX_FIELD}: {str(config.SSL_FIX_VALUE).lower()}',
                    proxy_text
                )
            else:
                # Add new
                proxy_text = re.sub(r'\}\s*$', f', {config.SSL_FIX_FIELD}: {str(config.SSL_FIX_VALUE).lower()} }}', proxy_text)
        else:
            # Multi-line format
            lines = proxy_text.split('\n')
            processed_lines = []
            has_skip_verify = any(config.SSL_FIX_FIELD in line for line in lines)
            
            for line in lines:
                if config.SSL_FIX_FIELD in line and not has_skip_verify:
                    # Replace existing
                    line = re.sub(
                        config.REGEX_PATTERNS['skip_cert_verify'],
                        f'{config.SSL_FIX_FIELD}: {str(config.SSL_FIX_VALUE).lower()}',
                        line
                    )
                    has_skip_verify = True
                processed_lines.append(line)
            
            if not has_skip_verify:
                # Find last property line
                for i in range(len(processed_lines) - 1, -1, -1):
                    if processed_lines[i].strip() and not processed_lines[i].strip().startswith('#'):
                        # Insert after last property
                        indent = len(processed_lines[i]) - len(processed_lines[i].lstrip())
                        processed_lines.insert(i + 1, ' ' * indent + f'{config.SSL_FIX_FIELD}: {str(config.SSL_FIX_VALUE).lower()}')
                        break
            
            proxy_text = '\n'.join(processed_lines)
        
        self.proxy_count += 1
        return proxy_text.split('\n')
    
    def add_metadata(self, content: str, input_file: str, output_file: str) -> str:
        """Add metadata header and footer"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create header
        header = config.OUTPUT_TEMPLATES['header'].format(
            tool_name=config.PROJECT_NAME,
            version=config.PROJECT_VERSION,
            github_url=config.PROJECT_URL,
            source_file=Path(input_file).name,
            timestamp=timestamp
        )
        
        # Create footer
        footer = config.OUTPUT_TEMPLATES['footer'].format(
            proxy_count=self.proxy_count,
            output_file=Path(output_file).name,
            security_warning=config.OUTPUT_TEMPLATES['security_warning']
        )
        
        return header + content.strip() + footer
    
    def fix_file(self, input_file: str, output_file: Optional[str] = None) -> Tuple[bool, str, int]:
        """Main function to fix configuration file"""
        self.proxy_count = 0
        self.processed_count += 1
        
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                self.log(config.ERROR_MESSAGES['file_not_found'].format(file=input_file), "error")
                return False, "", 0
            
            self.log(f"Processing: {input_path.name}", "file", "blue")
            
            # Check file size
            file_size_mb = input_path.stat().st_size / (1024 * 1024)
            max_size = config.PERFORMANCE_SETTINGS['max_file_size_mb']
            if file_size_mb > max_size:
                self.log(config.ERROR_MESSAGES['file_too_large'].format(size=max_size, file=input_file), "error")
                return False, "", 0
            
            # Read input file
            encoding = config.DEFAULT_SETTINGS['encoding']
            with open(input_file, 'r', encoding=encoding, errors='ignore') as f:
                content = f.read()
            
            # Create backup if requested
            if self.backup:
                self.create_backup(input_file)
            
            # Determine output file
            if not output_file:
                suffix = config.DEFAULT_SETTINGS['output_suffix']
                if input_file.endswith('.yaml'):
                    output_file = input_file.replace('.yaml', f'{suffix}.yaml')
                elif input_file.endswith('.yml'):
                    output_file = input_file.replace('.yml', f'{suffix}.yml')
                else:
                    output_file = input_file + f'{suffix}.yaml'
            
            output_path = Path(output_file)
            
            # Normalize content
            normalized = self.normalize_config(content)
            
            # Try YAML parsing first
            try:
                fixed_content, proxy_count = self.fix_with_yaml(normalized)
            except Exception:
                # Fallback to manual processing
                fixed_content, proxy_count = self.fix_manually(normalized)
            
            # Add metadata
            final_content = self.add_metadata(fixed_content, input_file, output_file)
            
            # Write output file
            with open(output_file, 'w', encoding=encoding) as f:
                f.write(final_content)
            
            self.log(config.SUCCESS_MESSAGES['file_processed'].format(file=output_path.name), "success", "green")
            self.log(config.SUCCESS_MESSAGES['proxies_fixed'].format(count=proxy_count, file=output_path.name), "success", "green")
            
            return True, output_file, proxy_count
            
        except Exception as e:
            self.log(f"Error processing {input_file}: {e}", "error")
            return False, "", 0
    
    def fix_directory(self, directory: str, pattern: str = "*.yaml") -> Dict[str, Tuple[bool, str, int]]:
        """Fix all configuration files in a directory"""
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            self.log(config.ERROR_MESSAGES['directory_not_found'].format(dir=directory), "error")
            return {}
        
        results = {}
        files = list(dir_path.glob(pattern)) + list(dir_path.glob("*.yml"))
        
        if not files:
            self.log(config.ERROR_MESSAGES['no_yaml_files'].format(dir=directory), "warning")
            return results
        
        self.log(f"Found {len(files)} files in {directory}", "info")
        
        for file_path in files:
            suffix = config.DEFAULT_SETTINGS['output_suffix']
            output_file = file_path.with_suffix(f'{suffix}{file_path.suffix}')
            success, out_path, count = self.fix_file(str(file_path), str(output_file))
            results[str(file_path)] = (success, out_path, count)
        
        return results