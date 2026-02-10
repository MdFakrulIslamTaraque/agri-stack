# Project Agri-Stack
### End-to-End MLOps Pipeline for Precision Livestock Farming (PLF)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Field: Agri-Tech](https://img.shields.io/badge/Field-Agri--Tech-green)](https://github.com/)
[![Tech: Data Engineering](https://img.shields.io/badge/Focus-Data--Engineering-blue)](https://github.com/)

## 1. Executive Summary
Poultry farming in tropical regions (specifically Bangladesh) faces high mortality rates due to **Heat Stress** and **Ammonia Toxicity**. Traditional monitoring is reactive and manual. 

**Agri-Stack** is a proactive, end-to-end data platform that leverages **Edge AI** for behavioral analysis and **Distributed Data Processing** for microclimate forecasting. It transitions poultry management from "Observation-based" to "Data-Driven Prediction."

---

## 2. System Architecture (The DE Stack)
The project is architected to demonstrate a professional **Modern Data Stack** capable of handling thousands of sensors at scale.

*   **Edge Layer:** ESP32-based sensors (DHT22, MQ-135) and ESP32-CAM. Implements **Store-and-Forward** logic to handle intermittent rural WiFi connectivity.
*   **Ingestion Layer:** Containerized **Eclipse Mosquitto (MQTT)** acting as the broker, bridged to a **Redpanda/Kafka** message bus for fault-tolerant data streaming.
*   **Processing Layer:** **Apache Spark (Structured Streaming)** for real-time feature engineering (Heat Index calculation, windowed averages) and anomaly detection.
*   **Storage Layer (Data Lakehouse):** **MinIO (S3-compatible)** using **Delta Lake** format to ensure ACID transactions on IoT time-series data.
*   **Orchestration:** **Apache Airflow** for daily ETL jobs, model retraining triggers, and health reporting.
*   **MLOps:** **DVC (Data Version Control)** for scientific reproducibility and **MLflow** for experiment tracking.

---

## 3. Core Research Scopes (PhD Narrative)
This project serves as the foundation for research in **Cyber-Physical Systems (CPS)**:
1.  **Behavioral Proxy Metrics:** Using Computer Vision (Centroid Distance Analysis) to estimate thermal comfort without expensive infrared hardware.
2.  **Edge-Cloud Hybrid Inference:** Optimizing model latency by running lightweight Anomaly Detection on the ESP32 (TinyML) while running complex LSTM forecasting in the cloud.
3.  **Resilient Architectures:** Designing systems that maintain data integrity in low-bandwidth, high-latency environments.

---

## 4. Current Progress: Digital Twin (Phase 1)
To ensure system stability before hardware deployment, we utilize a **Digital Twin simulation**:
- [x] Dockerized Infrastructure (Mosquitto, InfluxDB).
- [x] Python-based Mock Sensor (Intermittent data simulation).
- [ ] PySpark Streaming Integration.
- [ ] ESP32 Hardware Integration.

---

## 5. Local Setup (Development)

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- MQTT Explorer (for debugging)

### Deployment
1. **Launch Infrastructure:**
   ```bash
   docker-compose up -d
   ```
2. **Start Mock Sensor (Digital Twin):**
   ```bash
   pip install paho-mqtt
   python scripts/mock_sensor.py
   ```
3. **Monitor InfluxDB:**
   Access `http://localhost:8086` to view real-time telemetry.

---
**Lead Engineer:** [Fakrul Islam](https://github.com/your-profile)  
**Vision:** From Data Engineering to Edge AI Infrastructure Research.

---