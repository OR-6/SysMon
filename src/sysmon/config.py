"""
Configuration management for SysMon.

Handles loading/saving configuration from YAML files and provides
sensible defaults for all settings.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from pydantic import BaseModel, Field


class DisplayConfig(BaseModel):
    """Display settings."""
    
    refresh_interval: int = Field(default=2, ge=1, description="Refresh interval in seconds")
    show_per_cpu: bool = Field(default=False, description="Show per-CPU usage")
    show_processes: bool = Field(default=True, description="Show top processes")
    process_count: int = Field(default=5, ge=1, le=20, description="Number of processes to show")
    progress_bar_width: int = Field(default=30, ge=10, le=50, description="Progress bar width")


class StorageConfig(BaseModel):
    """Storage settings."""
    
    enabled: bool = Field(default=False, description="Enable data logging")
    backend: str = Field(default="json", description="Storage backend (json/sqlite)")
    path: str = Field(default="~/.local/share/sysmon/data", description="Storage path")
    max_records: int = Field(default=1000, ge=100, description="Maximum records to keep")


class LoggingConfig(BaseModel):
    """Logging settings."""
    
    enabled: bool = Field(default=True, description="Enable logging")
    level: str = Field(default="INFO", description="Log level")
    path: str = Field(default="~/.local/share/sysmon/logs", description="Log directory")
    max_size_mb: int = Field(default=10, ge=1, description="Max log file size in MB")
    backup_count: int = Field(default=3, ge=1, description="Number of backup log files")


class Config(BaseModel):
    """Main configuration."""
    
    display: DisplayConfig = Field(default_factory=DisplayConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


class ConfigManager:
    """Manages configuration loading, saving, and validation."""
    
    DEFAULT_CONFIG_DIR = Path.home() / ".config" / "sysmon"
    DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self.DEFAULT_CONFIG_FILE
        self.config: Optional[Config] = None
    
    def load(self) -> Config:
        """Load configuration from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f) or {}
                self.config = Config(**data)
            except Exception as e:
                # If config is invalid, fall back to defaults
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration.")
                self.config = Config()
        else:
            self.config = Config()
        
        return self.config
    
    def save(self, config: Optional[Config] = None) -> None:
        """Save configuration to file."""
        if config:
            self.config = config
        
        if not self.config:
            self.config = Config()
        
        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and save
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(
                self.config.model_dump(),
                f,
                default_flow_style=False,
                sort_keys=False
            )
    
    def get(self) -> Config:
        """Get current configuration."""
        if not self.config:
            self.load()
        return self.config
    
    def reset(self) -> Config:
        """Reset to default configuration."""
        self.config = Config()
        self.save()
        return self.config