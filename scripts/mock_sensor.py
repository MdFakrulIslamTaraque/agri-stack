"""
Script: mock_sensor.py
Purpose: Simulates an ESP32 sending telemetry to HiveMQ.
Usage: Run this in a separate terminal to test the ingestion pipeline.
"""

import os
import time
import json
import random
import logging
import paho.mqtt.client as mqtt
import ssl
from dotenv import load_dotenv

load_dotenv()

# Configuration
HIVEMQ_HOST = os.environ.get("HIVEMQ_HOST")
HIVEMQ_PORT = int(os.environ.get("HIVEMQ_PORT", 8883))
HIVEMQ_USER = os.environ.get("HIVEMQ_USERNAME")
HIVEMQ_PASS = os.environ.get("HIVEMQ_PASSWORD")
TOPIC = "agri/telemetry/mock_esp32"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

if not all([HIVEMQ_HOST, HIVEMQ_USER, HIVEMQ_PASS]):
    logger.error("Missing credentials. Please check your .env file.")
    exit(1)

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        logger.error(f"Connection failed: {reason_code}. {properties}")
    else:
        logger.info("Mock Sensor Connected to HiveMQ!")

def simulate_telemetry():
    # v2 API Migration
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "mock_esp32_sensor")
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.username_pw_set(HIVEMQ_USER, HIVEMQ_PASS)
    client.on_connect = on_connect

    try:
        client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
        client.loop_start() # Start background thread for network loop

        while True:
            # Simulate sensor readings
            payload = {
                "device_id": "esp32-mock-01",
                "timestamp": time.time(), # Current Unix timestamp
                "temperature": round(random.uniform(28.0, 35.0), 2), # Brooder temp range
                "humidity": round(random.uniform(50.0, 70.0), 2),
                "ammonia": round(random.uniform(0.0, 1.5), 2),
                "status": "active"
            }
            
            client.publish(TOPIC, json.dumps(payload))
            logger.info(f"Published: {payload}")
            
            time.sleep(5) # Send every 5 seconds

    except KeyboardInterrupt:
        logger.info("Stopping Simulation...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    simulate_telemetry()
