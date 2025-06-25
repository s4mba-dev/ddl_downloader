# DDownload Downloader

A lightweight segmented downloader with real-time web interface and plugin support.  
Designed for low-resource environments such as Termux, Debian, or WSL2.

## Features

- Direct file downloads from ddownload.com using a Premium API key
- Parallel and segmented downloading with adjustable chunk size
- Minimal, real-time web UI (no frontend framework dependencies)
- Plugin architecture for future hoster support
- Configuration via YAML file: `~/.config/ddl_downloader/config.yaml`

## Requirements

- Python 3.11 or higher
- Recommended environments:
  - Debian
  - Termux (Android)
  - WSL2
  - `com.android.virtualization.terminal` (Pixel 8 and similar)

### Special Instructions for `com.android.virtualization.terminal`

1. Install Python and pip manually:

   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv python3-pip curl
   ```

2. Create and activate a virtual environment:

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. If `pip` does not work inside the virtual environment, bootstrap it manually:

   ```bash
   curl -sS https://bootstrap.pypa.io/get-pip.py | python
   ```

Once the virtual environment is ready, you can install the required dependencies.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Then open the following URL in your browser to use the web interface:  
[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)

## Configuration

Create or edit the file at:

```bash
~/.config/ddl_downloader/config.yaml
```

Example configuration:

```yaml
download_dir: "~/downloads"
segment_size: 8388608
max_concurrency: 6
listen_host: 0.0.0.0
listen_port: 8000
ui_language: "en"
ddownload_api_key: "your-api-key-here"
```

## License

This project is licensed under the MIT License.