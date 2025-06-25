# DDownload Downloader

A lightweight segmented downloader with live web UI and plugin support – optimized for low-resource environments like Termux, Proot, or WSL2.

## Features

- Supports ddownload.com (via plugin)
- Segment-based downloading (parallel chunking)
- Minimalistic real-time web interface (HTML+JS, no frontend framework)
- Archive password input
- Plugin system for future hosters
- Configurable via `config.yaml`

## Requirements

- Python 3.11+ (+ pyvenv & pip)
- Linux, Termux, Debian, WSL2 or similar

## Usage

```bash
git clone https://github.com/s4mba-dev/ddl_downloader.git
cd ddl_downloader
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Then open http://localhost:8000/static/ in your browser.
