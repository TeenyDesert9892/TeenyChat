# TeenyChat

![License: GPL v3](https://img.shields.io/badge/license-GPLv3-blue.svg)
![Python](https://img.shields.io/badge/python-3.14+-blue.svg)

A lightweight, local-network chat application built with Flet that lets people on the same LAN join a centralized web chat with basic moderation features and a clean UI.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Development](#development)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Authors](#authors)

---

## Features

- Light/dark mode auto toggle ✅
- Centralized local web chat (LAN) 💬
- User moderation (ban, admin promotion) 🔒
- Simple local persistence (SQLite) 🗄️
- File upload support for images 📎

---

## Tech Stack

- Python (declared in `pyproject.toml`) — project currently lists **Python 3.14**
- Flet (UI framework) — app uses Flet to provide a browser-accessible UI
- SQLite for lightweight, local storage
- Simple, dependency-light architecture for LAN usage

---

## Quick Start

Prerequisites

- Python 3.14 (or a compatible Python 3.x runtime)
- Git
- (Optional) Poetry if you prefer using Poetry for dependency management

Clone the repository

```bash
git clone https://github.com/TeenyDesert9892/TeenyChat.git
cd TeenyChat
```

Create and activate a virtual environment (recommended)

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies

- Using the provided requirements file (note: file in repo is `requeriments.txt` — consider renaming to `requirements.txt`):

```bash
pip install -r requeriments.txt
```

- Or using Poetry (if you use Poetry):

```bash
poetry install
```

Run the application

- Start with Flet (recommended):

```bash
flet run -w
```

- Or run directly with Python:

```bash
python -m src.main
```

Open the app in your browser using your machine IP and configured port (default: 9892):

```
http://<your_local_ip>:9892
```

Tip: find your local IP on Windows with `ipconfig` or on macOS/Linux with `ifconfig` / `hostname -I`.

---

## Configuration

- The app sets environment variables at start (`FLET_SERVER_PORT`, `FLET_ASSETS_DIR`, `FLET_UPLOAD_DIR`, etc.). Edit `src/main.py` to change defaults or set environment variables in your environment before starting the server.
- Database file is created/used at `src/assets/database.db` by default.

Notes / Recommendations

- `pyproject.toml` currently references two different Flet versions (check the `tool.poetry` and `project.dependencies` sections). Consider syncing them to a single version.
- Rename `requeriments.txt` → `requirements.txt` to follow conventions and avoid confusion.

---

## Development

Run tests (if any):

```bash
pytest -q
```

Code style and checks (suggested):

```bash
pip install black flake8 mypy
black .
flake8 src
mypy src
```

Packaging / building Flet app (see Flet docs):

```bash
# To compile the app for distribution (Flet compile settings exist in pyproject.toml)
# follow Flet's packaging guide for exact commands and targets
```

---

## Project Structure (high level)

- `src/` — application source code
  - `main.py` — application entrypoint
  - `ui/` — UI components
  - `core/` — core utilities / business logic
  - `database/` — sqlite helper
  - `models/` — data models
  - `routes/`, `services/` — server logic and services
  - `assets/`, `upload/` — static files and uploaded images
- `storage/` — runtime storage folders (`data/`, `temp/`)
- `upgraded_chat/` — an experimental or upgraded version of the app (contains a more feature-complete copy)
- `tests/` — test suite (if present)

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Implement your changes and add tests where applicable
4. Run `black` and `flake8`, and ensure tests pass
5. Submit a pull request describing your change

If you plan larger changes, open an issue first to discuss design and compatibility.

---

## Troubleshooting

- Port already in use: change `FLET_SERVER_PORT` env var or stop the conflicting process
- Database locked or permission errors: ensure `src/assets/` exists and is writable
- UI not accessible from another device: make sure the host machine firewall allows inbound connections and use the correct local IP

---

## License

This project is distributed under the GNU General Public License v3.0 (GPL-3.0). See the `LICENSE` file for details.

---

## Authors

- TeenyDesert9892 — https://github.com/TeenyDesert9892

---

If you want, I can also:
- Fix the `requeriments.txt` → `requirements.txt` filename
- Unify the Flet version between `pyproject.toml` entries
- Add a `CONTRIBUTING.md` and PR template

Happy to make any of those changes — tell me which you'd like me to do next. ✨
