Smart Dustbin with Raspberry Pi Pico

## Project Overview
An IoT-enabled smart dustbin that automatically opens its lid when someone approaches and monitors waste levels in real-time. The system sends notifications when the bin is full and provides usage statistics through a web interface, making waste management more hygienic and efficient.

## Features
- Automatic Lid Control: Ultrasonic sensor detects approaching users and triggers servo motor to open/close the lid
- Fill Level Monitoring: Real-time tracking of dustbin capacity using ultrasonic distance measurement
- WiFi Connectivity: Connects to local network for remote monitoring and notifications
- Web Dashboard: View current fill level and usage statistics through a simple web interface
- Smart Notifications: Alerts when bin reaches 80% capacity
- Low Power Mode: Automatic sleep mode during inactivity to conserve energy
- LED Status Indicators: Visual feedback for system status and fill levels

## Hardware Components

| Component | Specification | Quantity | Purpose |
|-----------|--------------|----------|---------|
| Raspberry Pi Pico W | RP2040 with WiFi | 1 | Main microcontroller |
| HC-SR04 Ultrasonic Sensor | 2-400cm range | 2 | Lid trigger & fill detection |
| SG90 Micro Servo Motor | 180° rotation | 1 | Lid actuation |
| LEDs | 5mm (Red, Yellow, Green) | 3 | Status indicators |
| Resistors | 220Ω | 3 | LED current limiting |
| Buzzer | 5V Active | 1 | Audio alerts |
| Breadboard | 830 points | 1 | Prototyping |
| Jumper Wires | Male-to-Male/Female | 20+ | Connections |
| Power Supply | 5V 2A USB | 1 | Power source |
| Dustbin | Medium size | 1 | Physical enclosure |

## Circuit Diagram

```
Raspberry Pi Pico W Pin Connections:

Lid Sensor (HC-SR04 #1):
- VCC → VBUS (5V)
- GND → GND
- Trig → GP2
- Echo → GP3

Fill Sensor (HC-SR04 #2):
- VCC → VBUS (5V)
- GND → GND
- Trig → GP4
- Echo → GP5

Servo Motor:
- Red (VCC) → VBUS (5V)
- Brown (GND) → GND
- Orange (Signal) → GP15

LEDs:
- Green LED → GP16 → 220Ω → GND (Normal status)
- Yellow LED → GP17 → 220Ω → GND (Half full)
- Red LED → GP18 → 220Ω → GND (Full)

Buzzer:
- Positive → GP19
- Negative → GND

## Software Architecture

### Technology Stack
- Language: MicroPython 1.20+
- Python Libraries: 
  - `machine` - Hardware control (GPIO, PWM, Timer)
  - `network` - WiFi connectivity
  - `socket` - Web server functionality
  - `time` - Timing and delays
  - `urequests` - HTTP requests (optional for external APIs)

### Code Structure

smart-dustbin/
│
├── main.py                 # Main program loop
├── config.py              # WiFi credentials and settings
├── sensors.py             # Ultrasonic sensor functions
├── actuators.py           # Servo and LED control
├── web_server.py          # HTTP server for dashboard
├── notifications.py       # Alert system
└── README.md              # This file
```

### Program Flow
1. Initialize hardware (sensors, servo, LEDs, WiFi)
2. Connect to WiFi network and start web server
3. Continuous monitoring loop:
   - Check lid sensor for approaching user
   - If detected, open lid for 5 seconds
   - Monitor fill level sensor
   - Update LED indicators based on fill percentage
   - Send notifications if threshold exceeded
4. Handle web requests for dashboard access

## Setup Instructions

