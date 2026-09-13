from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api import app, joy_state

client = TestClient(app)

def test_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Location Changer" in response.text

def test_get_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "intent" in data
    assert "lat" in data
    assert "lng" in data

@patch("backend.device_manager.DeviceManager.connect")
def test_connect(mock_connect):
    response = client.post("/api/connect")
    assert response.status_code == 200
    assert response.json() == {"status": "success"}
    mock_connect.assert_called_once()

@patch("backend.device_manager.DeviceManager.disconnect")
def test_disconnect(mock_disconnect, monkeypatch):
    monkeypatch.setattr(joy_state, 'active', True)
    response = client.post("/api/disconnect")
    assert response.status_code == 200
    assert joy_state.active is False
    mock_disconnect.assert_called_once()

@patch("backend.device_manager.DeviceManager.set_location")
def test_set_location_valid(mock_set):
    response = client.post("/api/set_location", json={"lat": 40.7128, "lng": -74.0060})
    assert response.status_code == 200
    mock_set.assert_called_once_with(40.7128, -74.0060)

def test_set_location_invalid_latitude():
    # Latitude > 90 is physically impossible, should hit Pydantic 422 block
    response = client.post("/api/set_location", json={"lat": 95.0, "lng": -74.0})
    assert response.status_code == 422

def test_set_location_invalid_longitude():
    # Longitude > 180 is blocked
    response = client.post("/api/set_location", json={"lat": 40.0, "lng": 185.0})
    assert response.status_code == 422

def test_set_speed():
    response = client.post("/api/speed", json={"speed": 15.5})
    assert response.status_code == 200
    assert response.json()["speed"] == 15.5
    assert joy_state.speed == 15.5

def test_joystick_state_machine():
    # Start joystick
    response = client.post("/api/joystick", json={"action": "start", "heading": 90.0})
    assert response.status_code == 200
    assert joy_state.active is True
    assert joy_state.heading == 90.0

    # Update joystick
    response = client.post("/api/joystick", json={"action": "update", "heading": 180.0})
    assert response.status_code == 200
    assert joy_state.active is True
    assert joy_state.heading == 180.0

    # Stop joystick
    response = client.post("/api/joystick", json={"action": "stop", "heading": 180.0})
    assert response.status_code == 200
    assert joy_state.active is False
