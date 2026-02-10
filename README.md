# Project Agri-Stack
### End-to-End MLOps Pipeline for Precision Livestock Farming (PLF)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Field: Agri-Tech](https://img.shields.io/badge/Field-Agri--Tech-green)](https://github.com/)
[![Focus: Data Engineering](https://img.shields.io/badge/Focus-Data--Engineering-blue)](https://github.com/)

## 1. Executive Summary
Poultry farming in tropical regions (specifically Bangladesh) is plagued by high mortality rates due to human error in manual dosing and reactive climate control. 

**Agri-Stack** is a professional-grade MLOps platform that transitions poultry management from "Observation-based" to "Data-Driven Prediction." The system is designed to handle high-frequency sensor streams and provide real-time automated intervention for life-critical poultry environments.

---

## 2. Current Architecture (Lite / Local Development)
Due to resource constraints (8GB RAM), the initial development phase uses a **Serverless / Cloud-Hybrid** approach:

*   **Mock Sensor (Simulation):** Python script simulating ESP32 telemetry (Temp, Humidity, Ammonia).
*   **Message Broker (Cloud):** **HiveMQ Cloud** (MQTT) for reliable data transport.
*   **Ingestion Bridge:** A lightweight Python service (`ingest_to_supabase.py`) that subscribes to MQTT and upserts data.
*   **Database (Cloud):** **Supabase** (PostgreSQL) with `TimescaleDB` optimizations for time-series data.
*   **Visualization:** **Streamlit** Dashboard for real-time monitoring and alerts.

---

## 3. Deployment Guide (Quick Start)

### Prerequisites
1.  **Python 3.9+** installed.
2.  Create a `.env` file with your HiveMQ and Supabase credentials (see `.env.example`).
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Pipeline (3 Terminals Required)
To run the full system, open **3 separate terminal windows**:

**Terminal 1: Ingestion Bridge** (Connects HiveMQ -> Supabase)
```bash
source .venv/bin/activate
python scripts/ingest_to_supabase.py
```

**Terminal 2: Mock Sensor** (Generates telemetry -> HiveMQ)
```bash
source .venv/bin/activate
python scripts/mock_sensor.py
```

**Terminal 3: Streamlit Dashboard** (Visualizes Supabase data)
```bash
source .venv/bin/activate
streamlit run dashboard/app.py
```

---

## 4. Future Roadmap (Scale-Out)
For production scale deployment, the architecture will evolve to:
*   **Edge Layer:** Physical ESP32 nodes with LoRaWAN/WiFi.
*   **Ingestion:** **Redpanda** (Kafka-compatible) for high-throughput buffering.
*   **Processing:** **Apache Spark** for complex event processing.
*   **MLOps:** **MLflow** for model registry and **Airflow** for orchestration.

---
**Lead Engineer:** [Md Fakrul Islam Taraque](https://github.com/MdFakrulIslamTaraque)  