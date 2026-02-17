#!/usr/bin/env python3
"""
Script: serial_bridge.py
Purpose: Reads JSON from Arduino (via USB Serial) and publishes to HiveMQ Cloud.
Usage: python scripts/serial_bridge.py [SERIAL_PORT]
"""

import sys
import os
import json
import time
import logging
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import ssl
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

HIVEMQ_HOST = os.environ.get("HIVEMQ_HOST")
HIVEMQ_PORT = int(os.environ.get("HIVEMQ_PORT", 8883))
HIVEMQ_USER = os.environ.get("HIVEMQ_USERNAME")
HIVEMQ_PASS = os.environ.get("HIVEMQ_PASSWORD")
TOPIC = "agri/telemetry/serial_bridge"

DEFAULT_BAUD = 9600

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SerialBridge")

def get_serial_port():
    """
    Attempts to auto-detect the Arduino port.
    Returns the port string or exits if not found.
    """
    if len(sys.argv) > 1:
        return sys.argv[1]

    ports = list(serial.tools.list_ports.comports())
    
    # Common Arduino descriptors
    arduino_ports = [
        p.device for p in ports 
        if "Arduino" in p.description or "USB" in p.description or "ttyACM" in p.device
    ]

    if not arduino_ports:
        logger.error("No Arduino found! Connect it or specify port manually.")
        logger.info("Available ports: " + ", ".join([p.device for p in ports]))
        sys.exit(1)
        
    return arduino_ports[0] # Return first match

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logger.info("Connected to HiveMQ Cloud!")
    else:
        logger.error(f"MQTT Connection Failed: {reason_code}")

def main():
    # 1. Setup Serial
    port = get_serial_port()
    logger.info(f"Connecting to Serial Port: {port}...")
    
    try:
        ser = serial.Serial(port, DEFAULT_BAUD, timeout=1)
        time.sleep(2) # Wait for Arduino reset
    except serial.SerialException as e:
        logger.critical(f"Could not open serial port {port}: {e}")
        sys.exit(1)

    # 2. Setup MQTT
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, "serial_bridge_gateway")
    client.tls_set(tls_version=ssl.PROTOCOL_TLS)
    client.username_pw_set(HIVEMQ_USER, HIVEMQ_PASS)
    client.on_connect = on_connect
    
    try:
        client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
        client.loop_start() # Background thread
    except Exception as e:
        logger.critical(f"Could not connect to MQTT Broker: {e}")
        sys.exit(1)

    # 3. Main Loop
    logger.info("Listening for data... (Twist that Potentiometer!)")
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                
                logger.debug(f"Raw from Serial: {line}")
                
                try:
                    # Parse JSON from Arduino
                    data = json.loads(line)
                    
                    # Enhance Data
                    payload = {
                        "device_id": "arduino-prototype-v0",
                        "timestamp": time.time(),
                        "temperature": data.get("temperature"),
                        "ammonia": data.get("ammonia"),
                        "humidity": data.get("humidity", 60.0)
                    }
                    
                    # Publish
                    client.publish(TOPIC, json.dumps(payload))
                    logger.info(f"Published: {payload}")
                    
                except json.JSONDecodeError:
                    # Arduino sometimes prints debug text (e.g. "Setup done")
                    logger.warning(f"Ignored non-JSON line: {line}")
                    
    except KeyboardInterrupt:
        logger.info("Stopping Bridge...")
        client.loop_stop()
        ser.close()
        logger.info("Disconnected.")

if __name__ == "__main__":
    main()
