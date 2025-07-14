import paho.mqtt.client as mqtt
import json
import random
import time

# Broker configuration
BROKER = "test.mosquitto.org"
PORT = 1883
TOPIC = "telemetry-7835/device1"

# Function to generate random telemetry data
def generate_payload():
    return {
        "light": random.randint(0, 999),
        "temperature": random.randint(0, 999)
    }

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print("Failed to connect. Return code:", rc)

# Create MQTT client and configure callbacks
client = mqtt.Client()
client.on_connect = on_connect

# Connect to the broker
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

# Publish telemetry every 1 second
try:
    while True:
        payload = generate_payload()
        client.publish(TOPIC, json.dumps(payload))
        print(f"Published to {TOPIC}: {payload}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nStopped by user.")
    client.loop_stop()
    client.disconnect()
