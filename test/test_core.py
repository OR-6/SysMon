"""
Tests for core system monitoring functionality.
"""

import pytest
from sysmon.core import SystemMonitor
from sysmon.models import SystemSnapshot


def test_system_monitor_initialization():
    """Test that SystemMonitor can be initialized."""
    monitor = SystemMonitor()
    assert monitor is not None


def test_get_system_info():
    """Test getting system information."""
    monitor = SystemMonitor()
    info = monitor.get_system_info()
    
    assert info.os is not None
    assert info.hostname is not None
    assert info.architecture is not None


def test_get_cpu_info():
    """Test getting CPU information."""
    monitor = SystemMonitor()
    cpu = monitor.get_cpu_info()
    
    assert 0 <= cpu.percent <= 100
    assert cpu.count > 0


def test_get_memory_info():
    """Test getting memory information."""
    monitor = SystemMonitor()
    mem = monitor.get_memory_info()
    
    assert mem.total_gb > 0
    assert 0 <= mem.percent <= 100


def test_get_disk_info():
    """Test getting disk information."""
    monitor = SystemMonitor()
    disk = monitor.get_disk_info()
    
    assert disk.total_gb > 0
    assert 0 <= disk.percent <= 100


def test_get_network_info():
    """Test getting network information."""
    monitor = SystemMonitor()
    net = monitor.get_network_info()
    
    assert net.bytes_sent >= 0
    assert net.bytes_recv >= 0


def test_capture_snapshot():
    """Test capturing a complete system snapshot."""
    monitor = SystemMonitor()
    snapshot = monitor.capture_snapshot()
    
    assert isinstance(snapshot, SystemSnapshot)
    assert snapshot.system is not None
    assert snapshot.cpu is not None
    assert snapshot.memory is not None
    assert snapshot.disk is not None
    assert snapshot.network is not None


def test_get_top_processes():
    """Test getting top processes."""
    monitor = SystemMonitor()
    processes = monitor.get_top_processes(count=5)
    
    assert len(processes) <= 5
    # Processes should be sorted by CPU usage
    if len(processes) > 1:
        assert processes[0].cpu_percent >= processes[-1].cpu_percent