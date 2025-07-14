import pytest
import json
from unittest.mock import MagicMock, patch
from app import mqtt_client
from bson import ObjectId

@patch("app.mqtt_client.insert_telemetry")
@patch("app.mqtt_client.get_device")
def test_on_message_valid_payload(mock_get_device, mock_insert_telemetry):
    
    telemetry = {"temperature": 25, "light": 300}
    topic = "telemetry-7835/device1"
    payload = json.dumps(telemetry).encode()

    msg = MagicMock()
    msg.topic = topic
    msg.payload = payload

    device = {"_id": ObjectId("687304546c1d0728ac85be8a"), "channel": "device1", "status": True, "description": "Device 1"}
    
    mock_get_device.return_value = device

    mqtt_client.on_message(None, None, msg)

    mock_get_device.assert_called_once_with("device1")

    mock_insert_telemetry.assert_called_once_with(
        telemetry,
        device
    )

def test_on_connect_success():
    client = MagicMock()
    userdata = None
    flags = None
    rc = 0

    with patch("app.mqtt_client.config.MQTT_TOPIC", "telemetry-7835/#"):
        mqtt_client.on_connect(client, userdata, flags, rc)
        client.subscribe.assert_called_once_with("telemetry-7835/#")
