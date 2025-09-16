from __future__ import annotations

import random
from typing import List
from models.device import Device

class DeviceRepository:
    """Provides access to device data (mock, randomized)."""

    DEVICE_TYPES = ["Router", "Switch", "Firewall", "AccessPoint", "Server"]

    def get_all_devices(self, n: int = 15, seed: int | None = None) -> List[Device]:
        if seed is not None:
            random.seed(seed)

        devices: List[Device] = []
        for i in range(1, n + 1):
            device_type = random.choice(self.DEVICE_TYPES)
            ip_address = f"192.168.{(i // 255) % 256}.{i % 255 or 1}"
            devices.append(
                Device(
                    id=i,
                    name=f"{device_type}{i}",
                    ip_address=ip_address,
                    status=random.choice(["Up", "Down"]),
                )
            )
        return devices
