# Project Agri-Stack
### End-to-End MLOps Pipeline for Precision Livestock Farming (PLF)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Field: Agri-Tech](https://img.shields.io/badge/Field-Agri--Tech-green)](https://github.com/)
[![Focus: Data Engineering](https://img.shields.io/badge/Focus-Data--Engineering-blue)](https://github.com/)

## 1. Executive Summary
Poultry farming in tropical regions (specifically Bangladesh) is plagued by high mortality rates due to human error in manual dosing and reactive climate control. 

**Agri-Stack** is a professional-grade MLOps platform that transitions poultry management from "Observation-based" to "Data-Driven Prediction." The system is designed to handle high-frequency sensor streams and provide real-time automated intervention for life-critical poultry environments.

---

## 2. System Architecture (The DE Stack)
The project is architected to demonstrate a professional **Modern Data Stack** capable of handling thousands of sensors at scale.

*   **Edge Layer (IoT):** 
    *   **ESP32-CAM:** Real-time behavioral analysis (Chick clustering detection via Centroid Distance).
    *   **ESP32 DevKit:** Multi-sensor telemetry (Temp, Humidity, Ammonia/NH3).
    *   **Logic:** Implements a **Store-and-Forward** buffer to handle intermittent rural WiFi.
*   **Ingestion Layer:** 
    *   **MQTT (Mosquitto):** Lightweight IoT broker.
    *   **Redpanda (Kafka-Compatible):** High-throughput message bus for stream persistence.
*   **Processing Layer:** 
    *   **Apache Spark (Structured Streaming):** Real-time feature engineering (Heat Index, windowed smoothing).
    *   **Logic:** Handling late-arriving data via Watermarking.
*   **Storage Layer:** 
    *   **MinIO (S3-Compatible):** Local object storage.
    *   **Delta Lake:** Ensuring ACID transactions and schema enforcement on Parquet-backed time-series data.
*   **Orchestration & MLOps:** 
    *   **Apache Airflow:** Scheduling batch ETL and model retraining.
    *   **MLflow:** Experiment tracking for microclimate forecasting models.

---

## 3. Real-World Field Challenges (Problem Statements)
*   **Manual Medication:** Transitioning from hand-mixing to **Automated Volumetric Dosing** (Peristaltic Pump + Flow Sensor).
*   **Ammonia Management:** Automated mitigation of NH3 toxicity via **MQ-135 sensors** and adaptive ventilation.
*   **Thermal Comfort:** Replacing manual observation with **CV-based Behavioral Proxies** (Huddling/Scattering detection).

---

## 4. Local Development Strategy
The project follows a **"Digital Twin"** first approach.
1.  **Phase 1 (Infrastructure):** Dockerize the full stack (Mosquitto, Redpanda, MinIO, InfluxDB).
2.  **Phase 2 (Simulation):** Python-based mock sensors to stress-test the Spark Streaming pipelines.
3.  **Phase 3 (Hardware):** Integration of ESP32 physical nodes.

---

## 5. Deployment Guide
```bash
# 1. Start the Dockerized Infrastructure
docker-compose up -d

# 2. Monitor Streams
# Use MQTT Explorer on port 1883 or Redpanda Console on port 8080
```

---
**Lead Engineer:** [Md Fakrul Islam Taraque](https://github.com/MdFakrulIslamTaraque)  