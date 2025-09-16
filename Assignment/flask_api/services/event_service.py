from __future__ import annotations

import random
import time
from typing import Dict, Iterable, List

from services.device_repository import DeviceRepository
# assuming your predefined model is here
from models.device import Device  # adjust import if needed


class EventService:
    """
    Produces a stream of device status-change events for realtime demos.
    Works with an immutable Device model by keeping a separate status map.
    """

    def __init__(self, repo: DeviceRepository, total: int = 15):
        self.repo = repo
        self.devices: List[Device] = self.repo.get_all_devices(total)
        # Keep a mutable shadow state for statuses (since Device is frozen/immutable)
        self._status_map: Dict[int, str] = {d.id: d.status for d in self.devices}

    def stream(self, interval_sec: float = .5, seed: int | None = None) -> Iterable[Dict]:
        if seed is not None:
            random.seed(seed)

        while True:
            device: Device = random.choice(self.devices)

            curr = self._status_map[device.id]
            new_status = "Down" if curr == "Up" else "Up"
            self._status_map[device.id] = new_status  # update shadow state only

            yield {
                "type": "device_status_changed",
                "device_id": device.id,
                "name": device.name,
                "ip_address": device.ip_address,
                "status": new_status,
                "timestamp": time.time(),
            }

            time.sleep(interval_sec)
