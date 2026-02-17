# Agri-Stack: Hardware Simulation Setup Guide 🚜

**Goal:** We are building a "Digital Twin" simulator. Since we don't have real chickens yet, we will use a **Potentiometer (Knob)** to simulate **Temperature** and an **MQ Sensor** to simulate air quality (Ammonia).

---

## 🛠️ Phase 1: The Breadboard Wiring (The "Power Strip" Method)
**Problem:** The Arduino only has **one** 5V pin, but we have **two** components (Potentiometer + MQ Sensor) that need power.
**Solution:** We use the Breadboard like a power strip!

### Step 1: Power the Breadboard
Look at your breadboard. It has long lines on the sides, usually marked with **Red (+)** and **Blue (-)** lines.
1.  **Red Rail (+)**: Connect a wire from **Arduino 5V** to any hole in the **Red (+)** line on the breadboard.
    *   *Now the entire Red line is "hot" with 5V power.*
2.  **Blue Rail (-)**: Connect a wire from **Arduino GND** to any hole in the **Blue (-)** line on the breadboard.
    *   *Now the entire Blue line is Ground.*

### Step 2: Connect the Potentiometer (The Knob)
1.  **Left Leg** → Plug into a hole in the main area (e.g., Row 10). From that same row, run a wire to the **Red (+) Rail**.
2.  **Right Leg** → Plug into the main area (e.g., Row 12). Run a wire from that row to the **Blue (-) Rail**.
3.  **Middle Leg** → Plug into the main area (e.g., Row 11). Run a wire from that row directly to **Arduino Pin A0**.

### Step 3: Connect the MQ Sensor (The Nose)
*Use your Male-to-Female wires here.*
1.  **VCC** (Female side on sensor) → Male side goes to the **Red (+) Rail** on the breadboard.
2.  **GND** (Female side on sensor) → Male side goes to the **Blue (-) Rail** on the breadboard.
3.  **A0** (Analog Output) → Male side goes directly to **Arduino Pin A1**.

---

## 💻 Phase 2: The Firmware (Arduino Software)
Now we teach the Arduino what to do with these sensors.

1.  **Plug in the Arduino** to your computer via USB.
2.  Open the **Arduino IDE**.
3.  Open the file inside this project: `agri-stack/firmware/main.ino`.
4.  **Select your Board:**
    *   Go to `Tools` > `Board` > `Arduino Uno`.
    *   Go to `Tools` > `Port` > Select the one that says "Arduino" or "USB".
5.  **Click the Arrow Button (➜)** to Upload.
    *   You should see "Done uploading" at the bottom.
6.  **Test it:**
    *   Click the **Magnifying Glass** (top right) to open "Serial Monitor".
    *   Set the baud rate (bottom right corner of the window) to **9600 baud**.
    *   You should see text like:
        `{"temperature": 25.0, "ammonia": 12, "humidity": 65.0}`
    *   **Twist the knob!** The `temperature` number should change.
    *   **Close the Serial Monitor window.** (This is important! The next step won't work if this window is open).

---

## 🐍 Phase 3: The Gateway (Python Bridge)
The Arduino is shouting data, but we need Python to catch it and put it on the internet.

1.  **Open your Terminal** (VS Code Terminal is fine).
2.  **Activate the Virtual Environment** (Always do this first!):
    ```bash
    source .venv/bin/activate
    ```
3.  **Run the Bridge Script:**
    ```bash
    python scripts/serial_bridge.py
    ```
4.  **Check Output:**
    *   It should say: `Connected to HiveMQ Cloud!`
    *   Then: `Published: {'device_id': ..., 'temperature': 32.5 ...}`

---

## 🚀 Phase 4: See it Live
1.  Leave the bridge script running.
2.  Open a **New Terminal** (Keep the first one open!).
3.  Activate `.venv` again: `source .venv/bin/activate`.
4.  **Run the Dashboard:**
    ```bash
    streamlit run dashboard/app.py
    ```
5.  Your browser will open. You should see the graphs moving!

---

## ❓ Troubleshooting

### Error: `Device or resource busy: '/dev/ttyACM0'`
This means something else is already talking to the Arduino.
1.  **Check Arduino IDE:** Did you leave the **Serial Monitor** window open? **Close it.**
2.  **Check other terminals:** Did you leave an old version of the script running?
3.  **Fix:** Close the Serial Monitor and try running the command again.
