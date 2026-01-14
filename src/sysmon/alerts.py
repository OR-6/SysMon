"""
Alert system for monitoring thresholds.

Provides a simple alert mechanism when system metrics exceed defined thresholds.
"""

from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from .models import SystemSnapshot


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    """Definition of an alert rule."""
    name: str
    metric: str  # e.g., 'cpu.percent', 'memory.percent'
    threshold: float
    level: AlertLevel
    message: str


@dataclass
class Alert:
    """An triggered alert."""
    rule: AlertRule
    value: float
    snapshot_time: str


class AlertManager:
    """Manages alert rules and notifications."""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.callbacks: List[Callable[[Alert], None]] = []
        self.logger = logging.getLogger("sysmon.alerts")
        self._setup_default_rules()
    
    def _setup_default_rules(self) -> None:
        """Set up default alert rules."""
        self.rules = [
            AlertRule(
                name="high_cpu",
                metric="cpu.percent",
                threshold=90.0,
                level=AlertLevel.CRITICAL,
                message="CPU usage is critically high"
            ),
            AlertRule(
                name="high_memory",
                metric="memory.percent",
                threshold=90.0,
                level=AlertLevel.CRITICAL,
                message="Memory usage is critically high"
            ),
            AlertRule(
                name="high_disk",
                metric="disk.percent",
                threshold=90.0,
                level=AlertLevel.WARNING,
                message="Disk usage is high"
            ),
            AlertRule(
                name="warning_cpu",
                metric="cpu.percent",
                threshold=75.0,
                level=AlertLevel.WARNING,
                message="CPU usage is elevated"
            ),
            AlertRule(
                name="warning_memory",
                metric="memory.percent",
                threshold=75.0,
                level=AlertLevel.WARNING,
                message="Memory usage is elevated"
            ),
        ]
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add a custom alert rule."""
        self.rules.append(rule)
    
    def add_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add a callback function to be called when alerts trigger."""
        self.callbacks.append(callback)
    
    def _get_metric_value(self, snapshot: SystemSnapshot, metric_path: str) -> Optional[float]:
        """Extract metric value from snapshot using dot notation."""
        parts = metric_path.split('.')
        value = snapshot
        
        try:
            for part in parts:
                value = getattr(value, part)
            return float(value)
        except (AttributeError, ValueError, TypeError):
            return None
    
    def check_alerts(self, snapshot: SystemSnapshot) -> List[Alert]:
        """
        Check all rules against a snapshot and return triggered alerts.
        
        Args:
            snapshot: System snapshot to check
        
        Returns:
            List of triggered alerts
        """
        triggered = []
        
        for rule in self.rules:
            value = self._get_metric_value(snapshot, rule.metric)
            
            if value is None:
                continue
            
            if value >= rule.threshold:
                alert = Alert(
                    rule=rule,
                    value=value,
                    snapshot_time=snapshot.timestamp.isoformat()
                )
                triggered.append(alert)
                
                # Log the alert
                log_msg = f"{rule.name}: {rule.message} ({value:.1f}%)"
                if rule.level == AlertLevel.CRITICAL:
                    self.logger.critical(log_msg)
                elif rule.level == AlertLevel.WARNING:
                    self.logger.warning(log_msg)
                else:
                    self.logger.info(log_msg)
                
                # Call registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        self.logger.error(f"Alert callback failed: {e}")
        
        return triggered