from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Device:
    id: int
    name: str
    ip_address: str
    status: str  # "Up" | "Down"

    def to_dict(self) -> dict:
        return asdict(self)
