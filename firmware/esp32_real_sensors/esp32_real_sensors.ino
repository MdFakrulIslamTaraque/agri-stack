/*
  Firmware: esp32_real_sensors.ino
  Board:    ESP32 NodeMCU (30-pin)
  Sensors:  DHT22 (Temp + Humidity), MQ-137 (Ammonia)
  Output:   JSON over Serial (USB) at 115200 baud
  
  Wiring:
    DHT22:
      VCC  -> 3.3V on ESP32
      GND  -> GND
      DATA -> GPIO 4 (D4)
    MQ-137:
      VCC  -> 5V (VIN pin on ESP32, powered via USB)
      GND  -> GND
      A0   -> GPIO 34 (ADC1 - input only pin, safe for ADC)
*/

#include <DHT.h>

// --- Pin Definitions ---
#define DHT_PIN   4     // GPIO 4 for DHT22 data
#define DHT_TYPE  DHT22
#define MQ_PIN    34    // GPIO 34 for MQ-137 analog output

// --- DHT Sensor ---
DHT dht(DHT_PIN, DHT_TYPE);

// --- Timing ---
const unsigned long INTERVAL_MS = 2000; // Send every 2 seconds
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  delay(2000); // Give DHT22 time to stabilize
  Serial.println("ESP32 Agri-Stack Sensor Ready!");
}

void loop() {
  unsigned long now = millis();
  if (now - lastSendTime < INTERVAL_MS) return;
  lastSendTime = now;

  // 1. Read DHT22
  float temperature = dht.readTemperature(); // Celsius
  float humidity    = dht.readHumidity();

  // Check for read errors
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("{\"error\": \"DHT22 read failed\"}");
    return;
  }

  // 2. Read MQ-137 (Raw ADC 0-4095 on ESP32's 12-bit ADC)
  int mqRaw = analogRead(MQ_PIN);
  
  // Map raw ADC to an approximate PPM range for display
  // NOTE: Not scientifically calibrated. For visualization only.
  // Real calibration requires known gas concentrations.
  float ammoniaPPM = map(mqRaw, 0, 4095, 0, 100);

  // 3. Build JSON Payload
  String payload = "{";
  payload += "\"device_id\": \"esp32-v1\",";
  payload += "\"temperature\": " + String(temperature, 1) + ",";
  payload += "\"humidity\": "    + String(humidity, 1)    + ",";
  payload += "\"ammonia\": "     + String(ammoniaPPM)     + ",";
  payload += "\"mq_raw\": "      + String(mqRaw);
  payload += "}";

  // 4. Send over USB Serial
  Serial.println(payload);
}
