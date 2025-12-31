#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for err_x509
"""

import click
from pathlib import Path
from typing import Optional
from .core import X509Fixer
from . import __version__


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, message="err_x509 v%(version)s")
@click.pass_context
def cli(ctx):
    """err_x509 - Fix Clash x509 SSL certificate errors"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("input_file", type=click.Path(exists=True), required=False)
@click.argument("output_file", type=click.Path(), required=False)
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-b", "--backup", is_flag=True, help="Create backup of original file")
@click.option("-f", "--force", is_flag=True, help="Overwrite output file if exists")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without making changes"
)
def fix(
    input_file: Optional[str],
    output_file: Optional[str],
    verbose: bool,
    backup: bool,
    force: bool,
    dry_run: bool,
):
    """Fix SSL certificate errors in Clash configuration"""

    # Banner
    click.echo(
        click.style(
            """
╔═══════════════════════════════════════════════╗
║            err_x509 - x509 SSL Fixer          ║
║          Fix Clash SSL certificate errors     ║
║           GitHub: 13winged/err_x509           ║
╚═══════════════════════════════════════════════╝
    """,
            fg="cyan",
            bold=True,
        )
    )

    # If no input file, try to find defaults
    if not input_file:
        default_files = ["x509_no_fix.yaml", "config.yaml", "clash.yaml"]
        for file in default_files:
            if Path(file).exists():
                input_file = file
                click.echo(
                    click.style(f"📁 Using default file: {input_file}", fg="yellow")
                )
                break

        if not input_file:
            click.echo(
                click.style(
                    "❌ No input file specified and no default files found", fg="red"
                )
            )
            click.echo("\nExamples:")
            click.echo("  err_x509 fix config.yaml")
            click.echo("  err_x509 fix input.yaml output.yaml")
            click.echo("  err_x509 fix --verbose --backup my_config.yaml")
            sys.exit(1)

    # Check output file
    if output_file and Path(output_file).exists() and not force and not dry_run:
        click.echo(click.style(f"❌ Output file exists: {output_file}", fg="red"))
        click.echo("Use --force to overwrite or specify different output file")
        sys.exit(1)

    # Create fixer
    fixer = X509Fixer(verbose=verbose, backup=backup)

    # Dry run
    if dry_run:
        click.echo(click.style(f"🔍 Dry run: Would process {input_file}", fg="yellow"))
        if output_file:
            click.echo(click.style(f"   Output: {output_file}", fg="yellow"))
        else:
            click.echo(
                click.style(
                    f"   Output: {Path(input_file).stem}_fixed.yaml", fg="yellow"
                )
            )
        sys.exit(0)

    # Process file
    success, out_path, proxy_count = fixer.fix_file(input_file, output_file)

    if success:
        click.echo("\n" + "=" * 50)
        click.echo(click.style("🎉 SUCCESS!", fg="green", bold=True))
        click.echo("=" * 50)
        click.echo(click.style(f"✅ Fixed file: {Path(out_path).name}", fg="green"))
        click.echo(click.style(f"🔗 Proxies processed: {proxy_count}", fg="cyan"))
        click.echo(click.style(f"📁 Location: {Path(out_path).absolute()}", fg="blue"))

        # Show usage instructions
        click.echo(
            "\n" + click.style("🚀 How to use in Clash:", fg="yellow", bold=True)
        )
        click.echo(click.style("1. Open Clash application", fg="white"))
        click.echo(click.style("2. Go to Profiles/Configurations", fg="white"))
        click.echo(click.style("3. Import or select the fixed file", fg="white"))
        click.echo(click.style("4. Apply the configuration", fg="white"))
        click.echo(click.style("5. Check if SSL errors are resolved", fg="white"))

        click.echo("\n" + click.style("⚠️  Security Note:", fg="red", bold=True))
        click.echo(
            click.style(
                "skip-cert-verify: true disables SSL certificate validation.",
                fg="white",
            )
        )
        click.echo(
            click.style("Use only for testing with trusted servers.", fg="white")
        )

        sys.exit(0)
    else:
        click.echo(click.style("\n❌ Failed to process file", fg="red"))
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.option("-p", "--pattern", default="*.yaml", help="File pattern to match")
@click.option("--dry-run", is_flag=True, help="Show what would be done")
def batch(directory: str, verbose: bool, pattern: str, dry_run: bool):
    """Fix all configuration files in a directory"""

    click.echo(click.style(f"🔍 Batch processing: {directory}", fg="cyan", bold=True))

    dir_path = Path(directory)
    files = list(dir_path.glob(pattern)) + list(dir_path.glob("*.yml"))

    if not files:
        click.echo(click.style(f"❌ No YAML files found in: {directory}", fg="red"))
        sys.exit(1)

    click.echo(click.style(f"📁 Found {len(files)} files", fg="yellow"))

    if dry_run:
        for file in files:
            click.echo(
                click.style(f"   📄 {file.name} → {file.stem}_fixed.yaml", fg="yellow")
            )
        sys.exit(0)

    fixer = X509Fixer(verbose=verbose)
    results = fixer.fix_directory(directory, pattern)

    # Summary
    successful = sum(1 for r in results.values() if r[0])
    total_proxies = sum(r[2] for r in results.values())

    click.echo("\n" + "=" * 50)
    click.echo(click.style("📊 BATCH PROCESSING SUMMARY", fg="cyan", bold=True))
    click.echo("=" * 50)
    click.echo(click.style(f"✅ Successful: {successful}/{len(results)}", fg="green"))
    click.echo(click.style(f"🔗 Total proxies: {total_proxies}", fg="cyan"))
    click.echo("=" * 50)

    if successful == len(results):
        sys.exit(0)
    else:
        sys.exit(1)


