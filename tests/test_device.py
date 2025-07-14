from app.services.device_service import insert_device, get_device

def test_post_device_insert_success(client):
    payload = {"channel": "channel-test1", "description": "Device test"}
    response = client.post("/device", json=payload)
    
    assert response.status_code == 201
    assert "message" in response.get_json()
    
def test_post_device_update_success(client):
    insert_device({
        "channel": "channel-test2",
        "description": "Device test 2",
    })
    
    payload = {"channel": "channel-test2", "description": "Device test 2"}
    response = client.post("/device", json=payload)
    
    assert response.status_code == 200
    assert "message" in response.get_json()

def test_post_device_error(client):
    payload = {"channel": 123}
    response = client.post("/device", json=payload)
    
    assert response.status_code == 400
    assert "message" in response.get_json()
    
def test_device_not_found(client):
    response = get_device("nonexistent-device")
    
    assert response is None