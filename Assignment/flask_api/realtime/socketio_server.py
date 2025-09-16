# flask_api/realtime/socketio_server.py
from __future__ import annotations

from flask_socketio import SocketIO

# threading works everywhere and avoids extra deps
socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")

def start_event_broadcaster(app, event_service):
    """
    Initialize Socket.IO on the app and start ONE background task that
    consumes events from EventService.stream(...) and broadcasts them.
    """
    socketio.init_app(app)

    # prevent double-starts (Flask dev reloader, multiple imports, etc.)
    if app.config.get("EVENT_BG_STARTED"):
        return
    app.config["EVENT_BG_STARTED"] = True

    def _bg():
        # ensure we have an app context for logging/config if needed
        with app.app_context():
            for evt in event_service.stream():
                # broadcast on default namespace
                socketio.emit("device_status", evt)

    socketio.start_background_task(_bg)

# Optional: simple connect log/ping
@socketio.on("connect")
def _on_connect():
    socketio.emit("device_status", {"type": "info", "message": "connected"})
