# flask_api/app.py
from __future__ import annotations
from pathlib import Path
from flask import Flask, request, render_template
from flask_cors import CORS

from api.routes import device_bp
from services.device_repository import DeviceRepository
from services.event_service import EventService
from realtime.socketio_server import socketio, start_event_broadcaster


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # Core dependencies
    repo = DeviceRepository()
    events = EventService(repo)

    @app.route("/dashboard")
    def dashboard():
        return render_template("index.html")

    @app.route("/realtime-dashboard")
    def realtime_page():
        return render_template("realtime.html")

    @app.get("/")
    def index():
        allowed_methods = {"GET", "POST", "PUT", "PATCH", "DELETE"}
        base_url = request.host_url.rstrip("/")
        routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint == "static":
                continue
            methods = sorted((rule.methods or set()) & allowed_methods)
            if not methods:
                continue
            routes.append({
                "endpoint": f"{base_url}{rule.rule}",
                "methods": [m.lower() for m in methods],
            })
        return {"message": "Welcome to the Device API. Here are the available routes:", "routes": routes}, 200
    
    @app.route("/health")
    def health_check():
        return {"status": "ok"}, 200

   

    # HTTP routes
    app.register_blueprint(device_bp)

    # Realtime broadcaster (this kicks off the background generator)
    start_event_broadcaster(app)

    return app

app = create_app()

if __name__ == "__main__":
    # IMPORTANT: disable the dev reloader to avoid double background tasks
    socketio.run(app, host="127.0.0.1", port=8000, debug=True, use_reloader=False)
