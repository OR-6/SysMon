#!/usr/bin/env python3
"""
Cross-platform launcher for SysMon.
Works on Windows, macOS, and Linux.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run
from sysmon.cli import main

if __name__ == "__main__":
    main()