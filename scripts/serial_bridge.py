#!/usr/bin/env python3
"""
Script: serial_bridge.py
Purpose: Reads JSON from any board (Arduino / ESP32) via USB Serial and publishes to HiveMQ Cloud.
Usage:
  python scripts/serial_bridge.py                      # auto-detect port, 115200 baud
  python scripts/serial_bridge.py /dev/ttyUSB0          # specify port (ESP32)
  python scripts/serial_bridge.py /dev/ttyACM0 9600     # specify port + baud (Arduino)
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

DEFAULT_BAUD = 115200  # ESP32 firmware uses 115200; old Arduino sketch used 9600

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SerialBridge")

def get_serial_port():
    """
    Attempts to auto-detect port for Arduino (ttyACM) or ESP32 (ttyUSB).
    Port can also be passed as first CLI argument.
    Baud rate can be passed as second CLI argument (default 115200).
    """
    port = sys.argv[1] if len(sys.argv) > 1 else None
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_BAUD

    if port:
        return port, baud

    """ 
    as the esp32 is connected to the computer, it will be listed as a serial port
    we need to find the port that corresponds to the esp32
    here, the comports() function will return a list of all available serial ports
    we need to find the port that corresponds to the esp32
    """
    ports = list(serial.tools.list_ports.comports())
    
    # Match ESP32 (ttyUSB) and Arduino (ttyACM) on Linux
    board_ports = [
        p.device for p in ports 
        if any(x in p.device for x in ["ttyUSB", "ttyACM"])
        or "Arduino" in (p.description or "")
        or "Silicon Labs" in (p.description or "")
        or "CP210" in (p.description or "")
    ]

    if not board_ports:
        logger.error("No device found! Connect your board or specify port manually.")
        logger.info("Available ports: " + ", ".join([p.device for p in ports]))
        sys.exit(1)
        
    return board_ports[0], baud  # Return first match

def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logger.info("Connected to HiveMQ Cloud!")
    else:
        logger.error(f"MQTT Connection Failed: {reason_code}")

def main():
    # 1. Setup Serial
    port, baud = get_serial_port()
    logger.info(f"Connecting to {port} at {baud} baud...")
    
    try:
        ser = serial.Serial(port, baud, timeout=1)
        time.sleep(2) # Wait for board reset
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
    logger.info("Listening for data...")
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue
                
                logger.debug(f"Raw from Serial: {line}")
                
                try:
                    # Parse JSON from board
                    data = json.loads(line)
                    
                    # Build payload - preserve device_id if firmware sends it (ESP32 does)
                    payload = {
                        "device_id": data.get("device_id", "serial-bridge-unknown"),
                        "timestamp": time.time(),
                        "temperature": data.get("temperature"),
                        "ammonia": data.get("ammonia"),
                        "humidity": data.get("humidity", 60.0),
                    }
                    
                    # Publish
                    client.publish(TOPIC, json.dumps(payload))
                    logger.info(f"Published: {payload}")
                    
                except json.JSONDecodeError:
                    # Boards sometimes print debug text on startup
                    logger.warning(f"Ignored non-JSON line: {line}")
                    
    except KeyboardInterrupt:
        logger.info("Stopping Bridge...")
        client.loop_stop()
        ser.close()
        logger.info("Disconnected.")

if __name__ == "__main__":
    main()
