#!/usr/bin/env bash
# install.sh - Cross-platform installation for SysMon

set -e

echo "=== SysMon Installation ==="
echo ""

# Check Python version
echo "Python version: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Install package in development mode
echo ""
echo "Installing SysMon package..."
pip3 install -e .

echo ""
echo "✓ SysMon installed successfully!"

# Make shell script executable
chmod +x sysmon

echo ""
echo "=== How to use SysMon ==="
echo ""
echo "Option 1: Use the launcher script (Recommended)"
echo "  ./sysmon monitor                    (Unix/Linux/Mac)"
echo "  python3 run.py monitor              (All platforms)"
echo ""
echo "Option 2: Use Python module directly"
echo "  python3 -m sysmon.cli monitor"
echo ""
echo "Option 3: Add to PATH for direct 'sysmon' command"
echo "  sudo ln -s $(pwd)/sysmon /usr/local/bin/sysmon"
echo "  # Then use: sysmon monitor"
echo ""
echo "=== Quick Start ==="
echo "  ./sysmon monitor              # Start the dashboard"
echo "  ./sysmon snapshot             # Take a snapshot"
echo "  ./sysmon config show          # View configuration"
echo "  ./sysmon --help               # See all commands"
echo ""