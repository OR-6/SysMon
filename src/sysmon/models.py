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


class NetworkInfo(BaseModel):
    """Network statistics."""
    
    bytes_sent: float = Field(..., ge=0, description="Bytes sent in MB")
    bytes_recv: float = Field(..., ge=0, description="Bytes received in MB")
    packets_sent: int = Field(..., ge=0, description="Packets sent")
    packets_recv: int = Field(..., ge=0, description="Packets received")


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


class SystemSnapshot(BaseModel):
    """Complete snapshot of system state at a point in time."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    system: SystemInfo
    cpu: CPUInfo
    memory: MemoryInfo
    disk: DiskInfo
    network: NetworkInfo
    top_processes: List[ProcessInfo] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }