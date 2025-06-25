# DDownload Downloader

A lightweight, segmented downloader with a plugin system and real‑time web UI.  
Optimized for low‑resource environments such as Termux, Debian, or WSL2.

---

## Table of Contents
1. [Overview](#overview)  
2. [Features](#features)  
3. [System Requirements](#system-requirements)  
4. [Installation](#installation)  
   * [Debian / Ubuntu / WSL2](#debian--ubuntu--wsl2)  
   * [com.android.virtualization.terminal](#comandroidvirtualizationterminal)  
5. [Configuration](#configuration)  
6. [Usage](#usage)  
7. [Contributing](#contributing)  
8. [License](#license)

---

## Overview
DDownload Downloader provides high‑performance, parallel downloads from **ddownload.com** via its Premium API.  
Its minimalist web interface (no JavaScript frameworks) and modular plugin architecture make it ideal for devices with limited CPU or RAM.

---

## Features
* Direct premium downloads from **ddownload.com**  
* Chunked / parallel downloading with configurable segment size  
* Real‑time web UI with live progress updates  
* Plugin system for adding support for further file hosts  
* User‑level configuration file at `~/.config/ddl_downloader/config.yaml`

---

## System Requirements
| Component | Minimum Version | Notes                           |
|-----------|-----------------|---------------------------------|
| Python    | 3.11            | Core runtime                    |
| OS        | Debian / Termux / WSL2 / com.android.virtualization.terminal | Tested environments |

---

## Installation

### Debian / Ubuntu / WSL2
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
git clone https://github.com/s4mba/ddl_downloader.git
cd ddl_downloader
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If pip is still missing, activate venv and install it manually:
```bash
[...]
source .venv/bin/activate
curl -sS https://bootstrap.pypa.io/get-pip.py | python
pip install -r requirements.txt
```

---

## Configuration
Create or edit the file `~/.config/ddl_downloader/config.yaml`.

```yaml
download_dir: "~/downloads"
segment_size: 8388608       # bytes (8 MiB default)
max_concurrency: 6
listen_host: 0.0.0.0
listen_port: 8000
ui_language: "en"
ddownload_api_key: "your-api-key-here"
```

---

## Usage
```bash
source .venv/bin/activate      # if not already active
python main.py
```
Open the web interface at:  
`http://localhost:8000/static/index.html`

---

## Contributing
Pull requests are welcome. Please ensure any external dependencies remain lightweight and the codebase stays compatible with low‑resource environments. For larger changes, open an issue first to discuss your proposal.

---

## License
This project is licensed under the **MIT License**. See `LICENSE` for details.
