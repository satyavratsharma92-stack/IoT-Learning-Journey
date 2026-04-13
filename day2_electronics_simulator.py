# day2_electronics_simulator.py
# Simulates voltage divider calculations and sensor readings
# No hardware needed — pure Python

import math
import sys
import io

# This tells Python to always use UTF-8, which supports the Omega and Arrow symbols
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ─── CONCEPT 1: Ohm's Law calculator ───
def ohms_law(V=None, I=None, R=None):
    """Given any 2 values, calculate the third."""
    if V is None: return ("Voltage",   I * R)
    if I is None: return ("Current",   V / R)
    if R is None: return ("Resistance", V / I)

print("=" * 50)
print("CONCEPT 1 — Ohm's Law")
print("=" * 50)

# LED resistor calculation
supply_voltage = 5.0   # Arduino output
led_voltage    = 2.0   # LED forward voltage
led_current    = 0.020 # 20mA in amps

v_resistor = supply_voltage - led_voltage
label, R = ohms_law(V=v_resistor, I=led_current)
print(f"LED circuit: need {label} - {R:.0f} Ohms -> use 220 Ohms (nearest standard)")

# Motor current check
label, I = ohms_law(V=12, R=24)
print(f"Motor at 12V, 24Ω coil: {label} = {I*1000:.0f}mA → needs transistor switch!")


# ─── CONCEPT 2: Voltage Divider + Sensor Simulation ───
def voltage_divider(vcc, r1, r2):
    """Calculate output voltage and Arduino ADC value."""
    vout = vcc * r2 / (r1 + r2)
    adc  = int(vout / vcc * 1023)
    return round(vout, 3), adc

def ldr_resistance(light_percent):
    """
    Simulate LDR resistance based on light level.
    0% = complete darkness (~1MΩ), 100% = bright light (~200Ω)
    Uses logarithmic relationship — real LDRs behave this way.
    """
    min_r, max_r = 200, 1_000_000
    r = max_r * ((100 - light_percent) / 100) ** 3 + min_r
    return int(r)

print("\n" + "=" * 50)
print("CONCEPT 2 — LDR Voltage Divider Simulation")
print("=" * 50)
print(f"{'Light %':<10} {'LDR Ω':<12} {'Vout':<8} {'ADC':<6} {'Condition'}")
print("-" * 50)

light_conditions = [
    (95,  "Bright sunlight"),
    (70,  "Indoor daylight"),
    (50,  "Overcast"),
    (25,  "Dim room"),
    (5,   "Near darkness"),
]

VCC = 5.0
R2_FIXED = 10_000  # 10kΩ fixed resistor

for light_pct, condition in light_conditions:
    r1 = ldr_resistance(light_pct)
    vout, adc = voltage_divider(VCC, r1, R2_FIXED)
    print(f"{light_pct:<10} {r1:<12,} {vout:<8.2f} {adc:<6} {condition}")


# ─── CONCEPT 3: Capacitor RC time constant ───
print("\n" + "=" * 50)
print("CONCEPT 3 — RC Filter for Sensor Noise")
print("=" * 50)

def rc_time_constant(R, C):
    """RC time constant — how fast the capacitor charges."""
    tau = R * C
    cutoff_freq = 1 / (2 * math.pi * tau)
    return tau, cutoff_freq

# Common IoT filter: 10kΩ + 100nF
R = 10_000        # 10kΩ
C = 100e-9        # 100nF
tau, fc = rc_time_constant(R, C)
print(f"R = 10kΩ, C = 100nF")
print(f"Time constant τ = {tau*1000:.2f} ms")
print(f"Cutoff frequency = {fc:.1f} Hz")
print(f"Frequencies above {fc:.1f}Hz are filtered out (noise removed!)")
print(f"Sensor signals below {fc:.1f}Hz pass through cleanly.")


# ─── CONCEPT 4: Transistor switch check ───
print("\n" + "=" * 50)
print("CONCEPT 4 — Transistor Switch Design")
print("=" * 50)

def transistor_switch(load_current_mA, hFE=100, vbe=0.7):
    """
    Calculate base resistor for transistor switch.
    hFE = current gain (100 for 2N2222)
    """
    ic = load_current_mA / 1000  # load current in amps
    ib_needed = ic / hFE         # base current needed
    # Arduino pin outputs 5V, transistor base needs 0.7V
    vr_base = 5.0 - vbe
    r_base = vr_base / (ib_needed * 10)  # 10x overdrive for saturation
    return ib_needed * 1000, r_base

print("Motor load = 500mA, using 2N2222 (hFE=100):")
ib, rb = transistor_switch(500)
print(f"  Base current needed : {ib:.1f} mA")
print(f"  Base resistor       : {rb:.0f}Ω → use 1kΩ standard")
print(f"  Arduino pin current : ~5mA — well within 40mA limit ✓")


# ─── CONCEPT 5: Pull-up vs Pull-down ───
print("\n" + "=" * 50)
print("CONCEPT 5 — Pull-up / Pull-down Resistors")
print("=" * 50)

def simulate_button(has_pulldown, button_pressed, noise_voltage=0.8):
    """
    Show why pull-down resistors are needed.
    Without them, floating pins read random values.
    """
    if not has_pulldown:
        if button_pressed:
            return 5.0, "HIGH", "Button pressed → 5V"
        else:
            # Floating: random noise
            import random
            v = random.uniform(0, 5)
            state = "HIGH" if v > 2.5 else "LOW"
            return round(v, 2), state, "FLOATING — unpredictable!"
    else:
        if button_pressed:
            return 5.0, "HIGH", "Button pressed → 5V"
        else:
            return 0.0, "LOW", "Pull-down holds pin at 0V — stable"

print("WITHOUT pull-down resistor (5 readings when button is open):")
for i in range(5):
    v, state, desc = simulate_button(False, False)
    print(f"  Reading {i+1}: {v}V → {state} ← {desc}")

print("\nWITH 10kΩ pull-down resistor (5 readings when button is open):")
for i in range(5):
    v, state, desc = simulate_button(True, False)
    print(f"  Reading {i+1}: {v}V → {state} ← {desc}")

print("\n" + "=" * 50)
print("SUMMARY — Key values to memorize for IoT")
print("=" * 50)
print("  LED resistor      : 220Ω (5V system)")
print("  Pull-up/down      : 10kΩ")
print("  Decoupling cap    : 100nF ceramic")
print("  Base resistor     : 1kΩ (transistor switch)")
print("  LDR fixed R       : 10kΩ")
print("  Arduino max pin   : 40mA — NEVER exceed this")
print("  Arduino analog    : 0–1023 maps to 0–5V")