### 1. Flash MicroPython to Pico W
- Download the latest MicroPython UF2 file for Pico W from [micropython.org](https://micropython.org/download/rp2-pico-w/)
- Hold the BOOTSEL button on Pico W and connect it via USB
- Drag and drop the UF2 file to the RPI-RP2 drive
- The Pico W will reboot with MicroPython installed

### 2. Assemble Hardware
- Follow the circuit diagram above to connect all components
- Ensure proper polarity for LEDs and buzzer
- Secure the ultrasonic sensors: one near the lid opening area, one at the top inside the bin pointing downward
- Mount the servo motor to the lid mechanism

### 3. Configure Software
- Clone this repository or download the project files
- Edit `config.py` and add your WiFi credentials:
```python
WIFI_SSID = "SheykonieRPW"
WIFI_PASSWORD = "s3k0n1"
BIN_HEIGHT = 40  # Height of bin in cm
```

### 4. Upload Code to Pico W
- Use Thonny IDE or similar tool to connect to the Pico W
- Upload all Python files to the Pico W
- Ensure `main.py` is present (runs automatically on boot)

### 5. Power On and Test
- Connect power supply
- Wait for WiFi connection (green LED blinks during connection)
- Check serial monitor for IP address
- Access web dashboard at `http://<PICO_IP_ADDRESS>`

## Usage

### Basic Operation
1. Power on the smart dustbin
2. Wait for the green status LED to stop blinking (WiFi connected)
3. Approach the bin - lid opens automatically
4. Dispose waste and move away - lid closes after 5 seconds
5. Monitor fill level via LED indicators:
   - Green: 0-50% full
   - Yellow: 50-80% full
   - Red: 80-100% full (buzzer sounds)

### Web Dashboard
Access the dashboard by entering the Pico W's IP address in a web browser:
- View current fill percentage
- See total number of lid openings
- Check last emptied timestamp
- View real-time sensor readings

## Code Example
Python
# main.py snippet
from machine import Pin, PWM
import time
from sensors import get_distance
from actuators import open_lid, close_lid, update_leds

lid_sensor_trig = Pin(2, Pin.OUT)
lid_sensor_echo = Pin(3, Pin.IN)

while True:
    distance = get_distance(lid_sensor_trig, lid_sensor_echo)
    
    if distance < 30:  # User within 30cm
        open_lid()
        time.sleep(5)
        close_lid()
    
    fill_level = check_fill_level()
    update_leds(fill_level)
    
    time.sleep(0.1)
```

## Future Improvements
- Solar Power: Add solar panel for outdoor/off-grid operation
- Mobile App: Develop companion app for Android/iOS
- Multiple Compartments: Separate bins for recycling, compost, and waste
- Weight Sensors: Add load cells for more accurate fill detection
- Voice Feedback: Audio prompts for user guidance
- Cloud Integration: Store data on cloud platform for analytics
- Machine Learning: Predict when bin will be full based on usage patterns
- RFID Access: Track which users are disposing waste
- Odor Detection: Gas sensor to detect unpleasant smells

## Troubleshooting

Problem: Lid doesn't open when approaching?
- Check ultrasonic sensor connections (Trig and Echo pins)
- Verify sensor is positioned correctly and not obstructed
- Adjust detection distance threshold in code

Problem: WiFi won't connect?
- Double-check SSID and password in `config.py`
- Ensure 2.4GHz network (Pico W doesn't support 5GHz)
- Move closer to router or reduce interference

Problem: Servo jitters or doesn't move?
- Ensure adequate power supply (5V 2A minimum)
- Check servo signal wire connection to GP15
- Test servo separately to verify it's functional

Problem: Inaccurate fill level readings?
- Clean ultrasonic sensors (dust can interfere)
- Calibrate `BIN_HEIGHT` value in `config.py`
- Ensure sensor is mounted vertically inside bin

Problem: Web dashboard not loading?
- Verify Pico W is connected to WiFi (check serial output)
- Confirm you're on the same network
- Try accessing via IP address shown in serial monitor

## Demo
*Insert photos and video links here*
- Image 1: Complete assembled circuit
- Image 2: Lid opening mechanism
- Image 3: Web dashboard screenshot
- Video: [Demo video link]

## Project Team
- Sekoni F. Oluwaseni(2025/14581), Yemitan Oluwatamilore Jonathan(2025/14520) - Hardware & Software Development
- Eseurhuie Ogheneochuko Hansel(2025/14498), Olakunle Oluwakorede Gabriel(2025/14626) - Circuit Design & Testing
- Bamidele Olamide Emmanuel(2025/14550)- Documentation & Presentation

## Timeline
- Day 1-6: Component procurement and initial research
- Week 2: Circuit design and prototype assembly
- Week 3-4: Software development and sensor calibration
- Week 5: WiFi integration and web dashboard
- Week 5 cont'd: Testing, debugging, and documentation

## References
1. Raspberry Pi Pico W Datasheet: https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf
2. HC-SR04 Ultrasonic Sensor Tutorial: https://www.micropython.org/
3. MicroPython Documentation: https://docs.micropython.org/
4. Servo Motor Control with PWM: https://projects-raspberry.com/servo-motor-with-raspberry-pi-and-pwm/
5. IoT Waste Management Systems - Research Paper: https://www.laujet.com/conference/2025/docs/LAUFET_15_2025.pdf

## License
This project is open-source and available under the MIT License.

## Acknowledgments
Special thanks to our project supervisor, Mr Ayuba Mohammed, for guidance and the university for providing prerequisite MCU and Proteus usage learning facilities.

Project Year: 2025/2026 200LEVEL 
Course: ICT215-ROBOTICS  
Institution: BELLS UNIVERSITY OF TECHNOLOGY.
