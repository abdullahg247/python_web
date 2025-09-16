# Network Device Status Dashboard (Flask)

A compact **Flask** project that exposes a mock `/devices` API and a simple dashboard. It includes unit tests with **pytest** and optional **Socket.IO** real‑time updates. Everything runs locally with **no internet dependency**.

---

## ✨ Features

- **Mock API**: `GET /devices` returns a list of devices: `{ id, name, ip_address, status }`.
- **API Index**: `GET /` advertises available routes in JSON.
- **Health Check**: `GET /health` returns quick service status.
- **(Optional) Real‑time**: Socket.IO broadcasts sample `device_status` events.
- **Clean tests**: Positive & negative paths with `pytest`.
- **Windows/macOS/Linux** friendly.

---

## 🧱 Project Structure (expected)

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
      │  └─ routes.py         # /, /devices, /health (+ optional dashboards)
      ├─ services/
      │  ├─ __init__.py
      │  └─ device_repository.py
      ├─ realtime/            # (optional) Socket.IO server
      │  ├─ __init__.py
      │  └─ socketio_server.py
      └─ tests/
         ├─ __init__.py
         ├─ conftest.py
         ├─ test_devices.py
         └─ test_index.py
```

> If any folder is missing `__init__.py`, add an empty one so Python treats it as a package.

---

## 🚀 Setup

### 1) Prerequisites
- Python **3.11+** (3.12 supported)
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

> Run as a **module** so package imports remain correct.

**Option A — from the repo root (`python_web/`):**
```bash
python -m assignment.flask_api.app
```

**Option B — from inside `assignment/`:**
```bash
cd assignment
python -m flask_api.app
```

- Default host/port (unless you changed it in `app.py`): `http://127.0.0.1:5000`

### Quick sanity checks (replace BASE if you changed host/port)
```bash
BASE=http://127.0.0.1:5000
curl -s $BASE/ | jq .
curl -s $BASE/health | jq .
curl -s $BASE/devices | jq .
```

---

## 🔚 Endpoints

### `GET /` — API Index

Returns a JSON index of available routes.

**Example response (recommended: relative endpoints)**
### Context for `GET /` — How this index is built and used

**Purpose.** The API home (`/`) is a **self‑describing index** so you can quickly discover the service without external docs and verify routing is healthy.

**Base URL.** The index shows **relative paths** (e.g., `/devices`) so it works on any host/port. Treat your runtime base as, for example, `http://127.0.0.1:5000`, then resolve each relative path against it.

**Shape.**
```json
{
  "message": "Welcome to the Device API. Here are the available routes:",
  "routes": [
    { "endpoint": "/",                   "methods": ["GET"] },
    { "endpoint": "/devices",            "methods": ["GET"] },
    { "endpoint": "/health",             "methods": ["GET"] },
    { "endpoint": "/dashboard",          "methods": ["GET"] },
    { "endpoint": "/realtime-dashboard", "methods": ["GET"] }
  ]
}
```

**How it’s generated.** The index iterates over Flask’s `url_map`, filters out non‑public entries (like `static`), and emits only HTTP verbs relevant to clients (typically `GET`). If your implementation currently emits **absolute URLs**, either switch to `str(rule)` (relative) or normalize endpoints in tests.

**Acceptance criteria (tests).**
- `GET /` returns **200** with JSON containing `message` and a `routes` array.
- Each `routes[i]` has:  
  - `endpoint`: **relative path** starting with `/`  
  - `methods`: array of HTTP verbs and must include `"GET"`
- The index includes at least: `/`, `/devices`, `/health` (and if enabled: `/dashboard`, `/realtime-dashboard`).

**Quick checks.**
```bash
BASE=http://127.0.0.1:5000
curl -s $BASE/ | jq .
curl -s $BASE/health | jq .
curl -s $BASE/devices | jq .
```

