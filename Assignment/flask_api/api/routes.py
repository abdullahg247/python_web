from __future__ import annotations

from flask import Blueprint, jsonify, request
from services.device_repository import DeviceRepository

device_bp = Blueprint("devices", __name__)

# We keep a module-level repo for simplicity; in larger apps inject via app context/DI.
_repo = DeviceRepository()

@device_bp.get("/devices")
def get_devices():
    n = request.args.get("n", "20")
    seed = request.args.get("seed")
    try:
        n = int(n)
        if n < 1:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Invalid 'n', must be integer >= 1"}), 400

    seed_val = int(seed) if seed and seed.lstrip("-").isdigit() else None
    devices = _repo.get_all_devices(n=n, seed=seed_val)
    return jsonify([d.to_dict() for d in devices]), 200

@device_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200
