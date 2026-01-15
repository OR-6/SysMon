"""
Data models for system monitoring.

Uses Pydantic for validation and serialization, making it easy to
export data to JSON or other formats.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CPUInfo(BaseModel):
    """CPU usage information."""
    
    percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    count: int = Field(..., gt=0, description="Number of CPU cores")
    frequency: Optional[float] = Field(None, description="CPU frequency in MHz")
    per_cpu: Optional[List[float]] = Field(None, description="Per-core CPU usage")


class MemoryInfo(BaseModel):
    """Memory usage information."""
    
    total_gb: float = Field(..., gt=0, description="Total memory in GB")
    used_gb: float = Field(..., ge=0, description="Used memory in GB")
    available_gb: float = Field(..., ge=0, description="Available memory in GB")
    percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")


class DiskInfo(BaseModel):
    """Disk usage information."""
    
    total_gb: float = Field(..., gt=0, description="Total disk space in GB")
    used_gb: float = Field(..., ge=0, description="Used disk space in GB")
    free_gb: float = Field(..., ge=0, description="Free disk space in GB")
    percent: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    mount_point: str = Field(default="/", description="Disk mount point")


class DiskIOInfo(BaseModel):
    """Disk I/O statistics."""
    
    read_bytes_mb: float = Field(..., ge=0, description="Total bytes read in MB")
    write_bytes_mb: float = Field(..., ge=0, description="Total bytes written in MB")
    read_count: int = Field(..., ge=0, description="Number of read operations")
    write_count: int = Field(..., ge=0, description="Number of write operations")
    read_time_ms: float = Field(..., ge=0, description="Total read time in milliseconds")
    write_time_ms: float = Field(..., ge=0, description="Total write time in milliseconds")


class NetworkInfo(BaseModel):
    """Network statistics."""
    
    bytes_sent: float = Field(..., ge=0, description="Bytes sent in MB")
    bytes_recv: float = Field(..., ge=0, description="Bytes received in MB")
    packets_sent: int = Field(..., ge=0, description="Packets sent")
    packets_recv: int = Field(..., ge=0, description="Packets received")


class NetworkInterfaceInfo(BaseModel):
    """Network interface statistics."""
    
    name: str = Field(..., description="Interface name")
    bytes_sent: float = Field(..., ge=0, description="Bytes sent in MB")
    bytes_recv: float = Field(..., ge=0, description="Bytes received in MB")
    packets_sent: int = Field(..., ge=0, description="Packets sent")
    packets_recv: int = Field(..., ge=0, description="Packets received")
    is_up: bool = Field(default=True, description="Interface is up/active")
    ip_addr: Optional[str] = Field(None, description="IP address")


class ProcessInfo(BaseModel):
    """Information about a running process."""
    
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str


class SystemInfo(BaseModel):
    """Basic system information."""
    
    os: str
    os_version: str
    hostname: str
    architecture: str
    boot_time: datetime
    uptime_seconds: float


class AlertConfig(BaseModel):
    """Alert threshold configuration."""
    
    cpu_threshold: float = Field(default=80.0, ge=0, le=100, description="CPU usage alert threshold")
    memory_threshold: float = Field(default=85.0, ge=0, le=100, description="Memory usage alert threshold")
    disk_threshold: float = Field(default=90.0, ge=0, le=100, description="Disk usage alert threshold")
    enabled: bool = Field(default=True, description="Enable alerts")


class Alert(BaseModel):
    """System alert."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    alert_type: str = Field(..., description="Type of alert (cpu, memory, disk)")
    severity: str = Field(..., description="Severity level (warning, critical)")
    message: str = Field(..., description="Alert message")
    current_value: float = Field(..., description="Current metric value")
    threshold: float = Field(..., description="Threshold that was exceeded")


class SystemSnapshot(BaseModel):
    """Complete snapshot of system state at a point in time."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    system: SystemInfo
    cpu: CPUInfo
    memory: MemoryInfo
    disk: DiskInfo
    disk_io: Optional[DiskIOInfo] = Field(None, description="Disk I/O statistics")
    network: NetworkInfo
    network_interfaces: Optional[List[NetworkInterfaceInfo]] = Field(None, description="Per-interface network stats")
    top_processes: List[ProcessInfo] = Field(default_factory=list)
    alerts: List[Alert] = Field(default_factory=list, description="System alerts triggered")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }