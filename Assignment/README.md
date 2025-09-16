# Network Device Status Dashboard

A small, production‑style project that shows a list of network devices and their live status (“Up/Down”) via a clean web UI and a mock API. It includes a **Flask** backend (with optional real‑time updates) and backend unit tests using **pytest**.

> The interview brief prefers a single‑page **Django** web application for the UI *and* a **mock API** you create (Django or Flask). This repo provides the Flask API and tests; the UI can be Django (recommended) or a simple HTML client for quick verification.

---

## ✨ Features

- `/devices` mock API with `id`, `name`, `ip_address`, `status`.
- No internet dependency; data is mocked and tests are isolated.
- Clean project layout & `pytest` test suite (positive & negative cases).
- Optional Socket.IO broadcast for “real-time” status updates.
- Works on Windows, macOS, and Linux.

---

## 🧱 Project Structure

```
python_web/
├─ README.md                 # ← keep this at the repo root
├─ requirements.txt
├─ pytest.ini
└─ assignment/
   └─ flask_api/
      ├─ __init__.py
      ├─ app.py
      ├─ api/
      │  ├─ __init__.py
      │  └─ routes.py       # /devices endpoint
      ├─ services/
      │  ├─ __init__.py
      │  └─ device_repository.py
      ├─ realtime/          # (optional) Socket.IO server pieces
      │  ├─ __init__.py
      │  └─ socketio_server.py
      └─ tests/
         ├─ __init__.py
         ├─ conftest.py
         └─ test_devices.py
```

---

## 🚀 Quickstart

### 1) Prerequisites
- Python 3.11+ (3.12 supported)
- Git

### 2) Create & activate a virtual environment

**Windows (PowerShell)**
```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Run the API

> Run as a **module** so package imports work everywhere.

**Option A — from the repo root (`python_web/`):**
```bash
python -m assignment.flask_api.app
```

**Option B — from inside `assignment/`:**
```bash
cd assignment
python -m flask_api.app
```

### Endpoint

- `GET /devices`  
  Example response:
  ```json
  [
    {"id":1,"name":"Router1","ip_address":"192.168.1.1","status":"Up"},
    {"id":2,"name":"Switch1","ip_address":"192.168.1.2","status":"Down"},
    {"id":3,"name":"Firewall1","ip_address":"192.168.1.3","status":"Up"}
  ]
  ```

> The data source is mocked (no external calls). You can adjust the quantity and randomness in `services/device_repository.py`.

---

## 🧪 Testing (pytest)

### `pytest.ini` (at repo root)
```ini
[pytest]
pythonpath = assignment
testpaths = assignment/flask_api/tests
```

### Run tests (from repo root)
```bash
pytest -q
```

**Notes**
- Tests import the app with:  
  ```python
  from flask_api.app import create_app
  ```
- Keep imports **consistent** inside the package, e.g.:
  ```python
  from flask_api.api.routes import device_bp
  # or explicit relative
  # from .api.routes import device_bp
  ```

---

## 🔌 Optional: Real-time (Socket.IO)

If enabled, the server emits periodic `device_status` updates. Minimal client to verify:

```html
<!doctype html>
<html>
  <body>
    <ul id="log"></ul>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
      const log = (m)=>document.getElementById('log').insertAdjacentHTML('beforeend', `<li>${m}</li>`);
      const socket = io("http://localhost:5000", { transports: ["websocket"] });
      socket.on("connect", ()=>log("connected"));
      socket.on("device_status", (evt)=>log(JSON.stringify(evt)));
    </script>
  </body>
</html>
```

---

## 🧭 (Optional) Django UI

The brief expects a Django page that lists devices. If you add a Django project (e.g., `django_ui/`), document it here, e.g.:

```bash
cd django_ui
python manage.py migrate
python manage.py runserver 8000
```

Then have the Django front end fetch from the Flask API (`http://127.0.0.1:5000/devices`) and render a simple table (Bootstrap or Material UI).

---

## 🧯 Troubleshooting

- **`ModuleNotFoundError` while running tests**  
  - Ensure `pytest.ini` is at the **repo root** with `pythonpath = assignment`.
  - Add `__init__.py` in `assignment/` and each subfolder.
  - Use module entry points: `python -m assignment.flask_api.app`.

- **Running `conftest.py` directly fails**  
  - `conftest.py` is a pytest plugin; do **not** run it with `python conftest.py`. Use `pytest`.

---

## 📨 Submission Checklist

- [x] Zip the entire project (keep `README.md` at the **repo root**).
- [x] Include clear setup, run, and test instructions (this file).
- [x] Ensure tests pass cleanly and do not require internet access.

---

## 📝 Tech Notes & Conventions

- Prefer absolute imports within the package (`from flask_api...`) or explicit relatives (`from . ...`)—just be consistent.
- Run time config (host/port) can be changed in `app.py` (`app.run(host="127.0.0.1", port=5000, debug=True)`).
- For local development, a `.env` can be introduced later; not required for this mock API.