"""
Core system monitoring functionality.

This module handles all the heavy lifting of gathering system metrics
using psutil and organizing them into our data models.
"""

import psutil
import platform
from datetime import datetime
from typing import List, Optional
import logging

from .models import (
    SystemSnapshot,
    SystemInfo,
    CPUInfo,
    MemoryInfo,
    DiskInfo,
    NetworkInfo,
    ProcessInfo
)
from .utils import bytes_to_gb, bytes_to_mb


class SystemMonitor:
    """
    Main system monitoring class.
    
    Collects various system metrics and packages them into structured data.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("sysmon")
        self._boot_time = datetime.fromtimestamp(psutil.boot_time())
    
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
            # Get overall CPU percentage (interval=1 for accurate reading)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get per-CPU percentages if requested
            per_cpu_percent = None
            if per_cpu:
                per_cpu_percent = psutil.cpu_percent(interval=0, percpu=True)
            
            # Get CPU frequency (may not be available on all systems)
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
                    
                    # Skip System Idle Process (PID 0) as it shows inverse CPU usage
                    if pinfo['pid'] == 0:
                        continue
                    
                    # Get actual CPU percentage
                    cpu_pct = pinfo['cpu_percent'] or 0.0
                    
                    # Skip processes with 0% CPU to show more meaningful data
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
                    # Process disappeared or we don't have permission
                    continue
            
            # Sort by CPU usage and return top N
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            return processes[:count]
            
        except Exception as e:
            self.logger.error(f"Error getting process info: {e}")
            return []
    
    def capture_snapshot(
        self,
        per_cpu: bool = False,
        include_processes: bool = True,
        process_count: int = 5
    ) -> SystemSnapshot:
        """
        Capture complete system snapshot.
        
        Args:
            per_cpu: Include per-CPU usage
            include_processes: Include top processes
            process_count: Number of processes to include
        
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
            
            if include_processes:
                snapshot.top_processes = self.get_top_processes(count=process_count)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Error capturing snapshot: {e}")
            raise