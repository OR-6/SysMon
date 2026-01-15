"""
Core system monitoring functionality.

This module handles all the heavy lifting of gathering system metrics
using psutil and organizing them into our data models.
"""

import psutil
import platform
from datetime import datetime
from typing import List, Optional, Dict
import logging

from .models import (
    SystemSnapshot,
    SystemInfo,
    CPUInfo,
    MemoryInfo,
    DiskInfo,
    DiskIOInfo,
    NetworkInfo,
    NetworkInterfaceInfo,
    ProcessInfo,
    Alert,
    AlertConfig
)
from .utils import bytes_to_gb, bytes_to_mb


class SystemMonitor:
    """
    Main system monitoring class.
    
    Collects various system metrics and packages them into structured data.
    """
    
    def __init__(self, alert_config: Optional[AlertConfig] = None):
        self.logger = logging.getLogger("sysmon")
        self._boot_time = datetime.fromtimestamp(psutil.boot_time())
        self.alert_config = alert_config or AlertConfig()
        self._previous_disk_io = None
    
    def get_system_info(self) -> SystemInfo:
        """Gather basic system information."""
        try:
            uptime = (datetime.now() - self._boot_time).total_seconds()
            
            return SystemInfo(
                os=platform.system(),
                os_version=platform.version(),
                hostname=platform.node(),
                architecture=platform.machine(),
                boot_time=self._boot_time,
                uptime_seconds=uptime
            )
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            raise
    
    def get_cpu_info(self, per_cpu: bool = False) -> CPUInfo:
        """
        Gather CPU usage information.
        
        Args:
            per_cpu: If True, include per-core usage
        
        Returns:
            CPUInfo object with current CPU metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            per_cpu_percent = None
            if per_cpu:
                per_cpu_percent = psutil.cpu_percent(interval=0, percpu=True)
            freq = psutil.cpu_freq()
            frequency = freq.current if freq else None
            return CPUInfo(
                percent=cpu_percent,
                count=psutil.cpu_count(),
                frequency=frequency,
                per_cpu=per_cpu_percent
            )
        except Exception as e:
            self.logger.error(f"Error getting CPU info: {e}")
            raise
    
    def get_memory_info(self) -> MemoryInfo:
        """Gather memory usage information."""
        try:
            mem = psutil.virtual_memory()
            return MemoryInfo(
                total_gb=bytes_to_gb(mem.total),
                used_gb=bytes_to_gb(mem.used),
                available_gb=bytes_to_gb(mem.available),
                percent=mem.percent
            )
        except Exception as e:
            self.logger.error(f"Error getting memory info: {e}")
            raise
    
    def get_disk_info(self, mount_point: str = "/") -> DiskInfo:
        """
        Gather disk usage information.
        
        Args:
            mount_point: Disk mount point to check
        
        Returns:
            DiskInfo object with disk metrics
        """
        try:
            disk = psutil.disk_usage(mount_point)
            return DiskInfo(
                total_gb=bytes_to_gb(disk.total),
                used_gb=bytes_to_gb(disk.used),
                free_gb=bytes_to_gb(disk.free),
                percent=disk.percent,
                mount_point=mount_point
            )
        except Exception as e:
            self.logger.error(f"Error getting disk info for {mount_point}: {e}")
            raise
    
    def get_disk_io_info(self) -> Optional[DiskIOInfo]:
        """
        Gather disk I/O statistics.
        
        Returns:
            DiskIOInfo object with I/O metrics or None if unavailable
        """
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters is None:
                return None
            return DiskIOInfo(
                read_bytes_mb=bytes_to_mb(io_counters.read_bytes),
                write_bytes_mb=bytes_to_mb(io_counters.write_bytes),
                read_count=io_counters.read_count,
                write_count=io_counters.write_count,
                read_time_ms=io_counters.read_time,
                write_time_ms=io_counters.write_time
            )
        except Exception as e:
            self.logger.warning(f"Could not get disk I/O info: {e}")
            return None
    
    def get_network_info(self) -> NetworkInfo:
        """Gather network statistics."""
        try:
            net = psutil.net_io_counters()
            return NetworkInfo(
                bytes_sent=bytes_to_mb(net.bytes_sent),
                bytes_recv=bytes_to_mb(net.bytes_recv),
                packets_sent=net.packets_sent,
                packets_recv=net.packets_recv
            )
        except Exception as e:
            self.logger.error(f"Error getting network info: {e}")
            raise
    
    def get_network_interfaces(self) -> Optional[List[NetworkInterfaceInfo]]:
        """
        Get per-interface network statistics.
        
        Returns:
            List of NetworkInterfaceInfo objects for each interface
        """
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            for interface_name in io_counters:
                try:
                    if_io = io_counters[interface_name]
                    if_stat = net_if_stats.get(interface_name)
                    ip_addr = None
                    if interface_name in net_if_addrs:
                        addrs = net_if_addrs[interface_name]
                        for addr in addrs:
                            if addr.family.name == 'AF_INET':
                                ip_addr = addr.address
                                break
                    is_up = if_stat.isup if if_stat else True
                    interfaces.append(NetworkInterfaceInfo(
                        name=interface_name,
                        bytes_sent=bytes_to_mb(if_io.bytes_sent),
                        bytes_recv=bytes_to_mb(if_io.bytes_recv),
                        packets_sent=if_io.packets_sent,
                        packets_recv=if_io.packets_recv,
                        is_up=is_up,
                        ip_addr=ip_addr
                    ))
                except Exception as e:
                    self.logger.debug(f"Error getting stats for interface {interface_name}: {e}")
                    continue
            return interfaces if interfaces else None
        except Exception as e:
            self.logger.warning(f"Could not get network interface info: {e}")
            return None
    
    def get_top_processes(self, count: int = 5) -> List[ProcessInfo]:
        """
        Get top processes by CPU usage.
        
        Args:
            count: Number of processes to return
        
        Returns:
            List of ProcessInfo objects sorted by CPU usage
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    if pinfo['pid'] == 0:
                        continue
                    cpu_pct = pinfo['cpu_percent'] or 0.0
                    if cpu_pct == 0.0:
                        continue
                    processes.append(ProcessInfo(
                        pid=pinfo['pid'],
                        name=pinfo['name'],
                        cpu_percent=cpu_pct,
                        memory_percent=pinfo['memory_percent'] or 0.0,
                        status=pinfo['status']
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            return processes[:count]
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return []
    
    def check_alerts(self, snapshot: SystemSnapshot) -> List[Alert]:
        """
        Check system metrics against alert thresholds.
        
        Args:
            snapshot: Current system snapshot
        
        Returns:
            List of Alert objects for triggered alerts
        """
        alerts = []
        if not self.alert_config.enabled:
            return alerts
        if snapshot.cpu.percent >= self.alert_config.cpu_threshold:
            severity = "critical" if snapshot.cpu.percent >= 95 else "warning"
            alerts.append(Alert(
                alert_type="cpu",
                severity=severity,
                message=f"CPU usage is {snapshot.cpu.percent:.1f}%",
                current_value=snapshot.cpu.percent,
                threshold=self.alert_config.cpu_threshold
            ))
        if snapshot.memory.percent >= self.alert_config.memory_threshold:
            severity = "critical" if snapshot.memory.percent >= 95 else "warning"
            alerts.append(Alert(
                alert_type="memory",
                severity=severity,
                message=f"Memory usage is {snapshot.memory.percent:.1f}%",
                current_value=snapshot.memory.percent,
                threshold=self.alert_config.memory_threshold
            ))
        if snapshot.disk.percent >= self.alert_config.disk_threshold:
            severity = "critical" if snapshot.disk.percent >= 95 else "warning"
            alerts.append(Alert(
                alert_type="disk",
                severity=severity,
                message=f"Disk usage is {snapshot.disk.percent:.1f}%",
                current_value=snapshot.disk.percent,
                threshold=self.alert_config.disk_threshold
            ))
        return alerts
    
    def capture_snapshot(
        self,
        per_cpu: bool = False,
        include_processes: bool = True,
        process_count: int = 5,
        include_disk_io: bool = True,
        include_network_interfaces: bool = False,
        check_alerts: bool = True
    ) -> SystemSnapshot:
        """
        Capture complete system snapshot.
        
        Args:
            per_cpu: Include per-CPU usage
            include_processes: Include top processes
            process_count: Number of processes to include
            include_disk_io: Include disk I/O statistics
            include_network_interfaces: Include per-interface network stats
            check_alerts: Check system alerts
        
        Returns:
            Complete system snapshot
        """
        try:
            snapshot = SystemSnapshot(
                timestamp=datetime.now(),
                system=self.get_system_info(),
                cpu=self.get_cpu_info(per_cpu=per_cpu),
                memory=self.get_memory_info(),
                disk=self.get_disk_info(),
                network=self.get_network_info(),
                top_processes=[]
            )
            if include_disk_io:
                snapshot.disk_io = self.get_disk_io_info()
            if include_network_interfaces:
                snapshot.network_interfaces = self.get_network_interfaces()
            if include_processes:
                snapshot.top_processes = self.get_top_processes(count=process_count)
            if check_alerts:
                snapshot.alerts = self.check_alerts(snapshot)
            return snapshot
        except Exception as e:
            self.logger.error(f"Error capturing snapshot: {e}")
            raise