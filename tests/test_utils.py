#!/usr/bin/env python3
"""
Tests for utility functions
"""

import pytest
import tempfile
import os
from pathlib import Path
from err_x509.utils import (
    get_platform_info,
    detect_clash_directories,
    calculate_file_hash,
    format_file_size,
    format_duration,
    validate_proxy_url,
    is_valid_ip_address,
    extract_proxy_info,
    create_backup_file,
    find_yaml_files,
    safe_yaml_load,
    safe_yaml_dump,
    print_table,
    get_terminal_size,
    wrap_text,
    get_relative_time,
)


class TestFileUtils:
    def test_get_platform_info(self):
        info = get_platform_info()

        assert "system" in info
        assert "python_version" in info
        assert isinstance(info, dict)

    def test_detect_clash_directories(self):
        dirs = detect_clash_directories()

        # At minimum should return some directories
        assert isinstance(dirs, list)
        assert all(isinstance(d, Path) for d in dirs)

    def test_calculate_file_hash(self, tmp_path):
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        hash_value = calculate_file_hash(str(test_file))

        assert len(hash_value) == 64  # SHA256 hex length
        assert isinstance(hash_value, str)

    def test_format_file_size(self):
        assert format_file_size(0) == "0.00 B"
        assert format_file_size(1024) == "1.00 KB"
        assert format_file_size(1024 * 1024) == "1.00 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.00 GB"

    def test_format_duration(self):
        assert format_duration(0.5) == "500ms"
        assert format_duration(30) == "30.00s"
        assert format_duration(90) == "1m 30s"
        assert format_duration(3660) == "1h 1m"


class TestValidation:
    def test_validate_proxy_url(self):
        assert validate_proxy_url("example.com") is True
        assert validate_proxy_url("192.168.1.1") is True
        assert validate_proxy_url("[2001:db8::1]") is True
        assert validate_proxy_url("") is False
        assert validate_proxy_url("invalid url") is False

    def test_is_valid_ip_address(self):
        assert is_valid_ip_address("192.168.1.1") is True
        assert is_valid_ip_address("255.255.255.255") is True
        assert is_valid_ip_address(
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True

        assert is_valid_ip_address("999.999.999.999") is False
        assert is_valid_ip_address("192.168.1") is False
        assert is_valid_ip_address("not an ip") is False

    def test_extract_proxy_info(self):
        proxy = {
            "name": "test",
            "type": "trojan",
            "server": "example.com",
            "port": 443,
            "skip-cert-verify": False,
            "password": "secret",
        }

        info = extract_proxy_info(proxy)

        assert info["name"] == "test"
        assert info["type"] == "trojan"
        assert info["server"] == "example.com"
        assert info["port"] == 443
        assert info["has_ssl_verify"] is True
        assert info["ssl_verify_value"] is False
        assert info["password"] == "secret"


class TestFileOperations:
    def test_create_backup_file(self, tmp_path):
        original = tmp_path / "test.yaml"
        original.write_text("original content")

        backup = create_backup_file(original)

        assert backup.exists()
        assert backup.read_text() == "original content"
        assert backup != original

    def test_find_yaml_files(self, tmp_path):
        # Create test files
        (tmp_path / "config1.yaml").write_text("test")
        (tmp_path / "config2.yml").write_text("test")
        (tmp_path / "other.txt").write_text("test")

        files = find_yaml_files(tmp_path)

        assert len(files) == 2
        assert any("config1.yaml" in str(f) for f in files)
        assert any("config2.yml" in str(f) for f in files)

    def test_find_yaml_files_recursive(self, tmp_path):
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "config1.yaml").write_text("test")
        (subdir / "config2.yaml").write_text("test")

        files = find_yaml_files(tmp_path, recursive=True)
        assert len(files) == 2

        files = find_yaml_files(tmp_path, recursive=False)
        assert len(files) == 1


class TestYAMLUtils:
    def test_safe_yaml_load_valid(self):
        yaml_content = "key: value\nlist: [1, 2, 3]"

        result = safe_yaml_load(yaml_content)

        assert result["key"] == "value"
        assert result["list"] == [1, 2, 3]

    def test_safe_yaml_load_invalid(self):
        yaml_content = "key: [unclosed list"

        with pytest.raises(ValueError):
            safe_yaml_load(yaml_content)

    def test_safe_yaml_dump(self):
        data = {"key": "value", "list": [1, 2, 3]}

        result = safe_yaml_dump(data)

        assert isinstance(result, str)
        assert "key:" in result
        assert "value" in result


class TestFormatting:
    def test_print_table(self, capsys):
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Charlie", "35", "Paris"],
        ]

        print_table(headers, rows)

        captured = capsys.readouterr()
        assert "Name" in captured.out
        assert "Alice" in captured.out
        assert "Bob" in captured.out

    def test_get_terminal_size(self):
        width, height = get_terminal_size()

        assert isinstance(width, int)
        assert isinstance(height, int)
        assert width > 0
        assert height > 0

    def test_wrap_text(self):
        text = "This is a very long text that needs to be wrapped to fit within a certain width."

        wrapped = wrap_text(text, width=20)

        # Check it was wrapped
        lines = wrapped.split("\n")
        assert len(lines) > 1
        assert all(len(line) <= 20 for line in lines)

    def test_get_relative_time(self):
        from datetime import datetime, timedelta

        now = datetime.now()

        # Just now
        assert get_relative_time(now - timedelta(seconds=30)) == "just now"

        # Minutes ago
        assert "minute" in get_relative_time(now - timedelta(minutes=5))

        # Hours ago
        assert "hour" in get_relative_time(now - timedelta(hours=2))

        # Days ago
        assert "day" in get_relative_time(now - timedelta(days=3))

        # Months ago
        assert "month" in get_relative_time(now - timedelta(days=40))

        # Years ago
        assert "year" in get_relative_time(now - timedelta(days=400))
