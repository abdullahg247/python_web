import pytest
from services.device_repository import DeviceRepository

def test_get_all_devices_returns_expected_count():
    repo = DeviceRepository()
    devices = repo.get_all_devices(n=5, seed=42)
    assert len(devices) == 5
    assert all(d.id for d in devices)
    assert all(d.status in {"Up", "Down"} for d in devices)

def test_get_all_devices_is_deterministic_with_seed():
    repo = DeviceRepository()
    d1 = repo.get_all_devices(n=3, seed=123)
    d2 = repo.get_all_devices(n=3, seed=123)
    assert [dev.to_dict() for dev in d1] == [dev.to_dict() for dev in d2]

def test_get_all_devices_invalid_seed_does_not_crash():
    repo = DeviceRepository()
    devices = repo.get_all_devices(n=2)  # no seed
    assert len(devices) == 2
