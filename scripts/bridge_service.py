"""
Script: bridge_service.py
Purpose: Wraps the MQTT Bridge (ingest_to_supabase.py) in a Flask Web Server.
Why? To deploy on Render "Free Web Service" tier which requires HTTP traffic to stay alive.

Pattern: "Web Shell"
- Main Thread: Flask Server (responds to pings)
- Background Thread: MQTT Client (does the actual work)
"""

import sys
import os
# Add current directory to sys.path to ensure ingest_to_supabase can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import threading
import logging
from flask import Flask
try:
    from ingest_to_supabase import main as start_mqtt_bridge
except ImportError:
    # Fallback if run from root as module
    from scripts.ingest_to_supabase import main as start_mqtt_bridge

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BridgeService")

app = Flask(__name__)

@app.route("/")
def health_check():
    """
    Simple health check endpoint.
    External pingers (cron-job.org) will hit this to keep the service alive.
    """
    return "Agri-Stack Bridge is Running! 🐔", 200

import time

def run_bridge_in_background():
    """
    Runs the blocking MQTT loop in a separate daemon thread.
    Retries automatically if it crashes.
    """
    logger.info("Starting MQTT Bridge in background thread...")
    while True:
        try:
            start_mqtt_bridge()
        except Exception as e:
            logger.critical(f"Bridge Thread Crashed: {e}")
        
        logger.warning("Bridge stopped unexpectedly. Restarting in 10 seconds...")
        time.sleep(10)

# Start the background thread when the script loads
# Daemon=True means it will die when the main Flask process dies
bridge_thread = threading.Thread(target=run_bridge_in_background, daemon=True)
bridge_thread.start()

if __name__ == "__main__":
    # Get PORT from environment (Render sets this automatically)
    port = int(os.environ.get("PORT", 5000))
    
    # Run Flask server (blocks main thread)
    app.run(host="0.0.0.0", port=port)
