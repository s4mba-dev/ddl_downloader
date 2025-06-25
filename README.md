# DDownload Downloader

A lightweight segmented downloader with plugin system and real-time web UI.  
Supports ddownload.com and is optimized for low-resource environments like Termux, Debian or WSL2.

## Features

- Direct download from ddownload.com via Premium API key
- Chunked/parallel downloading with configurable segment size
- Simple real-time Web UI (no frontend framework)
- Plugin support for future hosts
- Config file in `~/.config/ddl_downloader/config.yaml`

## Requirements

- Python 3.11 or higher
- Recommended environments: Debian, Termux, WSL2, or com.android.virtualization.terminal

### ⚠️ Note for `com.android.virtualization.terminal` users

1. You must install Python + pip manually:

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip curl