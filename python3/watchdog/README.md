# Watchdog File System Monitor

A Python utility for monitoring file system events with pattern matching capabilities.

## Overview

This tool uses the Watchdog library to monitor file system events (create, modify, delete, move) in specified directories. It supports:

- Pattern matching for specific file types
- Ignoring specific patterns
- Recursive directory monitoring
- Detailed logging with timestamps
- Command-line configuration

## Requirements

- Python 3.6+
- Watchdog library

## Installation

### Using a Virtual Environment (Recommended)

1. **Create a virtual environment**:

   **Windows**:
   ```bash
   # Navigate to the project directory
   cd python_recipes

   # Create a virtual environment
   python -m venv .venv

   # Activate the virtual environment
   .venv\Scripts\activate
   ```

   **macOS/Linux**:
   ```bash
   # Navigate to the project directory
   cd python_recipes

   # Create a virtual environment
   python3 -m venv .venv

   # Activate the virtual environment
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   # Install watchdog
   pip install watchdog
   ```

   Or using the requirements file:
   ```bash
   pip install -r python3/watchdog/requirements.txt
   ```

## Usage

### Basic Usage

Monitor the current directory for Python files:
```bash
python python3/watchdog/watchdog_2.py
```

### Command-line Options

```
usage: watchdog_2.py [-h] [-p PATTERNS [PATTERNS ...]] [-i IGNORE_PATTERNS [IGNORE_PATTERNS ...]] [-d] [-r] [-v] [-l LOG_FILE] [path]

Monitor file system events with pattern matching

positional arguments:
  path                  Directory path to monitor (default: current directory)

optional arguments:
  -h, --help            show this help message and exit
  -p PATTERNS [PATTERNS ...], --patterns PATTERNS [PATTERNS ...]
                        File patterns to watch (default: *.py *.pyc)
  -i IGNORE_PATTERNS [IGNORE_PATTERNS ...], --ignore-patterns IGNORE_PATTERNS [IGNORE_PATTERNS ...]
                        File patterns to ignore (default: version.py)
  -d, --ignore-directories
                        Ignore directory events
  -r, --recursive       Monitor directories recursively
  -v, --verbose         Enable verbose logging (DEBUG level)
  -l LOG_FILE, --log-file LOG_FILE
                        Log to file instead of console
```

### Examples

**Monitor a specific directory**:
```bash
python python3/watchdog/watchdog_2.py /path/to/monitor
```

**Monitor for specific file types**:
```bash
python python3/watchdog/watchdog_2.py -p "*.txt" "*.md" "*.json"
```

**Ignore certain files**:
```bash
python python3/watchdog/watchdog_2.py -i "temp*" "*.tmp" "*.bak"
```

**Enable verbose logging to a file**:
```bash
python python3/watchdog/watchdog_2.py -v -l watchdog.log
```

**Monitor without recursion** (only the top directory):
```bash
python python3/watchdog/watchdog_2.py --recursive False
```

## Testing the Monitor

1. Start the monitor with your desired options
2. Open another terminal or file explorer
3. Create, modify, or delete files in the monitored directory
4. Observe the events being logged
5. Press `Ctrl+C` to stop monitoring

## Deactivating the Virtual Environment

When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Tips

- For directories with spaces, use quotes: `python python3/watchdog_2.py "C:\My Folder"`
- On Windows, you can use paths like `C:\Users\name\Documents`
- The script logs events with timestamps and additional information like file sizes
- For continuous monitoring in production, consider using a service manager like systemd (Linux) or a Windows service