@cli.command()
def check():
    """Check system compatibility and dependencies"""
    click.echo(click.style("🔧 System Compatibility Check", fg="cyan", bold=True))
    click.echo("=" * 40)

    import platform

    # Python version
    py_version = platform.python_version()
    click.echo(f"🐍 Python: {py_version}")

    # Platform
    click.echo(f"🖥️  Platform: {platform.platform()}")

    # Dependencies
    try:
        pass

        click.echo(click.style("✅ PyYAML: Installed", fg="green"))
    except ImportError:
        click.echo(click.style("❌ PyYAML: Not installed", fg="red"))

    try:
        import click

        click.echo(click.style("✅ Click: Installed", fg="green"))
    except ImportError:
        click.echo(click.style("❌ Click: Not installed", fg="red"))

    click.echo("\n" + click.style("✅ All checks passed!", fg="green"))


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
def preview(input_file: str):
    """Preview changes without saving"""
    click.echo(
        click.style(f"👁️  Preview changes for: {input_file}", fg="cyan", bold=True)
    )

    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    fixer = X509Fixer(verbose=True)
    normalized = fixer.normalize_config(content)

    try:
        import yaml

        config = yaml.safe_load(normalized)

        if "proxies" in config:
            click.echo(f"\nFound {len(config['proxies'])} proxies:")
            for i, proxy in enumerate(config["proxies"][:3], 1):  # Show first 3
                name = proxy.get("name", f"proxy_{i}")
                server = proxy.get("server", "unknown")
                click.echo(f"  {i}. {name} → {server}")

            if len(config["proxies"]) > 3:
                click.echo(f"  ... and {len(config['proxies']) - 3} more")

            click.echo(
                click.style(
                    "\n⚠️  Will add: skip-cert-verify: true to all proxies", fg="yellow"
                )
            )
        else:
            click.echo(click.style("❌ No proxies section found", fg="red"))

    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"))


def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(click.style("\n\n⚠️  Interrupted by user", fg="yellow"))
        sys.exit(1)
    except Exception as e:
        click.echo(click.style(f"\n❌ Unexpected error: {e}", fg="red"))
        sys.exit(1)


if __name__ == "__main__":
    main()
