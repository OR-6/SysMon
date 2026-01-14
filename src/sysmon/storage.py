"""
Storage layer for persisting system snapshots.

Supports multiple backends (JSON, SQLite) with a common interface.
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import logging

from .models import SystemSnapshot


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save(self, snapshot: SystemSnapshot) -> None:
        """Save a snapshot."""
        pass
    
    @abstractmethod
    def load(self, limit: Optional[int] = None) -> List[SystemSnapshot]:
        """Load snapshots."""
        pass
    
    @abstractmethod
    def cleanup(self, max_records: int) -> int:
        """Clean up old records, return number deleted."""
        pass
    
    @abstractmethod
    def export(self, output_path: Path) -> None:
        """Export data to file."""
        pass


class JSONStorage(StorageBackend):
    """JSON file-based storage backend."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.data_file = self.storage_path / "snapshots.json"
        self.logger = logging.getLogger("sysmon.storage")
    
    def save(self, snapshot: SystemSnapshot) -> None:
        """Save snapshot to JSON file."""
        try:
            # Load existing data
            snapshots = self._load_raw()
            
            # Add new snapshot
            snapshots.append(snapshot.model_dump(mode='json'))
            
            # Save back
            with open(self.data_file, 'w') as f:
                json.dump(snapshots, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
            raise
    
    def load(self, limit: Optional[int] = None) -> List[SystemSnapshot]:
        """Load snapshots from JSON file."""
        try:
            data = self._load_raw()
            
            # Parse into models
            snapshots = [SystemSnapshot(**item) for item in data]
            
            # Sort by timestamp (newest first)
            snapshots.sort(key=lambda x: x.timestamp, reverse=True)
            
            if limit:
                snapshots = snapshots[:limit]
            
            return snapshots
            
        except Exception as e:
            self.logger.error(f"Error loading snapshots: {e}")
            return []
    
    def _load_raw(self) -> List[dict]:
        """Load raw JSON data."""
        if not self.data_file.exists():
            return []
        
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            self.logger.warning("Corrupt JSON file, starting fresh")
            return []
    
    def cleanup(self, max_records: int) -> int:
        """Keep only the most recent N records."""
        try:
            snapshots = self._load_raw()
            
            if len(snapshots) <= max_records:
                return 0
            
            # Sort by timestamp and keep newest
            snapshots.sort(
                key=lambda x: x.get('timestamp', ''),
                reverse=True
            )
            kept_snapshots = snapshots[:max_records]
            
            # Save back
            with open(self.data_file, 'w') as f:
                json.dump(kept_snapshots, f, indent=2, default=str)
            
            deleted = len(snapshots) - max_records
            self.logger.info(f"Cleaned up {deleted} old records")
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0
    
    def export(self, output_path: Path) -> None:
        """Export data to another JSON file."""
        try:
            snapshots = self._load_raw()
            
            with open(output_path, 'w') as f:
                json.dump(snapshots, f, indent=2, default=str)
            
            self.logger.info(f"Exported {len(snapshots)} snapshots to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            raise


class SQLiteStorage(StorageBackend):
    """SQLite database storage backend."""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.db_file = self.storage_path / "snapshots.db"
        self.logger = logging.getLogger("sysmon.storage")
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON snapshots(timestamp)
            """)
    
    def save(self, snapshot: SystemSnapshot) -> None:
        """Save snapshot to database."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute(
                    "INSERT INTO snapshots (timestamp, data) VALUES (?, ?)",
                    (
                        snapshot.timestamp.isoformat(),
                        json.dumps(snapshot.model_dump(mode='json'), default=str)
                    )
                )
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
            raise
    
    def load(self, limit: Optional[int] = None) -> List[SystemSnapshot]:
        """Load snapshots from database."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                query = "SELECT data FROM snapshots ORDER BY timestamp DESC"
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                
                snapshots = []
                for row in rows:
                    data = json.loads(row[0])
                    snapshots.append(SystemSnapshot(**data))
                
                return snapshots
                
        except Exception as e:
            self.logger.error(f"Error loading snapshots: {e}")
            return []
    
    def cleanup(self, max_records: int) -> int:
        """Keep only the most recent N records."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                # Get total count
                cursor = conn.execute("SELECT COUNT(*) FROM snapshots")
                total = cursor.fetchone()[0]
                
                if total <= max_records:
                    return 0
                
                # Delete old records
                conn.execute("""
                    DELETE FROM snapshots WHERE id NOT IN (
                        SELECT id FROM snapshots 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    )
                """, (max_records,))
                
                deleted = total - max_records
                self.logger.info(f"Cleaned up {deleted} old records")
                return deleted
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return 0
    
    def export(self, output_path: Path) -> None:
        """Export data to JSON file."""
        try:
            snapshots = self.load()
            
            # Convert to dict format
            data = [s.model_dump(mode='json') for s in snapshots]
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Exported {len(snapshots)} snapshots to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {e}")
            raise


class StorageManager:
    """Manages storage operations with automatic backend selection."""
    
    def __init__(self, backend_type: str, storage_path: Path):
        self.backend: StorageBackend
        
        if backend_type.lower() == "sqlite":
            self.backend = SQLiteStorage(storage_path)
        else:
            self.backend = JSONStorage(storage_path)
    
    def save(self, snapshot: SystemSnapshot) -> None:
        """Save a snapshot."""
        self.backend.save(snapshot)
    
    def load(self, limit: Optional[int] = None) -> List[SystemSnapshot]:
        """Load snapshots."""
        return self.backend.load(limit)
    
    def cleanup(self, max_records: int) -> int:
        """Clean up old records."""
        return self.backend.cleanup(max_records)
    
    def export(self, output_path: Path) -> None:
        """Export data."""
        self.backend.export(output_path)