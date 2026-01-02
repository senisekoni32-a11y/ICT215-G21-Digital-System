# Smart Dustbin with Raspberry Pi Pico W

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-MicroPython-blue.svg)](https://micropython.org/)
[![Hardware](https://img.shields.io/badge/Hardware-Raspberry%20Pi%20Pico%20W-green.svg)](https://www.raspberrypi.com/products/raspberry-pi-pico/)

IoT-enabled smart waste management system with automatic lid opening, real-time fill monitoring, and web-based dashboard.

**ICT 215 - Robotics and Embedded Systems**  
**Bells University of Technology, Ota, Ogun State**  
**Group 21 | 2025/2026 Session**

---

## Overview

This project implements an affordable smart dustbin using Raspberry Pi Pico W that:
- Opens automatically when approached (contactless operation)
- Monitors waste fill level with ultrasonic sensors (98% accuracy)
- Provides visual indicators (Green/Yellow/Red LEDs)
- Sounds alerts when bin is full (80% threshold)
- Hosts web dashboard for remote monitoring (no cloud subscription needed)

**Total Cost:** ₦8,900 (components) + ₦7,500 (PCB) = ₦16,400

---

## Features

### Hardware
- Automatic lid opening via proximity sensor (30cm trigger distance)
- Real-time fill level monitoring with HC-SR04 ultrasonic sensors
- Three-color LED status system (0-49%: Green, 50-79%: Yellow, 80-100%: Red)
- Audio alerts via active buzzer (5-minute cooldown)
- SG90 servo motor for lid mechanism

### Software
- Web dashboard with live statistics and controls
- WiFi connectivity (local hosting, no subscriptions)
- Automatic reconnection on network dropout
- Error handling and graceful degradation
- Usage tracking (lid openings, last emptied timestamp)

---

## Hardware Requirements

| Component | Qty | Price (₦) | Purpose |
|-----------|-----|-----------|---------|
| Raspberry Pi Pico W | 1 | 3,500 | Main controller |
| HC-SR04 Sensor | 2 | 1,600 | Distance measurement |
| SG90 Servo | 1 | 600 | Lid operation |
| LEDs (3 colors) | 3 | 150 | Status display |
| Active Buzzer | 1 | 200 | Alert |
| Resistors (assorted) | 1 pack | 300 | Current limiting |
| Capacitors | 6 | 200 | Power smoothing |
| Breadboard | 1 | 500 | Prototyping |
| Jumper Wires | 1 set | 400 | Connections |
| 5V 2A Power Supply | 1 | 1,200 | Main power |
| USB Cable | 1 | 250 | Programming |
| **Total** | | **₦8,900** | |

---

## Software Requirements

- **VSCodium IDE** with MicroPython extension
- **MicroPython v1.20+** for Raspberry Pi Pico W
- **Web browser** (Chrome, Firefox, Edge)

### Optional (for circuit design)
- Proteus Design Suite (simulation)
- Tinkercad Circuits (online simulation)
- KiCad (PCB design)

---

## Installation

### 1. Flash MicroPython

1. Download [MicroPython .uf2](https://micropython.org/download/RPI_PICO_W/)
2. Hold **BOOTSEL** button on Pico W
3. Connect USB while holding button
4. Drag .uf2 file to RPI-RP2 drive
5. Pico reboots with MicroPython installed

### 2. Setup VSCodium

1. Install **Pico-W-Go** or **Pymakr** extension in VSCodium
2. Connect Pico W via USB
3. Configure extension to recognize Pico W

### 3. Clone and Upload

```bash
git clone https://github.com/senisekoni32-a11y/ICT215-G21-Digital-System.git
cd ICT215-G21-Digital-System
```

Upload files to Pico W in this order:
1. `config.py` (edit WiFi credentials first)
2. `sensor.py`
3. `actuator.py`
4. `webserver.py`
5. `notification.py`
6. `dashboard.html`
7. `main.py`

### 4. Configure

Edit `config.py`:

```python
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"
BIN_HEIGHT = 40  # Measure your bin in cm
```

### 5. Hardware Connections

**Voltage Dividers (for each HC-SR04 Echo pin):**
```
Echo → [2kΩ] → Junction → [1kΩ] → GND
                  ↓
              Pico GPIO
```

**Pin Mapping:**

| Component | Pico Pin |
|-----------|----------|
| Lid Sensor Trig | GP2 |
| Lid Sensor Echo | GP3 (via divider) |
| Fill Sensor Trig | GP4 |
| Fill Sensor Echo | GP5 (via divider) |
| Servo | GP15 |
| Green LED | GP16 (+ 220Ω) |
| Yellow LED | GP17 (+ 220Ω) |
| Red LED | GP18 (+ 220Ω) |
| Buzzer | GP19 |

---

## Usage

1. Power on system
2. Wait for WiFi connection (Green LED blinks 3× on success)
3. Note IP address from serial console
4. Open browser to `http://[IP-ADDRESS]`
5. Monitor fill level via dashboard
6. Lid opens automatically when approached

---

## Project Structure

```
ICT215-G21-Digital-System/
├── main.py              # Main program
├── config.py            # Settings
├── sensor.py            # Sensor functions
├── actuator.py          # Servo/LED/buzzer
├── webserver.py         # Web server
├── notification.py      # Alerts
├── dashboard.html       # Web interface
├── simulations/         # Proteus & Tinkercad
├── pcb/                 # KiCad files & Gerber
└── README.md            # This file
```

---

## Team Members

| Name | Matric No. | Role |
|------|-----------|------|
| ESEURHIE OGHENOCHUKO HANSEL | 2025/14498 | Circuit Design & PCB |
| BAMIDELE OLAMIDE EMMANUEL | 2025/14550 | Sensor/Actuator Software |
| OLAKUNLE OLUWAKOREDE GABRIEL | 2025/14626 | Web Development |
| SEKONI FAITH OLUWASENI | 2025/14581 | Hardware & Testing |
| YEMITAN OLUWATAMILORE JONATHAN | 2025/14520 | Coordination & Documentation |

**Supervisor:** Mr Ayuba Mohammed  
**Institution:** Bells University of Technology  
**Department:** Mechatronics Engineering

---

## Testing Results

- **Sensor Accuracy:** 97.8% (±2.2% average error)
- **Response Time:** 0.8 seconds (lid opening)
- **WiFi Range:** 15 meters (reliable)
- **Uptime:** 24 hours continuous operation (no failures)
- **Power Consumption:** 3.5W average

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| WiFi fails | Check SSID/password, use 2.4GHz network |
| Lid won't open | Verify servo connections, check 5V supply |
| Wrong fill readings | Ensure sensor faces down, update BIN_HEIGHT |
| Dashboard won't load | Confirm IP address, check firewall |

---

## References

1. Arebey, M., et al. (2021). "Solid Waste Bin Level Detection." *Journal of Environmental Management*, 290, 112-128.
2. Federal Ministry of Environment (2020). "National Policy on Solid Waste Management." Government of Nigeria.
3. Kumar, N. S., et al. (2016). "IOT Based Smart Garbage Alert System." *IEEE Conference*, 1-4.
4. Raspberry Pi Foundation (2023). "Raspberry Pi Pico W Datasheet."

Full references in project report.

---

## Contact

**GitHub:** https://github.com/senisekoni32-a11y/ICT215-G21-Digital-System   
**Institution:** Bells University of Technology, Ota, Ogun State

---

**Group 21 | ICT 215 | Bells University of Technology | 2025/2026**
