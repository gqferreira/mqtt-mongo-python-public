from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_DIR = os.path.join(BASE_DIR, 'env')

print('BASE_DIR:', BASE_DIR)
print('ENV_DIR:', ENV_DIR)

env_type = os.getenv("ENV", "local")
env_file = os.path.join(ENV_DIR, env_type, '.env')
print('env_file:', env_file)
print(f'ENV {env_type} loaded:', load_dotenv(dotenv_path=env_file))

MQTT_URL = os.getenv("MQTT_URL", "")
MQTT_PORT = int(os.getenv("MQTT_PORT", 0))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "")

print(env_type)
print(MQTT_URL, ':', MQTT_PORT)
print(MQTT_USERNAME, '|', MQTT_PASSWORD)
print(MQTT_TOPIC)
print(MONGODB_URI, '@', MONGODB_DB)
print(20*'-')