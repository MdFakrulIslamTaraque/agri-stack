// Pins
const int potPin = A0;  // Simulating Temperature
const int mqPin = A1;   // Simulating Ammonia

void setup() {
  Serial.begin(9600);
}

void loop() {
  // 1. Read Raw Values
  int potValue = analogRead(potPin);
  int mqValue = analogRead(mqPin);

  // 2. Map to "Real" Units
  // Potentiometer (0-1023) -> Temperature (20°C - 40°C)
  float temperature = map(potValue, 0, 1023, 200, 400) / 10.0;
  
  // MQ Sensor (0-1023) -> Ammonia PPM (0 - 100)
  // Note: This is not calibrated, just for showing data flow
  int ammonia = map(mqValue, 0, 1023, 0, 100);

  // 3. Create JSON String
  // Format: {"temperature": 32.5, "ammonia": 12, "humidity": 65}
  String payload = "{";
  payload += "\"temperature\": " + String(temperature) + ",";
  payload += "\"ammonia\": " + String(ammonia) + ",";
  payload += "\"humidity\": 65.0"; // Hardcoded for now
  payload += "}";

  // 4. Send to Laptop via USB
  Serial.println(payload);

  delay(2000); // Update every 2 seconds
}
