"""
Command-line interface for SysMon.

Built with Click for a robust, user-friendly CLI experience.
"""

import sys
import time
from pathlib import Path
from typing import Optional
import click
from rich.live import Live

from . import __version__
from .core import SystemMonitor
from .display import DashboardDisplay
from .storage import StorageManager
from .config import ConfigManager, Config
from .utils import setup_logging


# Create shared context object
class Context:
    """Shared context for CLI commands."""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        self.display = DashboardDisplay()
        self.monitor = SystemMonitor()
        
        # Setup logging if enabled
        if self.config.logging.enabled:
            log_path = Path(self.config.logging.path).expanduser()
            setup_logging(
                log_path=log_path,
                level=self.config.logging.level,
                max_bytes=self.config.logging.max_size_mb * 1024 * 1024,
                backup_count=self.config.logging.backup_count
            )


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.version_option(version=__version__, prog_name="sysmon")
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
@click.option('-q', '--quiet', is_flag=True, help='Suppress non-essential output')
@click.pass_context
def cli(ctx, verbose, quiet):
    """
    SysMon - Beautiful system monitoring in your terminal.
    
    A lightweight, extensible system monitoring tool that displays
    real-time CPU, memory, disk, and network statistics.
    """
    ctx.obj = Context()
    ctx.obj.verbose = verbose
    ctx.obj.quiet = quiet


@cli.command()
@click.option('-i', '--interval', default=None, type=int, 
              help='Refresh interval in seconds')
@click.option('--per-cpu', is_flag=True, 
              help='Show per-CPU core usage')
@click.option('--no-processes', is_flag=True, 
              help='Hide process list')
@click.option('--json', 'output_json', is_flag=True,
              help='Output single snapshot as JSON')
@pass_context
def monitor(ctx, interval, per_cpu, no_processes, output_json):
    """
    Start the interactive system monitor dashboard.
    
    This displays a live updating dashboard with system metrics.
    Press Ctrl+C to exit.
    
    Examples:
        sysmon monitor                    # Start with default settings
        sysmon monitor -i 5               # Update every 5 seconds
        sysmon monitor --per-cpu          # Show individual CPU cores
        sysmon monitor --json             # Output single JSON snapshot
    """
    config = ctx.config
    
    # Override config with CLI options
    if interval:
        config.display.refresh_interval = interval
    if per_cpu:
        config.display.show_per_cpu = True
    if no_processes:
        config.display.show_processes = False
    
    try:
        # JSON output mode - single snapshot
        if output_json:
            snapshot = ctx.monitor.capture_snapshot(
                per_cpu=config.display.show_per_cpu,
                include_processes=config.display.show_processes,
                process_count=config.display.process_count
            )
            ctx.display.print_json(snapshot)
            return
        
        # Interactive dashboard mode
        if not ctx.quiet:
            ctx.display.print_info("Starting system monitor...")
            ctx.display.print_info(f"Refresh interval: {config.display.refresh_interval}s")
            ctx.display.print_info("Press Ctrl+C to exit\n")
            time.sleep(1)
        
        # Initialize storage if enabled
        storage = None
        if config.storage.enabled:
            storage_path = Path(config.storage.path).expanduser()
            storage = StorageManager(config.storage.backend, storage_path)
        
        # Live updating dashboard
        with Live(
            ctx.display.render_dashboard(
                ctx.monitor.capture_snapshot(
                    per_cpu=config.display.show_per_cpu,
                    include_processes=config.display.show_processes,
                    process_count=config.display.process_count
                )
            ),
            refresh_per_second=1,
            screen=True
        ) as live:
            while True:
                snapshot = ctx.monitor.capture_snapshot(
                    per_cpu=config.display.show_per_cpu,
                    include_processes=config.display.show_processes,
                    process_count=config.display.process_count
                )
                
                # Save to storage if enabled
                if storage:
                    storage.save(snapshot)
                
                # Update display
                live.update(ctx.display.render_dashboard(snapshot))
                
                time.sleep(config.display.refresh_interval)
                
    except KeyboardInterrupt:
        if not ctx.quiet:
            ctx.display.console.clear()
            ctx.display.print_success("Monitor stopped. Goodbye!")
    except Exception as e:
        ctx.display.print_error(f"An error occurred: {e}")
        sys.exit(1)


@cli.command()
@click.option('-n', '--limit', default=10, type=int,
              help='Number of snapshots to show')
@click.option('--json', 'output_json', is_flag=True,
              help='Output as JSON')
@pass_context
def history(ctx, limit, output_json):
    """
    View historical system snapshots.
    
    Displays previously recorded system metrics from storage.
    Requires storage to be enabled in config.
    
    Examples:
        sysmon history              # Show last 10 snapshots
        sysmon history -n 20        # Show last 20 snapshots
        sysmon history --json       # Output as JSON
    """
    config = ctx.config
    
    if not config.storage.enabled:
        ctx.display.print_error("Storage is not enabled.")
        ctx.display.print_info("Enable storage in config: sysmon config set storage.enabled true")
        sys.exit(1)
    
    try:
        storage_path = Path(config.storage.path).expanduser()
        storage = StorageManager(config.storage.backend, storage_path)
        
        snapshots = storage.load(limit=limit)
        
        if not snapshots:
            ctx.display.print_warning("No snapshots found in storage.")
            return
        
        if output_json:
            import json
            data = [s.model_dump(mode='json') for s in snapshots]
            ctx.display.console.print_json(json.dumps(data, default=str))
        else:
            ctx.display.print_table(snapshots)
            
    except Exception as e:
        ctx.display.print_error(f"Failed to load history: {e}")
        sys.exit(1)


