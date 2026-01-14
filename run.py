#!/usr/bin/env python3
"""
Cross-platform launcher for SysMon.
Works on Windows, macOS, and Linux.
"""
import sys
from pathlib import Path

def main():
    # Add src to path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        # Import and run
        from sysmon.cli import main as cli_main
        cli_main()
    except ImportError as e:
        print(f"Error: Could not import sysmon module: {e}")
        print("Make sure you've installed the package with: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()