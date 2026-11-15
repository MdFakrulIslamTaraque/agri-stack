# Project Agri-Stack

### Real-time IoT telemetry pipeline for poultry brooder monitoring

[![Field: Agri-Tech](https://img.shields.io/badge/Field-Agri--Tech-green)](https://github.com/)
[![Focus: Data Engineering](https://img.shields.io/badge/Focus-Data--Engineering-blue)](https://github.com/)
[![Status: Working prototype](https://img.shields.io/badge/Status-Working%20prototype-orange)](https://github.com/)

---

## 1. What this is

Poultry brooders in tropical regions need tight control of temperature, humidity and ammonia. Getting it
wrong kills birds, and most small farms run on spot checks and memory.

**Agri-Stack is the data layer for that problem.** A sensor publishes a JSON reading, a broker carries it,
an ingestion service validates and stores it, and a dashboard shows it live with threshold alerts.

It is a **working prototype**, built solo to practise end-to-end pipeline design. It is not a product and it
does not yet run on a farm. What follows describes exactly what the code does — see
[Known limitations](#5-known-limitations) for what it does not.

---

## 2. Architecture (as built)

```
 ┌──────────────────────┐
 │ mock_sensor.py       │  simulated ESP32, publishes every 5 s
 │                      │  topic: agri/telemetry/mock_esp32
 ├──────────────────────┤
 │ firmware/main.ino    │  Arduino + potentiometer (temp) + MQ gas
 │  → serial_bridge.py  │  sensor (ammonia); JSON over USB serial,
 │                      │  republished to agri/telemetry/serial_bridge
 └──────────┬───────────┘
            │  MQTT over TLS (port 8883)
            ▼
 ┌──────────────────────┐
 │ HiveMQ Cloud         │  managed MQTT broker (free tier)
 └──────────┬───────────┘
            │  subscribes agri/telemetry/#
            ▼
 ┌──────────────────────┐
 │ ingest_to_supabase.py│  validates payload, maps fields,
 │                      │  normalises timestamps, inserts
 └──────────┬───────────┘
            ▼
 ┌──────────────────────┐
 │ Supabase PostgreSQL  │  table: brooder_telemetry
 │                      │  index (device_id, timestamp DESC)
 └──────────┬───────────┘
            │  last 50 rows, polled every 3 s
            ▼
 ┌──────────────────────┐
 │ Streamlit dashboard  │  KPIs, trend charts, threshold alerts
 └──────────────────────┘
```

| Layer | Technology | File |
|---|---|---|
| Simulated source | Python, paho-mqtt | `scripts/mock_sensor.py` |
| Hardware source | Arduino C++ (potentiometer + MQ gas sensor) | `firmware/main.ino` |
| Serial gateway | Python, pyserial → MQTT | `scripts/serial_bridge.py` |
| Broker | HiveMQ Cloud (MQTT over TLS) | — |
| Ingestion | Python, paho-mqtt + supabase-py | `scripts/ingest_to_supabase.py` |
| Storage | Supabase (PostgreSQL) | `migrations/01_init_telemetry.sql` |
| Dashboard | Streamlit + pandas | `dashboard/app.py`, `dashboard/data_loader.py` |
| Deploy shim | Flask "web shell" for Render's free tier | `scripts/bridge_service.py` |

---

## 3. Data model

`brooder_telemetry` is deliberately simple, with three decisions worth calling out:

```sql
create table if not exists brooder_telemetry (
  id            bigint generated always as identity primary key,
  device_id     text not null,
  timestamp     timestamptz not null default now(),
  temperature   float,
  humidity      float,
  ammonia_ppm   float,
  raw_data      jsonb,          -- full original payload
  created_at    timestamptz default now()
);

create index if not exists idx_telemetry_device_time
  on brooder_telemetry (device_id, timestamp desc);
```

1. **`TIMESTAMPTZ`, not `TIMESTAMP`.** Devices on farms in different zones should land on one comparable
   time axis. The ingestion service converts Unix-epoch floats from the device to ISO-8601 before insert.
2. **`raw_data jsonb` keeps the original payload.** If a firmware revision adds or renames a field, the
   typed columns may miss it but nothing is lost — the row can be reprocessed. Cheap insurance against
   schema drift on devices you cannot redeploy quickly.
3. **The index matches the read pattern, not the write.** Every dashboard query is "latest N readings for
   this device", so `(device_id, timestamp desc)` serves it directly without a sort.

Row-level security is enabled on the table (see the caveat under limitations).

---

## 4. Running it

### Prerequisites

- Python 3.9+
- A free [HiveMQ Cloud](https://console.hivemq.cloud) cluster and a free [Supabase](https://supabase.com) project
- `cp .env.example .env` and fill in the credentials described there

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Then apply `migrations/01_init_telemetry.sql` in the Supabase SQL editor.

### Three terminals

```bash
# 1. Ingestion bridge: HiveMQ -> Supabase
python scripts/ingest_to_supabase.py

# 2. A data source — either the simulator...
python scripts/mock_sensor.py
#    ...or a real board over USB (auto-detects the port)
python scripts/serial_bridge.py                    # default 115200 baud
python scripts/serial_bridge.py /dev/ttyACM0 9600  # Arduino Uno running main.ino

# 3. Dashboard
streamlit run dashboard/app.py
```

For the hardware path (breadboard wiring, Arduino IDE upload), see [HARDWARE_SETUP.md](HARDWARE_SETUP.md).

---

## 5. Known limitations

Stated plainly, because a prototype that hides its gaps is harder to build on.

**Sensing**

- The Arduino sketch uses a **potentiometer in place of a temperature sensor** — it is a knob, not a thermometer.
- The **MQ gas sensor is uncalibrated**. Its reading is mapped linearly onto a 0–100 "ppm" scale to prove the
  data path; the number is not a real ammonia concentration.
- **Humidity is hardcoded** to `65.0` in `main.ino`.
- ESP32 firmware for real sensors exists in `firmware/esp32_real_sensors` but is **committed untested**.

**Pipeline**

- Ingestion **inserts**; it does not upsert or deduplicate. A broker redelivery produces a duplicate row.
  There is no idempotency key.
- Messages are published at the paho default QoS 0 — fine for a live dashboard, not for data that must not
  be lost.
- `ingest_to_supabase.py` still uses the paho **v1 callback API** while both publishers use v2. It works,
  but it should be unified.
- No automated tests.

**Storage and security**

- This is **plain PostgreSQL**. There is no TimescaleDB hypertable, no partitioning and no retention policy,
  so the table grows unbounded.
- RLS is enabled but the policies are **permissive** (`insert … with check (true)`, `select … using (true)`)
  — appropriate for a demo, not for production.
- The dashboard reads the **last 50 rows only**, so it shows recent trend, not history.

**Scope**

- There is **no machine learning** in this repository: no model, no training, no inference. The alerts are
  fixed thresholds (`temperature > 35 °C`, `ammonia > 1.0 ppm`) evaluated in the dashboard.
- There is **no actuation or control loop**. Nothing adjusts a heater or a fan; the system observes and warns.

---

## 6. Roadmap — *not built*

Everything in this section is intended direction, not working code.

- **Edge:** physical ESP32 nodes with calibrated DHT22 and MQ-137 sensors over WiFi/LoRaWAN.
- **Ingestion:** a durable log (Kafka or Redpanda) in place of direct broker→database writes, for replay
  and buffering.
- **Storage:** TimescaleDB hypertables with continuous aggregates and a retention policy.
- **Processing:** stream processing for windowed anomaly detection.
- **ML:** once enough labelled data exists, mortality-risk prediction — with MLflow for the model registry
  and Airflow for orchestration. Not started.

---

**Author:** [Md Fakrul Islam Taraque](https://github.com/MdFakrulIslamTaraque)
