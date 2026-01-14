#!/usr/bin/env bash
# install.sh - Cross-platform installation for SysMon

set -e

echo "=== SysMon Installation ==="
echo ""

# Detect Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo "Error: Python not found!"
    exit 1
fi

# Check Python version
echo "Python version: $($PYTHON_CMD --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
$PIP_CMD install -r requirements.txt

# Install package in development mode
echo ""
echo "Installing SysMon package..."
$PIP_CMD install -e .

echo ""
echo "✓ SysMon installed successfully!"

# Make shell script executable
if [ -f "sysmon" ]; then
    chmod +x sysmon
    echo "✓ Made launcher script executable"
fi

echo ""
echo "=== How to use SysMon ==="
echo ""
echo "Option 1: Use the launcher script (Recommended)"
echo "  ./sysmon monitor                    (Unix/Linux/Mac)"
echo "  $PYTHON_CMD run.py monitor          (All platforms)"
echo ""
echo "Option 2: Use Python module directly"
echo "  $PYTHON_CMD -m sysmon.cli monitor"
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