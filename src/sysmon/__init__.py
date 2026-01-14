"""
SysMon - A beautiful terminal-based system monitoring tool.

This package provides a rich CLI interface for monitoring system resources
including CPU, memory, disk, and network usage.
"""

__version__ = "0.1.0"
__author__ = "Numair Khan"
__email__ = "ornor6@gmail.com"

from .core import SystemMonitor
from .models import SystemSnapshot

__all__ = ["SystemMonitor", "SystemSnapshot"]