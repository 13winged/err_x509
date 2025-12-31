#!/usr/bin/env python3
"""
Tests for CLI functionality
"""

import pytest
from click.testing import CliRunner
from err_x509.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def sample_config():
    return """port: 7890
proxies:
  - {name: test1, server: s1.com}
  - {name: test2, server: s2.com}"""


class TestCLI:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "err_x509" in result.output

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "fix" in result.output
        assert "batch" in result.output

    def test_fix_command_success(self, runner, sample_config, tmp_path):
        # Create input file
        input_file = tmp_path / "config.yaml"
        input_file.write_text(sample_config)

        result = runner.invoke(cli, ["fix", str(input_file)])

        assert result.exit_code == 0
        assert "SUCCESS" in result.output
        assert "proxies processed" in result.output

        # Check output file was created
        output_file = tmp_path / "config_fixed.yaml"
        assert output_file.exists()

        # Verify content
        content = output_file.read_text()
        assert "skip-cert-verify: true" in content

    def test_fix_with_output_file(self, runner, sample_config, tmp_path):
        input_file = tmp_path / "input.yaml"
        output_file = tmp_path / "output.yaml"

        input_file.write_text(sample_config)

        result = runner.invoke(cli, ["fix", str(input_file), str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_fix_verbose(self, runner, sample_config, tmp_path):
        input_file = tmp_path / "config.yaml"
        input_file.write_text(sample_config)

        result = runner.invoke(cli, ["fix", "-v", str(input_file)])

        assert result.exit_code == 0
        assert "Processing:" in result.output

    def test_fix_backup(self, runner, sample_config, tmp_path):
        input_file = tmp_path / "config.yaml"
        input_file.write_text(sample_config)

        result = runner.invoke(cli, ["fix", "-b", str(input_file)])

        assert result.exit_code == 0
        # Check if backup was created (look for .backup files)
        backup_files = list(tmp_path.glob("*.backup.yaml"))
        assert len(backup_files) > 0

    def test_fix_dry_run(self, runner, sample_config, tmp_path):
        input_file = tmp_path / "config.yaml"
        input_file.write_text(sample_config)

        result = runner.invoke(cli, ["fix", "--dry-run", str(input_file)])

        assert result.exit_code == 0
        assert "Dry run" in result.output
        # Should not create output file
        output_file = tmp_path / "config_fixed.yaml"
        assert not output_file.exists()

    def test_fix_file_not_found(self, runner):
        result = runner.invoke(cli, ["fix", "nonexistent.yaml"])

        assert result.exit_code != 0
        assert "not found" in result.output or "No input file" in result.output

    def test_batch_command(self, runner, tmp_path):
        # Create multiple config files
        for i in range(3):
            config_file = tmp_path / f"config_{i}.yaml"
            config_file.write_text(
                f"""port: 7890
proxies:
  - {{name: test{i}, server: s{i}.com}}"""
            )

        result = runner.invoke(cli, ["batch", str(tmp_path)])

        assert result.exit_code == 0
        assert "BATCH PROCESSING SUMMARY" in result.output
        assert "Successful: 3/3" in result.output

        # Check output files were created
        for i in range(3):
            output_file = tmp_path / f"config_{i}_fixed.yaml"
            assert output_file.exists()

    def test_batch_empty_directory(self, runner, tmp_path):
        result = runner.invoke(cli, ["batch", str(tmp_path)])

        assert result.exit_code != 0
        assert "No YAML files" in result.output

    def test_preview_command(self, runner, sample_config, tmp_path):
        input_file = tmp_path / "config.yaml"
        input_file.write_text(sample_config)

        result = runner.invoke(cli, ["preview", str(input_file)])

        assert result.exit_code == 0
        assert "Preview" in result.output
        assert "proxies" in result.output

    def test_check_command(self, runner):
        result = runner.invoke(cli, ["check"])

        assert result.exit_code == 0
        assert "System Compatibility Check" in result.output
        assert "Python" in result.output

    def test_no_command_shows_help(self, runner):
        result = runner.invoke(cli)

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "err_x509" in result.output


class TestEdgeCases:
    def test_config_without_proxies(self, runner, tmp_path):
        config = """port: 7890
mode: global"""

        input_file = tmp_path / "config.yaml"
        input_file.write_text(config)

        result = runner.invoke(cli, ["fix", str(input_file)])

        # Should still succeed but warn about no proxies
        assert result.exit_code == 0
        assert "SUCCESS" in result.output

    def test_config_with_comments(self, runner, tmp_path):
        config = """# Clash configuration
port: 7890  # Main port

proxies:
  # Trojan proxy
  - {name: test, server: s.com, port: 443}
# End of file"""

        input_file = tmp_path / "config.yaml"
        input_file.write_text(config)

        result = runner.invoke(cli, ["fix", str(input_file)])

        assert result.exit_code == 0

        # Check comments are preserved
        output_file = tmp_path / "config_fixed.yaml"
        content = output_file.read_text()
        assert "# Clash configuration" in content
        assert "# Trojan proxy" in content

    def test_large_number_of_proxies(self, runner, tmp_path):
        # Create config with many proxies
        proxies = []
        for i in range(100):
            proxies.append(f"  - {{name: proxy_{i}, server: s{i}.com}}")

        config = f"""port: 7890
proxies:
{chr(10).join(proxies)}"""

        input_file = tmp_path / "large_config.yaml"
        input_file.write_text(config)

        result = runner.invoke(cli, ["fix", str(input_file)])

        assert result.exit_code == 0
        assert "100" in result.output  # Should mention number of proxies
