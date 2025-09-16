# flask_api/realtime/socketio_server.py
from __future__ import annotations

import random
from typing import Dict
from flask import request
from flask_socketio import SocketIO

# threading works everywhere and avoids extra deps
socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")

# Per-client subscriptions: sid -> requested N
_subscribers: Dict[str, int] = {}

def _generate_devices(n: int) -> list[dict]:
    """Create n mock devices with random status."""
    types = ["Router", "Switch", "Firewall", "AccessPoint", "Server"]
    out: list[dict] = []
    for i in range(1, n + 1):
        t = random.choice(types)
        ip = f"192.168.{(i // 255) % 255}.{i % 255 or 1}"
        out.append({
            "id": i,
            "name": f"{t}{i}",
            "ip_address": ip,
            "status": random.choice(["Up", "Down"]),
        })
    return out

def _periodic_broadcast_loop():
    """Every 5s emit a fresh N-sized device list to each subscribed client."""
    while True:
        # Copy to avoid "dict changed size during iteration"
        for sid, n in list(_subscribers.items()):
            payload = _generate_devices(n)
            socketio.emit("device_status", payload, to=sid)
        socketio.sleep(5)  # seconds

def start_event_broadcaster(app, event_service=None):
    """
    Initialize Socket.IO on the app and start background tasks:

    1) If event_service is provided, consume event_service.stream() and emit each evt.
    2) Always run a periodic broadcaster that pushes N devices/5s to subscribed clients.
    """
    socketio.init_app(app)

    # prevent double-starts (Flask dev reloader, multiple imports, etc.)
    if event_service is not None and not app.config.get("EVENT_BG_STARTED"):
        app.config["EVENT_BG_STARTED"] = True

        def _bg():
            with app.app_context():
                for evt in event_service.stream():
                    # Broadcast live events to everyone (frontend handles single/array)
                    socketio.emit("device_status", evt, broadcast=True)

        socketio.start_background_task(_bg)

    if not app.config.get("PERIODIC_BG_STARTED"):
        app.config["PERIODIC_BG_STARTED"] = True
        socketio.start_background_task(_periodic_broadcast_loop)

# ---- Socket.IO events ----

@socketio.on("subscribe_devices")
def subscribe_devices(payload):
    """Client asks to receive N devices every 5s."""
    n = 10
    try:
        if isinstance(payload, dict) and "n" in payload:
            n = int(payload["n"])
    except (TypeError, ValueError):
        n = 10
    n = max(1, min(n, 500))
    _subscribers[request.sid] = n

@socketio.on("disconnect")
def _on_disconnect():
    _subscribers.pop(request.sid, None)

@socketio.on("connect")
def _on_connect():
    # per-client hello (useful for UI badges)
    socketio.emit("device_status", {"type": "info", "message": "connected"}, to=request.sid)
