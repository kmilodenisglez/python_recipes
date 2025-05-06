# Python Recipes 🐍🍴

A collection of practical Python 2 and 3 scripts for automation, image processing, AWS DynamoDB integration, and digital signature (JWS) handling.

![Python Version](https://img.shields.io/badge/python-2.7%20%7C%203.6+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📁 Project Structure

- `python2/`: Scripts for image processing and automation in Python 2.
- `python3/`: Modern examples for Python 3, including AWS integration and filesystem event handling.

Each subfolder contains its own README with details and usage examples.

## Requirements

- Python 2.7+ and/or Python 3.7+
- Specific dependencies in each subfolder (see `requirements.txt` where applicable)

### Python 2 (Legacy)
> Note: Python 2 is deprecated. These scripts are maintained for historical reference only.

| Script | Description | Dependencies |
|--------|-------------|--------------|
| `backup_bigger.py` | Backup files larger than specified size | `os`, `shutil` |
| `compress_quality_images.py` | Optimize images with quality adjustment | `PIL` |
| `delete_unused_images.py` | Cleanup unused image files | `os`, `time` |
| `generate_thumbnails.py` | Batch generate image thumbnails | `PIL` |

### Python 3 (Recommended)

#### File Management 🗂️
| Script | Description | Dependencies |
|--------|-------------|--------------|
| `watchdog_ex.py` | File system monitoring with basic event handling | `watchdog` |
| `watchdog_ex2.py` | Advanced directory monitoring with pattern matching | `watchdog`, `re` |

#### System Utilities 🖥️
| Script | Description | Dependencies |
|--------|-------------|--------------|
| `detect_device_in_windows.py` | Detect connected USB devices on Windows | `winreg`, `time` |

#### Security 🔒
| Script | Description | Dependencies |
|--------|-------------|--------------|
| `JWS/` | JWS signature implementation with x5c support | `cryptography`, `json` |
| - `sign.py` | Create detached JWS signatures (RFC-7797) |  |
| - `verify.py` | Verify JWS signatures with x5c validation |  |
