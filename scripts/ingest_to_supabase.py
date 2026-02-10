"""
Script: ingest_to_supabase.py
Purpose: Bridges MQTT (HiveMQ Cloud) to Supabase (PostgreSQL).
Constraints: Low RAM (8GB PC), Robust Error Handling.

Author: Antigravity (Assistant to Fakrul)
"""

import os
import json
import time
import logging
from typing import Dict, Any

# Lightweight imports
import paho.mqtt.client as mqtt
from supabase import create_client, Client
from dotenv import load_dotenv

# --- Configuration & Setup ---
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables (Fail fast if missing)
try:
    HIVEMQ_HOST = os.environ["HIVEMQ_HOST"]
    HIVEMQ_PORT = int(os.environ.get("HIVEMQ_PORT", 8883))
    HIVEMQ_USER = os.environ["HIVEMQ_USERNAME"]
    HIVEMQ_PASS = os.environ["HIVEMQ_PASSWORD"]
    
    SUPABASE_URL = os.environ["SUPABASE_URL"]
    SUPABASE_KEY = os.environ["SUPABASE_KEY"] # Use Service Role Key for writing
except KeyError as e:
    logger.error(f"Missing Environment Variable: {e}")
    exit(1)

MQTT_TOPIC = "agri/telemetry/#"

# --- Supabase Client ---
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logger.critical(f"Failed to initialize Supabase client: {e}")
    exit(1)

# --- Logic ---

def parse_and_validate(payload: str) -> Dict[str, Any]:
    """
    Parses incoming JSON and validates essential fields.
    Returns: Dict or None if invalid.
    """
    try:
        data = json.loads(payload)
        
        # Minimal Validation
        if "device_id" not in data:
            logger.warning(f"Payload missing 'device_id': {payload}")
            return None
            
        return data
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received: {payload}")
        return None

def save_to_supabase(data: Dict[str, Any]):
    """
    Inserts validated data into Supabase 'brooder_telemetry' table.
    """
    try:
        # Prepare record
        record = {
            "device_id": data.get("device_id"),
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
            "ammonia_ppm": data.get("ammonia"), # Mapping 'ammonia' to DB col 'ammonia_ppm'
            "raw_data": data, # Store full raw payload for debugging
            # timestamp will be handled by DB default (now()) if not provided,
            # but ideally the device sends a 'timestamp' field.
        }
        
        # Add timestamp if provided by device (Unix or ISO)
        # Add timestamp if provided by device (Unix or ISO)
        if "timestamp" in data:
            ts = data["timestamp"]
            # Convert Unix float to ISO 8601 if needed
            if isinstance(ts, (int, float)):
                from datetime import datetime, timezone
                ts = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
            record["timestamp"] = ts

        # Insert
        response = supabase.table("brooder_telemetry").insert(record).execute()
        logger.info(f"Persisted to Supabase: ID: {data.get('device_id')}")
        
    except Exception as e:
        logger.error(f"Supabase Insert Failed: {e}")

# --- MQTT Callbacks ---

def on_connect(client, userdata, flags, rc):
    connection_codes = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised"
    }
    if rc == 0:
        logger.info("Connected to HiveMQ Cloud!")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to {MQTT_TOPIC}")
    else:
        logger.error(f"Connection failed: {connection_codes.get(rc, 'Unknown error')}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        logger.debug(f"RX [{msg.topic}]: {payload}")
        
        data = parse_and_validate(payload)
        if data:
            save_to_supabase(data)
            
    except Exception as e:
        logger.error(f"Error processing message: {e}")

# --- Main Loop ---

def main():
    # Paho MQTT v2 requires explicit callback API version
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="agri_stack_bridge_v1")
    
    # TLS is mandatory for HiveMQ Cloud
    client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
    client.username_pw_set(HIVEMQ_USER, HIVEMQ_PASS)
    
    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(f"Connecting to Broker: {HIVEMQ_HOST}:{HIVEMQ_PORT}...")
    
    try:
        client.connect(HIVEMQ_HOST, HIVEMQ_PORT, 60)
        client.loop_forever() # Blocking loop, handles reconnects automatically
    except KeyboardInterrupt:
        logger.info("Stopping Bridge...")
        client.disconnect()
    except Exception as e:
        logger.critical(f"Fatal MQTT Error: {e}")

if __name__ == "__main__":
    main()
