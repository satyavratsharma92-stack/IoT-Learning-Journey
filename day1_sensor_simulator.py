# iot_day1_simulator.py
# Simulates a temperature + humidity sensor (like DHT11)
# Run this on any computer — no hardware needed!

import random
import time
import json
from datetime import datetime

# --- Simulate a sensor reading ---
def read_sensor():
    """
    In real IoT: this function would talk to actual hardware.
    For now we generate realistic random values.
    DHT11 range: Temperature 0-50°C, Humidity 20-90%
    """
    temperature = round(random.uniform(22.0, 38.0), 1)
    humidity    = round(random.uniform(40.0, 85.0), 1)
    return temperature, humidity

# --- Create an IoT data packet (JSON format) ---
def create_data_packet(device_id, temp, humidity):
    """
    Real IoT devices send data as JSON over the internet.
    This is what an ESP32 would actually transmit.
    """
    packet = {
        "device_id"  : device_id,
        "timestamp"  : datetime.now().isoformat(),
        "location"   : "Room-101",
        "sensors": {
            "temperature": {"value": temp,     "unit": "Celsius"},
            "humidity"   : {"value": humidity, "unit": "percent"}
        },
        "status": "ok"
    }
    return packet

# --- Check alert conditions ---
def check_alerts(temp, humidity):
    """
    Application layer logic — what should happen with the data?
    """
    alerts = []
    if temp > 35:
        alerts.append(f"HIGH TEMP ALERT: {temp}°C — Check cooling system!")
    if temp < 24:
        alerts.append(f"LOW TEMP ALERT:  {temp}°C — Room too cold!")
    if humidity > 75:
        alerts.append(f"HIGH HUMIDITY:   {humidity}% — Risk of condensation!")
    return alerts

# --- Main loop: simulates a device sending data every 2 seconds ---
print("=== IoT Sensor Simulator — Day 1 ===")
print(f"Device: SENSOR-001 | Location: Room-101")
print("-" * 45)

readings = []  # store readings for later analysis

for i in range(10):  # simulate 10 readings (in real IoT this runs forever)
    
    # Layer 1 — Perception: read from sensor
    temp, humidity = read_sensor()
    
    # Layer 2 — Network: create data packet (would be sent via MQTT/HTTP)
    packet = create_data_packet("SENSOR-001", temp, humidity)
    
    # Layer 3 — Application: process and display
    print(f"\nReading #{i+1} | {packet['timestamp'][11:19]}")
    print(f"  Temperature : {temp}°C")
    print(f"  Humidity    : {humidity}%")
    
    # Check alerts
    alerts = check_alerts(temp, humidity)
    if alerts:
        for alert in alerts:
            print(f"  ⚠ {alert}")
    else:
        print(f"  Status: All normal")
    
    # Store reading
    readings.append({"temp": temp, "humidity": humidity})
    
    time.sleep(2)  # wait 2 seconds between readings

# --- Simple analysis after 10 readings ---
print("\n" + "=" * 45)
print("SESSION SUMMARY (Application Layer Analysis)")
print("=" * 45)
avg_temp     = sum(r["temp"]     for r in readings) / len(readings)
avg_humidity = sum(r["humidity"] for r in readings) / len(readings)
max_temp     = max(r["temp"]     for r in readings)
min_temp     = min(r["temp"]     for r in readings)

print(f"  Average temp     : {avg_temp:.1f}°C")
print(f"  Average humidity : {avg_humidity:.1f}%")
print(f"  Max temp         : {max_temp}°C")
print(f"  Min temp         : {min_temp}°C")

# Save to JSON file (simulating cloud data storage)
with open("sensor_log.json", "w") as f:
    json.dump(readings, f, indent=2)
print(f"\n  Data saved to sensor_log.json")
print("  (In real IoT, this goes to a cloud database)")