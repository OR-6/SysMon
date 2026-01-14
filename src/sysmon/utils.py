"""
Utility functions for SysMon.

Contains helper functions for formatting, conversions, and common operations.
"""

import logging
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta


def setup_logging(
    log_path: Path,
    level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Set up rotating file logger.
    
    Args:
        log_path: Path to log directory
        level: Logging level
        max_bytes: Maximum log file size in bytes
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    log_path.mkdir(parents=True, exist_ok=True)
    log_file = log_path / "sysmon.log"
    
    logger = logging.getLogger("sysmon")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler for errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def bytes_to_gb(bytes_val: int) -> float:
    """Convert bytes to gigabytes."""
    return bytes_val / (1024 ** 3)


def bytes_to_mb(bytes_val: int) -> float:
    """Convert bytes to megabytes."""
    return bytes_val / (1024 ** 2)


def format_uptime(seconds: float) -> str:
    """
    Format uptime in a human-readable way.
    
    Args:
        seconds: Uptime in seconds
    
    Returns:
        Formatted string like "2 days, 3 hours, 45 minutes"
    """
    delta = timedelta(seconds=int(seconds))
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    return ", ".join(parts) if parts else "less than a minute"


def format_bytes(bytes_val: float) -> str:
    """
    Format bytes in human-readable format.
    
    Args:
        bytes_val: Number of bytes
    
    Returns:
        Formatted string with appropriate unit
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def truncate_string(text: str, max_length: int = 30) -> str:
    """
    Truncate string with ellipsis if too long.
    
    Args:
        text: String to truncate
        max_length: Maximum length
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def get_alert_color(percent: float) -> str:
    """
    Get color based on usage percentage.
    
    Args:
        percent: Usage percentage
    
    Returns:
        Color name for rich library
    """
    if percent >= 90:
        return "red"
    elif percent >= 75:
        return "yellow"
    else:
        return "green"