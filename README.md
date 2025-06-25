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

       sudo apt update
       sudo apt install -y python3.11 python3.11-venv python3-pip curl

2. Then create and activate your virtual environment:

       python3.11 -m venv .venv
       source .venv/bin/activate

3. If `pip` does not work in the venv, bootstrap it manually:

       curl -sS https://bootstrap.pypa.io/get-pip.py | python

Now you're ready to install project requirements.

## Setup

       pip install -r requirements.txt
       python main.py

Then open http://localhost:8000/static/index.html in your browser to use the Web UI.

## Configuration

Create or edit the following file:

       ~/.config/ddl_downloader/config.yaml

Example:

       download_dir: "~/downloads"
       segment_size: 8388608
       max_concurrency: 6
       listen_host: 0.0.0.0
       listen_port: 8000
       ui_language: "en"
       ddownload_api_key: "your-api-key-here"

## License

MIT License