**Optional (absolute URLs).** If you prefer absolute URLs in the index, build them with `url_for(..., _external=True)` and set `PREFERRED_URL_SCHEME` / `SERVER_NAME` in Flask config. Update tests to normalize with `urllib.parse.urlparse`.

```json
{
  "message": "Welcome to the Device API. Here are the available routes:",
  "routes": [
    {"endpoint": "/",                    "methods": ["GET"]},
    {"endpoint": "/devices",             "methods": ["GET"]},
    {"endpoint": "/health",              "methods": ["GET"]},
    {"endpoint": "/dashboard",           "methods": ["GET"]},
    {"endpoint": "/realtime-dashboard",  "methods": ["GET"]}
  ]
}
```

> Tip: Prefer **relative** paths in the index so it stays correct across environments/ports. If you return absolute URLs, normalize them in tests.

### `GET /devices` — Mock device list
Returns JSON with fields: `id`, `name`, `ip_address`, `status` (either `"Up"` or `"Down"`). The default implementation may randomize devices via `DeviceRepository`; tests fake/patch it to be deterministic.

### `GET /health` — Health check
Returns a simple JSON status like `{"status": "ok"}`.

### `GET /dashboard` — Static/simple UI (optional)
A simple HTML page that fetches `/devices` and renders a table.

### `GET /realtime-dashboard` — Live updates (optional)
If Socket.IO is enabled, this page subscribes to `device_status` events and updates badges without refresh.

---

## 🔌 (Optional) Real‑time Socket.IO

Minimal client snippet to verify events:

```html
<!doctype html>
<html>
  <body>
    <ul id="log"></ul>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
      const log = (m)=>document.getElementById('log').insertAdjacentHTML('beforeend', `<li>${m}</li>`);
      const socket = io("http://127.0.0.1:5000", { transports: ["websocket"] });
      socket.on("connect", ()=>log("connected"));
      socket.on("device_status", (evt)=>log(JSON.stringify(evt)));
    </script>
  </body>
</html>
```

---

## 🧪 Testing (pytest)

### `pytest.ini` (repo root)
```ini
[pytest]
pythonpath = assignment
testpaths = assignment/flask_api/tests
```

### Run tests (from repo root)
```bash
pytest -q
```

**Test notes**

- Tests import the app with:
  ```python
  from flask_api.app import create_app
  ```
- Keep imports consistent inside the package, e.g.:
  ```python
  from flask_api.api.routes import device_bp
  # or explicit relative imports:
  # from .api.routes import device_bp
  ```
- Example assertions in `test_index.py` normalize endpoints if your index returns absolute URLs.

### Coverage (optional)
```bash
pip install pytest-cov
pytest --cov=assignment/flask_api --cov-report=term-missing
```

---

## 🧯 Troubleshooting

- **`ModuleNotFoundError` while running tests**
  - Ensure `pytest.ini` is at the **repo root** with `pythonpath = assignment`.
  - All package folders have `__init__.py`.
  - Run the app as a module: `python -m assignment.flask_api.app`.

- **Running `conftest.py` directly fails**
  - `conftest.py` is a pytest plugin; don’t run it with `python conftest.py`. Use `pytest`.

- **API index shows absolute URLs but tests expect relative**
  - Either update the index to emit relative paths **or** normalize endpoints in tests (see `test_index.py`).

---

## 📝 Design Notes

- **App factory** (`create_app`) for isolated testing.
- **Repository layer** for data access; easily faked in tests.
- **Optional service layer** if logic grows (keeps routes thin).
- **JSON‑only API** for simplicity; add global error handlers for consistent error shapes.
- **Consistent imports** (absolute or explicit relative) to avoid path issues.

---

## 📦 Submission Checklist

- [x] Keep `README.md` at the **repo root**.
- [x] Include `requirements.txt` and `pytest.ini` at the root.
- [x] Ensure tests run cleanly offline: `pytest -q`.
- [x] Zip the entire project for hand‑off.
