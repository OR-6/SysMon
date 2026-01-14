# SysMon 📊

A beautiful, lightweight terminal-based system monitoring tool written in Python.

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Real-time Monitoring**: Live dashboard with auto-refresh
- **Rich Terminal UI**: Beautiful colors, tables, and progress bars
- **Multiple Storage Backends**: JSON or SQLite for data persistence
- **Historical Data**: View and export past system snapshots
- **Flexible Configuration**: YAML-based config with sensible defaults
- **Process Monitoring**: Track top processes by CPU usage
- **Per-CPU Metrics**: Optional per-core CPU usage display
- **JSON Export**: Machine-readable output for scripting
- **Rotating Logs**: Automatic log management

## Quick Start

## Installation

### Windows
```powershell
# Clone the repository
git clone https://github.com/OR-6/sysmon.git
cd sysmon

# Run installation script
.\install.ps1

# Optional: Add to PATH
.\install.ps1 -AddToPath
```

### Linux / macOS
```bash
# Clone the repository
git clone https://github.com/OR-6/sysmon.git
cd sysmon

# Run installation script
bash install.sh

# Optional: Add to system PATH
sudo ln -s $(pwd)/sysmon /usr/local/bin/sysmon
```

### Using pip (All platforms)
```bash
pip install sysmon
```

## Usage

### Windows
```powershell
# Using batch file
.\sysmon.bat monitor

# Using Python
python run.py monitor
```

### Linux / macOS
```bash
# Using shell script
./sysmon monitor

# Using Python
python3 run.py monitor
```

### All Platforms
```bash
# Using Python module
python -m sysmon.cli monitor
```

### Basic Usage
```bash
# Start the interactive dashboard
sysmon monitor

# Take a single snapshot
sysmon snapshot

# View configuration
sysmon config show

# Get JSON output (great for scripts)
sysmon monitor --json
```

## Commands

### Monitor

Start the live monitoring dashboard:
```bash
# Default settings
sysmon monitor

# Custom refresh interval (seconds)
sysmon monitor -i 5

# Show per-CPU core usage
sysmon monitor --per-cpu

# Hide process list
sysmon monitor --no-processes
```

### History

View stored snapshots (requires storage enabled):
```bash
# Show last 10 snapshots
sysmon history

# Show last 20 snapshots
sysmon history -n 20

# Output as JSON
sysmon history --json
```

### Configuration

Manage settings:
```bash
# Show current config
sysmon config show

# Show config file location
sysmon config path

# Change a setting
sysmon config set display.refresh_interval 5
sysmon config set storage.enabled true
sysmon config set storage.backend sqlite

# Reset to defaults
sysmon config reset
```

### Data Management
```bash
# Export stored data
sysmon export snapshots.json

# Clear all stored data
sysmon clear
```

## Configuration

Configuration is stored in `~/.config/sysmon/config.yaml`. Here's an example:
```yaml
display:
  refresh_interval: 2
  show_per_cpu: false
  show_processes: true
  process_count: 5
  progress_bar_width: 30

storage:
  enabled: false
  backend: json  # or 'sqlite'
  path: ~/.local/share/sysmon/data
  max_records: 1000

logging:
  enabled: true
  level: INFO
  path: ~/.local/share/sysmon/logs
  max_size_mb: 10
  backup_count: 3
```

## Requirements

- Python 3.8+
- psutil
- click
- rich
- pyyaml
- pydantic

## Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/OR-6/sysmon.git
cd sysmon

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest tests/
```

### Code Formatting
```bash
# Format code
black src/

# Check types
mypy src/
```

## Project Structure
```
sysmon/
├── src/sysmon/
│   ├── __init__.py      # Package initialization
│   ├── cli.py           # Command-line interface
│   ├── core.py          # System monitoring logic
│   ├── display.py       # Rich terminal display
│   ├── storage.py       # Data persistence
│   ├── config.py        # Configuration management
│   ├── models.py        # Data models
│   └── utils.py         # Utility functions
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```

## Why SysMon?

- **Lightweight**: Minimal dependencies, low resource usage
- **Flexible**: Multiple storage backends, configurable display
- **Developer-friendly**: Clean code, type hints, good documentation
- **Terminal-native**: No browser required, works over SSH
- **Extensible**: Easy to add new metrics or storage backends

## Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- Code follows PEP 8 style guide
- All tests pass
- New features include tests
- Documentation is updated

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [psutil](https://github.com/giampaolo/psutil) for system metrics
- UI powered by [Rich](https://github.com/Textualize/rich)
- CLI framework: [Click](https://click.palletsprojects.com/)

## Roadmap

- [ ] Alert thresholds with notifications
- [ ] Custom dashboard layouts
- [ ] Network interface selection
- [ ] GPU monitoring support
- [ ] Docker container stats
- [ ] Web UI option
- [ ] Prometheus exporter

## Support

- 🐛 [Report bugs](https://github.com/OR-6/sysmon/issues)
- 💡 [Request features](https://github.com/OR-6/sysmon/issues)
- 📖 [Documentation](https://github.com/OR-6/sysmon#readme)

---

Made with ❤️ by developers, for developers