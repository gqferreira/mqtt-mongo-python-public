import json
import threading
import time
import paho.mqtt.client as mqtt
from app.services.telemetry_service import insert_telemetry
from app.services.device_service import get_device
import app.config as config

RETRY_DELAY = 10

def on_connect(client, userdata, flags, rc):
	"""
    Callback function triggered when the MQTT client connects to the broker.

    Subscribes to the configured MQTT topic on successful connection.

    Args:
        client (mqtt.Client): The MQTT client instance.
        userdata: Private user data (not used).
        flags (dict): Response flags sent by the broker.
        rc (int): Connection result code (0 indicates success).
	"""
	if rc == 0:
		print("[MQTT] Subscribed to:", config.MQTT_TOPIC)
		client.subscribe(config.MQTT_TOPIC)
	else:
		print(f"[MQTT] Connection failed with code {rc}. Retrying in {RETRY_DELAY} seconds...")

def on_disconnect(client, userdata, rc):
	"""
    Callback function triggered when the MQTT client disconnects from the broker.

    Args:
        client (mqtt.Client): The MQTT client instance.
        userdata: Private user data (not used).
        rc (int): Disconnection result code (non-zero indicates unexpected disconnect).
	"""
	if rc != 0:
		print("[MQTT] Unexpected disconnection. Reconnecting...")
	else:
		print("[MQTT] Disconnected gracefully.")

def on_message(client, userdata, msg):
	"""
    Callback function triggered when a message is received on a subscribed topic.

    Parses the JSON payload and inserts telemetry data linked to the corresponding device.

    Args:
        client (mqtt.Client): The MQTT client instance.
        userdata: Private user data (not used).
        msg (mqtt.MQTTMessage): The received message, including topic and payload.
	"""
	try:
		payload = msg.payload.decode()
		data = json.loads(payload)
		print(f"[MQTT] Message received on {msg.topic}: {msg.payload}")

		device_topic = msg.topic.rsplit('/', 1)[-1]
    
		device = get_device(device_topic)
		insert_telemetry(data, device)
	except Exception as e:
		print("Error on MQTT message processing:", e)

def start_mqtt():
	"""
    Starts the MQTT client in a background thread.

    Connects to the MQTT broker using the configuration and listens indefinitely
    for incoming telemetry messages. Automatically retries connection if it fails.
	"""
	print("start_mqtt")
	def _run():
		print("MQTT _run")
		client = mqtt.Client()
		client.on_connect = on_connect
		client.on_disconnect = on_disconnect
		client.on_message = on_message
		while True:
			try:
				print(f"[MQTT] Trying to connect to {config.MQTT_URL}:{config.MQTT_PORT}")
				client.connect(config.MQTT_URL, config.MQTT_PORT, 60)
				client.loop_forever() 
				break
			except Exception as e:
				print(f"[MQTT] Connection failed: {e}")
				print("[MQTT] Retrying connection in", RETRY_DELAY, "seconds...")
				time.sleep(RETRY_DELAY)

	thread = threading.Thread(target=_run)
	thread.daemon = True
	thread.start()