@cli.command()
@click.argument('output_path', type=click.Path())
@pass_context
def export(ctx, output_path):
    """
    Export stored snapshots to a file.
    
    Exports all stored system snapshots to a JSON file.
    
    Examples:
        sysmon export snapshots.json
        sysmon export ~/backup/system-data.json
    """
    config = ctx.config
    
    if not config.storage.enabled:
        ctx.display.print_error("Storage is not enabled.")
        sys.exit(1)
    
    try:
        storage_path = Path(config.storage.path).expanduser()
        storage = StorageManager(config.storage.backend, storage_path)
        
        output_file = Path(output_path)
        storage.export(output_file)
        
        ctx.display.print_success(f"Data exported to {output_file}")
        
    except Exception as e:
        ctx.display.print_error(f"Export failed: {e}")
        sys.exit(1)


@cli.group()
def config():
    """
    Manage SysMon configuration.
    
    View and modify configuration settings.
    """
    pass


@config.command(name='show')
@pass_context
def config_show(ctx):
    """Display current configuration."""
    import yaml
    
    config_dict = ctx.config.model_dump()
    ctx.display.console.print("\n[bold cyan]Current Configuration:[/bold cyan]\n")
    ctx.display.console.print(yaml.dump(config_dict, default_flow_style=False))


@config.command(name='path')
@pass_context
def config_path(ctx):
    """Show configuration file path."""
    ctx.display.console.print(f"\nConfig file: [cyan]{ctx.config_manager.config_path}[/cyan]\n")


@config.command(name='set')
@click.argument('key')
@click.argument('value')
@pass_context
def config_set(ctx, key, value):
    """
    Set a configuration value.
    
    Examples:
        sysmon config set display.refresh_interval 5
        sysmon config set storage.enabled true
        sysmon config set storage.backend sqlite
    """
    try:
        # Parse the key path
        keys = key.split('.')
        config_dict = ctx.config.model_dump()
        
        # Navigate to the right nested dict
        current = config_dict
        for k in keys[:-1]:
            if k not in current:
                ctx.display.print_error(f"Invalid config key: {key}")
                return
            current = current[k]
        
        # Convert value to appropriate type
        final_key = keys[-1]
        if final_key not in current:
            ctx.display.print_error(f"Invalid config key: {key}")
            return
        
        # Try to maintain the original type
        original_value = current[final_key]
        if isinstance(original_value, bool):
            value = value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(original_value, int):
            value = int(value)
        elif isinstance(original_value, float):
            value = float(value)
        
        current[final_key] = value
        
        # Save updated config
        new_config = Config(**config_dict)
        ctx.config_manager.save(new_config)
        
        ctx.display.print_success(f"Set {key} = {value}")
        
    except Exception as e:
        ctx.display.print_error(f"Failed to set config: {e}")
        sys.exit(1)


@config.command(name='reset')
@click.confirmation_option(prompt='Are you sure you want to reset all settings?')
@pass_context
def config_reset(ctx):
    """Reset configuration to defaults."""
    try:
        ctx.config_manager.reset()
        ctx.display.print_success("Configuration reset to defaults")
    except Exception as e:
        ctx.display.print_error(f"Failed to reset config: {e}")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all stored data?')
@pass_context
def clear(ctx):
    """
    Clear all stored snapshot data.
    
    This will delete all historical system snapshots from storage.
    This action cannot be undone.
    """
    config = ctx.config
    
    if not config.storage.enabled:
        ctx.display.print_error("Storage is not enabled.")
        sys.exit(1)
    
    try:
        storage_path = Path(config.storage.path).expanduser()
        
        # Remove storage files
        if config.storage.backend == 'sqlite':
            db_file = storage_path / 'snapshots.db'
            if db_file.exists():
                db_file.unlink()
        else:
            json_file = storage_path / 'snapshots.json'
            if json_file.exists():
                json_file.unlink()
        
        ctx.display.print_success("All stored data cleared")
        
    except Exception as e:
        ctx.display.print_error(f"Failed to clear data: {e}")
        sys.exit(1)


@cli.command()
@pass_context
def snapshot(ctx):
    """
    Take a single snapshot and display it.
    
    Captures current system state and displays it in a simple format.
    """
    try:
        snap = ctx.monitor.capture_snapshot(
            per_cpu=False,
            include_processes=True,
            process_count=5
        )
        ctx.display.print_snapshot_summary(snap)
        
    except Exception as e:
        ctx.display.print_error(f"Failed to capture snapshot: {e}")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console = DashboardDisplay().console
        console.print(f"[bold red]Fatal error:[/bold red] {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()