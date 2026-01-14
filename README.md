# SysMon 📊

> A beautiful, lightweight system monitoring tool for your terminal

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

---

## 📸 Screenshots

### Main Dashboard
![SysMon Dashboard](screenshots/dashboard.png)

### Snapshot View
![Snapshot View](screenshots/snapshot.png)

### History View
![History View](screenshots/history.png)

---

## ✨ Features

- 🎨 **Beautiful Terminal UI** - Rich colors, progress bars, and organized layouts
- ⚡ **Real-time Monitoring** - Live dashboard with auto-refresh
- 💾 **Data Persistence** - Store snapshots in JSON or SQLite
- 📊 **Historical Data** - View and analyze past system metrics
- 🎯 **Top Processes** - Track resource-hungry applications
- 🔧 **Highly Configurable** - YAML-based configuration with sensible defaults
- 📦 **Multiple Export Formats** - JSON output for scripting and automation
- 🪵 **Smart Logging** - Rotating logs with configurable levels
- 🖥️ **Cross-Platform** - Works on Windows, macOS, and Linux
- 🚀 **Lightweight** - Minimal resource usage and dependencies

---

## 🎬 Demo

![Demo](screenshots/demo.gif)

---

## 📋 Table of Contents

- [Installation](#-installation)
  - [Windows](#windows)
  - [Linux / macOS](#linux--macos)
  - [From PyPI](#from-pypi-coming-soon)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
  - [Monitor Dashboard](#monitor-dashboard)
  - [Take Snapshots](#take-snapshots)
  - [View History](#view-history)
  - [Configuration](#configuration)
  - [Export Data](#export-data)
- [Configuration](#️-configuration)
- [Commands Reference](#-commands-reference)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)

---

## 🚀 Installation

### Windows
```powershell
# Clone the repository
git clone https://github.com/OR-6/sysmon.git
cd sysmon

# Run the installation script
.\install.ps1

# Optional: Add to PATH for 'sysmon' command
.\install.ps1 -AddToPath
```

### Linux / macOS
```bash
# Clone the repository
git clone https://github.com/OR-6/sysmon.git
cd sysmon

# Run the installation script
bash install.sh

# Optional: Add to system PATH
sudo ln -s $(pwd)/sysmon /usr/local/bin/sysmon
```

### From PyPI
```bash
pip install sysmonitor
```

### Requirements

- Python 3.8 or higher
- pip (Python package manager)
- Works on Windows, macOS, and Linux

---

## 🎯 Quick Start
```bash
# Windows
python run.py monitor

# Linux/Mac
./sysmon monitor

# All platforms
python -m sysmon.cli monitor
```

That's it! Press `Ctrl+C` to exit.

---

## 📖 Usage

### Monitor Dashboard

Start the live monitoring dashboard:
```bash
# Default settings (2 second refresh)
sysmon monitor

# Custom refresh interval
sysmon monitor -i 5

# Show per-CPU core usage
sysmon monitor --per-cpu

# Hide process list for cleaner view
sysmon monitor --no-processes
```

**Controls:**
- `Ctrl+C` - Exit the dashboard

### Take Snapshots

Capture a single system snapshot:
```bash
# Simple snapshot
sysmon snapshot

# JSON output (great for scripts)
sysmon monitor --json > snapshot.json
```

### View History

View stored historical data (requires storage to be enabled):
```bash
# Show last 10 snapshots
sysmon history

# Show last 50 snapshots
sysmon history -n 50

# Export as JSON
sysmon history --json > history.json
```

### Configuration

Manage your settings:
```bash
# View current configuration
sysmon config show

# Show config file location
sysmon config path

# Change settings
sysmon config set display.refresh_interval 5
sysmon config set storage.enabled true
sysmon config set storage.backend sqlite

# Reset to defaults
sysmon config reset
```

### Export Data

Export your stored snapshots:
```bash
# Export to JSON file
sysmon export snapshots.json

# Export to specific location
sysmon export ~/backups/system-data-$(date +%Y%m%d).json
```

### Clear Data

Remove all stored snapshots:
```bash
sysmon clear
```

---

## ⚙️ Configuration

Configuration is stored in `~/.config/sysmon/config.yaml`

### Default Configuration
```yaml
display:
  refresh_interval: 2        # Refresh every N seconds
  show_per_cpu: false        # Show individual CPU cores
  show_processes: true       # Display top processes
  process_count: 5           # Number of processes to show
  progress_bar_width: 30     # Width of progress bars

storage:
  enabled: false             # Enable data persistence
  backend: json              # 'json' or 'sqlite'
  path: ~/.local/share/sysmon/data
  max_records: 1000          # Keep last N snapshots

logging:
  enabled: true              # Enable logging
  level: INFO                # DEBUG, INFO, WARNING, ERROR
  path: ~/.local/share/sysmon/logs
  max_size_mb: 10           # Max log file size
  backup_count: 3           # Number of backup files
```

### Configuration Examples

**Enable data storage:**
```bash
sysmon config set storage.enabled true
sysmon config set storage.backend sqlite
```

**Show more processes:**
```bash
sysmon config set display.process_count 10
```

**Change refresh rate:**
```bash
sysmon config set display.refresh_interval 1
```

**Enable per-CPU monitoring:**
```bash
sysmon config set display.show_per_cpu true
```

---

## 📚 Commands Reference

### Global Options
```bash
sysmon --version              # Show version
sysmon --help                 # Show help
```

### Monitor Command
```bash
sysmon monitor [OPTIONS]

Options:
  -i, --interval INTEGER    Refresh interval in seconds
  --per-cpu                 Show per-CPU core usage
  --no-processes            Hide process list
  --json                    Output as JSON (single snapshot)
  --help                    Show help
```

### Snapshot Command
```bash
sysmon snapshot              # Take a single snapshot
```

### History Command
```bash
sysmon history [OPTIONS]

Options:
  -n, --limit INTEGER       Number of snapshots to show (default: 10)
  --json                    Output as JSON
  --help                    Show help
```

### Config Commands
```bash
sysmon config show           # Display current configuration
sysmon config path           # Show config file location
sysmon config set KEY VALUE  # Set a configuration value
sysmon config reset          # Reset to defaults
```

### Export Command
```bash
sysmon export OUTPUT_PATH    # Export stored data
```

### Clear Command
```bash
sysmon clear                 # Clear all stored data
```

---

## 🛠️ Development

### Setup Development Environment
```bash
# Clone the repository
git clone https://github.com/OR-6/sysmon.git
cd sysmon

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sysmon tests/

# Run specific test file
pytest tests/test_core.py
```

### Code Quality
```bash
# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

### Building Distribution
```bash
# Build package
python -m build

# Install locally
pip install dist/sysmon-0.1.0-py3-none-any.whl
```

---

## 📁 Project Structure
```
sysmon/
├── src/
│   └── sysmon/
│       ├── __init__.py       # Package initialization
│       ├── cli.py            # Command-line interface (Click)
│       ├── core.py           # System monitoring logic
│       ├── display.py        # Rich terminal display
│       ├── storage.py        # Data persistence (JSON/SQLite)
│       ├── config.py         # Configuration management
│       ├── models.py         # Pydantic data models
│       └── utils.py          # Helper functions
├── tests/
│   ├── __init__.py
│   └── test_core.py          # Unit tests
├── examples/
│   └── config.example.yaml   # Example configuration
├── screenshots/              # Screenshots for README
├── run.py                    # Cross-platform launcher
├── sysmon                    # Unix/Linux/Mac launcher
├── sysmon.bat                # Windows batch launcher
├── install.sh                # Unix installation script
├── install.ps1               # Windows installation script
├── pyproject.toml            # Project metadata and dependencies
├── setup.py                  # Setup configuration
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── LICENSE                   # MIT License
└── .gitignore               # Git ignore rules
```

---

## ❓ FAQ

### How do I enable data storage?
```bash
sysmon config set storage.enabled true
```

### Can I export data to CSV?

Currently, export is JSON only. You can convert JSON to CSV using tools like `jq` or Python:
```bash
# Using jq (if installed)
sysmon history --json | jq -r '.[] | [.timestamp, .cpu.percent, .memory.percent] | @csv'
```

### Why is my CPU showing 0%?

Make sure you're not running SysMon on a very fast refresh interval. CPU measurement needs at least 1 second to be accurate.

### How do I uninstall?
```bash
pip uninstall sysmonitor
```

### Does this work over SSH?

Yes! SysMon works perfectly over SSH connections as it's a pure terminal application.

### Can I monitor remote systems?

Not directly. SysMon monitors the local system where it's running. For remote monitoring, SSH into the remote system and run SysMon there.

### What's the difference between JSON and SQLite storage?

- **JSON**: Simple, human-readable, easy to backup
- **SQLite**: More efficient for large datasets, faster queries

### How much disk space does storage use?

Each snapshot is approximately 1-2 KB. With default settings (1000 max records), you'll use about 1-2 MB.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/OR-6/sysmon/issues)
2. If not, create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Your system info (OS, Python version)

### Suggesting Features

Open an issue with the `enhancement` label describing:
- The feature you'd like to see
- Why it would be useful
- How it might work

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass (`pytest`)
6. Format your code (`black src/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Code Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings for public APIs
- Include tests for new features
- Update documentation as needed

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[psutil](https://github.com/giampaolo/psutil)** - Cross-platform system and process utilities
- **[Rich](https://github.com/Textualize/rich)** - Beautiful terminal formatting
- **[Click](https://click.palletsprojects.com/)** - Elegant CLI framework
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation using Python type annotations

### Inspiration

Inspired by tools like:
- [htop](https://htop.dev/) - Interactive process viewer
- [btop](https://github.com/aristocratos/btop) - Resource monitor
- [glances](https://nicolargo.github.io/glances/) - Cross-platform monitoring tool

---

## 🗺️ Roadmap

### Version 0.2.0
- [ ] Alert system with threshold notifications
- [ ] Custom dashboard layouts
- [ ] Network interface selection
- [ ] Disk I/O monitoring

### Version 0.3.0
- [ ] GPU monitoring support (NVIDIA, AMD)
- [ ] Docker container stats
- [ ] Temperature sensors
- [ ] Battery status (laptops)

### Version 1.0.0
- [ ] Web UI option
- [ ] Prometheus exporter
- [ ] Plugin system
- [ ] Remote monitoring capability

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/OR-6/sysmon?style=social)
![GitHub forks](https://img.shields.io/github/forks/OR-6/sysmon?style=social)
![GitHub issues](https://img.shields.io/github/issues/OR-6/sysmon)
![GitHub pull requests](https://img.shields.io/github/issues-pr/OR-6/sysmon)

---

## 📧 Contact

- **Author**: Numair Khan
- **Email**: ornor6@gmail.com
- **GitHub**: [@OR-6](https://github.com/OR-6)
- **Issues**: [GitHub Issues](https://github.com/OR-6/sysmon/issues)

---

<p align="center">
  <strong>Made with ❤️ by developers, for developers</strong>
</p>

<p align="center">
  <sub>If you find this tool useful, consider giving it a ⭐ on GitHub!</sub>
</p>