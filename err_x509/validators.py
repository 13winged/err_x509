#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation functions for err_x509
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from . import config


def validate_clash_config(config_data: Dict[str, Any]) -> List[str]:
    """Validate Clash configuration structure"""
    errors = []

    # Check required fields
    for field in config.CLASH_REQUIRED_FIELDS:
        if field not in config_data:
            errors.append(f"Missing required field: {field}")

    # Check proxies section
    if "proxies" not in config_data:
        errors.append("Missing 'proxies' section")
    elif not isinstance(config_data["proxies"], list):
        errors.append("'proxies' must be a list")
    elif len(config_data["proxies"]) == 0:
        errors.append("'proxies' list is empty")
    else:
        # Validate each proxy
        for i, proxy in enumerate(config_data["proxies"]):
            if not isinstance(proxy, dict):
                errors.append(f"Proxy {i} is not a dictionary")
                continue

            # Check proxy has at least name and server
            if "name" not in proxy:
                errors.append(f"Proxy {i} missing 'name' field")
            if "server" not in proxy:
                errors.append(f"Proxy {i} missing 'server' field")

    return errors


def validate_file_path(file_path: str) -> Tuple[bool, str]:
    """Validate file path exists and is accessible"""
    path = Path(file_path)

    if not path.exists():
        return False, config.ERROR_MESSAGES["file_not_found"].format(file=file_path)

    if not path.is_file():
        return False, f"Path is not a file: {file_path}"

    # Check file extension
    if path.suffix.lower() not in config.YAML_EXTENSIONS:
        return (
            False,
            f"File must have YAML extension: {', '.join(config.YAML_EXTENSIONS)}",
        )

    # Check file size
    max_size_mb = config.PERFORMANCE_SETTINGS["max_file_size_mb"]
    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, config.ERROR_MESSAGES["file_too_large"].format(
            size=max_size_mb, file=file_path
        )

    return True, ""


def validate_directory_path(dir_path: str) -> Tuple[bool, str]:
    """Validate directory path exists and is accessible"""
    path = Path(dir_path)

    if not path.exists():
        return False, config.ERROR_MESSAGES["directory_not_found"].format(dir=dir_path)

    if not path.is_dir():
        return False, f"Path is not a directory: {dir_path}"

    return True, ""


def validate_proxy_data(proxy: Dict[str, Any]) -> List[str]:
    """Validate individual proxy data"""
    errors = []

    # Check required proxy fields
    required_fields = ["name", "type", "server"]
    for field in required_fields:
        if field not in proxy:
            errors.append(f"Proxy missing required field: {field}")

    # Validate proxy type
    if "type" in proxy and proxy["type"] not in config.CLASH_PROXY_TYPES:
        errors.append(
            f"Invalid proxy type: {proxy['type']}. Must be one of: {', '.join(config.CLASH_PROXY_TYPES)}"
        )

    # Validate server (basic URL/hostname check)
    if "server" in proxy:
        server = proxy["server"]
        # Basic validation - should contain at least a dot or be localhost
        if not re.match(r"^[a-zA-Z0-9.-]+$", server) and server != "localhost":
            errors.append(f"Invalid server address: {server}")

    # Validate port if present
    if "port" in proxy:
        try:
            port = int(proxy["port"])
            if not (1 <= port <= 65535):
                errors.append(f"Invalid port number: {port}")
        except (ValueError, TypeError):
            errors.append(f"Port must be a number: {proxy['port']}")

    return errors


def validate_yaml_content(content: str) -> Tuple[bool, str]:
    """Validate YAML content syntax"""
    try:
        import yaml

        yaml.safe_load(content)
        return True, ""
    except yaml.YAMLError as e:
        return False, f"Invalid YAML syntax: {e}"
    except Exception as e:
        return False, f"Error parsing YAML: {e}"
