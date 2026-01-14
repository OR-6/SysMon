"""
Display module using Rich library for beautiful terminal output.

Handles rendering system information in various formats.
"""

from typing import List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import BarColumn, Progress, TextColumn
from rich.live import Live
from rich.text import Text
from rich import box

from .models import SystemSnapshot, ProcessInfo
from .utils import format_uptime, get_alert_color, truncate_string


class DashboardDisplay:
    """Handles rich terminal display for the dashboard."""
    
    def __init__(self):
        self.console = Console()
    
    def create_progress_bar(self, percent: float, width: int = 20) -> Text:
        """Create a simple progress bar as Rich Text object."""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        # Color based on percentage
        color = get_alert_color(percent)
        
        # Create Text object with proper styling
        result = Text()
        result.append(f"[{bar}] ", style=color)
        result.append(f"{percent:.1f}%", style="white")
        return result
    
    def create_header(self, snapshot: SystemSnapshot) -> Panel:
        """Create header panel with system info."""
        info_text = Text()
        info_text.append("🖥️  ", style="bold cyan")
        info_text.append(f"{snapshot.system.hostname}", style="bold white")
        info_text.append(f" | {snapshot.system.os} ({snapshot.system.architecture})", style="dim")
        info_text.append("\n")
        info_text.append("⏱️  ", style="bold cyan")
        info_text.append(f"Uptime: {format_uptime(snapshot.system.uptime_seconds)}", style="white")
        info_text.append("\n")
        info_text.append("🕐 ", style="bold cyan")
        info_text.append(snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S"), style="white")
        
        return Panel(
            info_text,
            title="[bold cyan]System Information[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED
        )
    
    def create_cpu_panel(self, snapshot: SystemSnapshot) -> Panel:
        """Create CPU information panel."""
        cpu = snapshot.cpu
        
        content = Text()
        content.append(f"Cores: {cpu.count}\n", style="white")
        
        if cpu.frequency:
            content.append(f"Frequency: {cpu.frequency:.0f} MHz\n", style="white")
        
        content.append("Usage: ", style="white")
        # Append the Text object directly
        progress_bar = self.create_progress_bar(cpu.percent)
        content.append_text(progress_bar)
        
        # Per-CPU usage if available
        if cpu.per_cpu:
            content.append("\n\n", style="white")
            content.append("Per-Core Usage:\n", style="bold white")
            for i, usage in enumerate(cpu.per_cpu):
                content.append(f"  Core {i}: {usage:5.1f}%\n", style=get_alert_color(usage))
        
        return Panel(
            content,
            title="[bold yellow]⚡ CPU[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        )
    
    def create_memory_panel(self, snapshot: SystemSnapshot) -> Panel:
        """Create memory information panel."""
        mem = snapshot.memory
        
        content = Text()
        content.append(f"Total: {mem.total_gb:.2f} GB\n", style="white")
        content.append(f"Used: {mem.used_gb:.2f} GB\n", style="white")
        content.append(f"Available: {mem.available_gb:.2f} GB\n", style="white")
        content.append("Usage: ", style="white")
        progress_bar = self.create_progress_bar(mem.percent)
        content.append_text(progress_bar)
        
        return Panel(
            content,
            title="[bold blue]🧠 Memory[/bold blue]",
            border_style="blue",
            box=box.ROUNDED
        )
    
    def create_disk_panel(self, snapshot: SystemSnapshot) -> Panel:
        """Create disk information panel."""
        disk = snapshot.disk
        
        content = Text()
        content.append(f"Mount: {disk.mount_point}\n", style="white")
        content.append(f"Total: {disk.total_gb:.2f} GB\n", style="white")
        content.append(f"Used: {disk.used_gb:.2f} GB\n", style="white")
        content.append(f"Free: {disk.free_gb:.2f} GB\n", style="white")
        content.append("Usage: ", style="white")
        progress_bar = self.create_progress_bar(disk.percent)
        content.append_text(progress_bar)
        
        return Panel(
            content,
            title="[bold magenta]💾 Disk[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        )
    
    def create_network_panel(self, snapshot: SystemSnapshot) -> Panel:
        """Create network information panel."""
        net = snapshot.network
        
        content = Text()
        content.append(f"Sent: {net.bytes_sent:.2f} MB\n", style="white")
        content.append(f"Received: {net.bytes_recv:.2f} MB\n", style="white")
        content.append(f"Packets Sent: {net.packets_sent:,}\n", style="white")
        content.append(f"Packets Received: {net.packets_recv:,}", style="white")
        
        return Panel(
            content,
            title="[bold green]🌐 Network[/bold green]",
            border_style="green",
            box=box.ROUNDED
        )
    
    def create_processes_table(self, processes: List[ProcessInfo]) -> Table:
        """Create table of top processes."""
        table = Table(
            title="Top Processes by CPU",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("PID", style="dim", width=8)
        table.add_column("Name", style="white", width=25)
        table.add_column("CPU %", justify="right", width=10)
        table.add_column("Memory %", justify="right", width=10)
        table.add_column("Status", width=10)
        
        for proc in processes:
            name = truncate_string(proc.name, 23)
            cpu_color = get_alert_color(proc.cpu_percent)
            mem_color = get_alert_color(proc.memory_percent)
            
            table.add_row(
                str(proc.pid),
                name,
                f"[{cpu_color}]{proc.cpu_percent:.1f}%[/{cpu_color}]",
                f"[{mem_color}]{proc.memory_percent:.1f}%[/{mem_color}]",
                proc.status
            )
        
        return table
    
    def render_dashboard(self, snapshot: SystemSnapshot) -> Layout:
        """Create complete dashboard layout."""
        layout = Layout()
        
        # Split into sections with better proportions
        layout.split_column(
            Layout(name="header", size=7),  # Increased from 6
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(self.create_header(snapshot))
        
        # Main section - split into top and bottom
        layout["main"].split_column(
            Layout(name="metrics", ratio=2),
            Layout(name="processes", ratio=1)
        )
        
        # Metrics - split into 2x2 grid
        layout["metrics"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="cpu"),
            Layout(name="memory")
        )
        
        layout["right"].split_column(
            Layout(name="disk"),
            Layout(name="network")
        )
        
        # Populate panels
        layout["cpu"].update(self.create_cpu_panel(snapshot))
        layout["memory"].update(self.create_memory_panel(snapshot))
        layout["disk"].update(self.create_disk_panel(snapshot))
        layout["network"].update(self.create_network_panel(snapshot))
        
        # Processes
        if snapshot.top_processes:
            layout["processes"].update(
                Panel(
                    self.create_processes_table(snapshot.top_processes),
                    border_style="cyan",
                    box=box.ROUNDED
                )
            )
        
        # Footer
        footer_text = Text.assemble(
            ("Press ", "white"),
            ("Ctrl+C", "bold red"),
            (" to exit | Refresh: ", "white"),
            ("Active", "bold green")
        )
        layout["footer"].update(
            Panel(footer_text, border_style="dim", box=box.ROUNDED)
        )
        
        return layout
    
    def print_snapshot_summary(self, snapshot: SystemSnapshot) -> None:
        """Print a simple summary of a snapshot (for non-live mode)."""
        self.console.print()
        self.console.print(f"[bold cyan]Snapshot from {snapshot.timestamp}[/bold cyan]")
        self.console.print(f"  CPU: {snapshot.cpu.percent:.1f}%")
        self.console.print(f"  Memory: {snapshot.memory.percent:.1f}%")
        self.console.print(f"  Disk: {snapshot.disk.percent:.1f}%")
        self.console.print()
    
    def print_json(self, snapshot: SystemSnapshot) -> None:
        """Print snapshot as JSON."""
        import json
        data = snapshot.model_dump(mode='json')
        self.console.print_json(json.dumps(data, default=str))
    
    def print_table(self, snapshots: List[SystemSnapshot]) -> None:
        """Print multiple snapshots as a table."""
        table = Table(
            title="System Snapshots",
            box=box.SIMPLE_HEAD,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("Timestamp", style="white")
        table.add_column("CPU %", justify="right")
        table.add_column("Memory %", justify="right")
        table.add_column("Disk %", justify="right")
        
        for snapshot in snapshots:
            cpu_color = get_alert_color(snapshot.cpu.percent)
            mem_color = get_alert_color(snapshot.memory.percent)
            disk_color = get_alert_color(snapshot.disk.percent)
            
            table.add_row(
                snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                f"[{cpu_color}]{snapshot.cpu.percent:.1f}%[/{cpu_color}]",
                f"[{mem_color}]{snapshot.memory.percent:.1f}%[/{mem_color}]",
                f"[{disk_color}]{snapshot.disk.percent:.1f}%[/{disk_color}]"
            )
        
        self.console.print(table)
    
    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[bold red]Error:[/bold red] {message}")
    
    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[bold green]✓[/bold green] {message}")
    
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
    
    def print_info(self, message: str) -> None:
        """Print info message."""
        self.console.print(f"[bold cyan]ℹ[/bold cyan] {message}")