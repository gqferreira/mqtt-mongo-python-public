from app.services.device_service import insert_device, get_device
from app.services.telemetry_service import insert_telemetry
from bson import ObjectId, DBRef
from datetime import datetime, UTC
import app.config as config

def test_list_all_telemetries_success(client): 
    insert_device({
        "channel": "channel-test3",
        "description": "Device test 3",
    })
    
    device = get_device("channel-test3")
    telemetry = {"date": datetime.now(UTC), "light": 10, "temperature": 20}
    insert_telemetry(telemetry=telemetry, device=device)
    
    response = client.get("/telemetry")
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    first = data[0]

    assert "channel" in first
    assert "date" in first
    assert "description" in first
    assert "light" in first
    assert "temperature" in first

    assert isinstance(first["channel"], str)
    assert isinstance(first["date"], str)
    assert isinstance(first["description"], str)
    assert isinstance(first["light"], int)
    assert isinstance(first["temperature"], int)
    
def test_list_channel_telemetries_success(client):
    
    insert_device({
        "channel": "channel-test4",
        "description": "Device test 4",
    })
    
    device = get_device("channel-test4")
    telemetry = {"date": datetime.now(UTC), "light": 10, "temperature": 20}
    insert_telemetry(telemetry=telemetry, device=device)
    
    response = client.get("/telemetry/channel-test4")
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    first = data[0]

    assert "channel" in first
    assert "date" in first
    assert "description" in first
    assert "light" in first
    assert "temperature" in first

    assert isinstance(first["channel"], str)
    assert isinstance(first["date"], str)
    assert isinstance(first["description"], str)
    assert isinstance(first["light"], int)
    assert isinstance(first["temperature"], int)

def test_list_channel_telemetries_empty(client):
    
    response = client.get("/telemetry/channel-X")
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0
