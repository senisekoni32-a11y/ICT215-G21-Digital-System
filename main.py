# ============================================
# config.py
# ============================================
# Configuration file for Smart Dustbin

# WiFi Credentials
WIFI_SSID = "YourNetworkName"
WIFI_PASSWORD = "YourPassword"

# Bin Settings
BIN_HEIGHT = 40  # Height of bin in cm
FULL_THRESHOLD = 80  # Percentage to trigger full alert
HALF_THRESHOLD = 50  # Percentage for half full warning

# Sensor Settings
LID_TRIGGER_DISTANCE = 30  # Distance in cm to trigger lid opening
LID_OPEN_TIME = 5  # Seconds to keep lid open
SENSOR_TIMEOUT = 30000  # Ultrasonic timeout in microseconds

# Pin Assignments
LID_SENSOR_TRIG = 2
LID_SENSOR_ECHO = 3
FILL_SENSOR_TRIG = 4
FILL_SENSOR_ECHO = 5
SERVO_PIN = 15
LED_GREEN = 16
LED_YELLOW = 17
LED_RED = 18
BUZZER_PIN = 19

# Servo Settings
SERVO_FREQ = 50  # Frequency in Hz
SERVO_CLOSED_DUTY = 2500  # Duty cycle for closed position
SERVO_OPEN_DUTY = 7500  # Duty cycle for open position


# ============================================
# sensors.py
# ============================================
# Sensor control functions

from machine import Pin, time_pulse_us
import time
from config import SENSOR_TIMEOUT

def get_distance(trig_pin, echo_pin):
    """
    Measure distance using HC-SR04 ultrasonic sensor
    Returns distance in cm, or -1 if timeout/error
    """
    # Send trigger pulse
    trig_pin.low()
    time.sleep_us(2)
    trig_pin.high()
    time.sleep_us(10)
    trig_pin.low()
    
    try:
        # Measure echo pulse duration
        pulse_time = time_pulse_us(echo_pin, 1, SENSOR_TIMEOUT)
        
        if pulse_time < 0:
            return -1  # Timeout occurred
        
        # Calculate distance (speed of sound = 343 m/s)
        distance = (pulse_time / 2) / 29.1
        
        return distance
    except:
        return -1

def init_sensors(lid_trig, lid_echo, fill_trig, fill_echo):
    """
    Initialize ultrasonic sensors
    Returns tuple of (lid_trig, lid_echo, fill_trig, fill_echo) pin objects
    """
    lid_trig_pin = Pin(lid_trig, Pin.OUT)
    lid_echo_pin = Pin(lid_echo, Pin.IN)
    fill_trig_pin = Pin(fill_trig, Pin.OUT)
    fill_echo_pin = Pin(fill_echo, Pin.IN)
    
    # Initialize trigger pins to low
    lid_trig_pin.low()
    fill_trig_pin.low()
    
    return lid_trig_pin, lid_echo_pin, fill_trig_pin, fill_echo_pin

def calculate_fill_percentage(distance, bin_height):
    """
    Calculate fill percentage based on distance measurement
    """
    if distance <= 0 or distance > bin_height:
        return 0
    
    fill_percentage = ((bin_height - distance) / bin_height) * 100
    return max(0, min(100, fill_percentage))  # Clamp between 0-100


# ============================================
# actuators.py
# ============================================
# Actuator control (servo, LEDs, buzzer)

from machine import Pin, PWM
import time
from config import SERVO_FREQ, SERVO_CLOSED_DUTY, SERVO_OPEN_DUTY

class ServoController:
    def __init__(self, pin):
        self.servo = PWM(Pin(pin))
        self.servo.freq(SERVO_FREQ)
        self.is_open = False
        self.close_lid()
    
    def open_lid(self):
        """Open the dustbin lid"""
        self.servo.duty_u16(SERVO_OPEN_DUTY)
        self.is_open = True
        print("Lid opened")
    
    def close_lid(self):
        """Close the dustbin lid"""
        self.servo.duty_u16(SERVO_CLOSED_DUTY)
        self.is_open = False
        print("Lid closed")
    
    def deinit(self):
        """Disable servo to save power"""
        self.servo.deinit()

class LEDController:
    def __init__(self, green_pin, yellow_pin, red_pin):
        self.green = Pin(green_pin, Pin.OUT)
        self.yellow = Pin(yellow_pin, Pin.OUT)
        self.red = Pin(red_pin, Pin.OUT)
        self.all_off()
    
    def all_off(self):
        """Turn off all LEDs"""
        self.green.off()
        self.yellow.off()
        self.red.off()
    
    def update_status(self, fill_percentage, half_thresh, full_thresh):
        """Update LED status based on fill level"""
        self.all_off()
        
        if fill_percentage >= full_thresh:
            self.red.on()
        elif fill_percentage >= half_thresh:
            self.yellow.on()
        else:
            self.green.on()
    
    def blink(self, led_color, times=3, delay=0.2):
        """Blink specified LED"""
        led = getattr(self, led_color)
        for _ in range(times):
            led.on()
            time.sleep(delay)
            led.off()
            time.sleep(delay)

class BuzzerController:
    def __init__(self, pin):
        self.buzzer = Pin(pin, Pin.OUT)
        self.buzzer.off()
    
    def beep(self, duration=0.2):
        """Single beep"""
        self.buzzer.on()
        time.sleep(duration)
        self.buzzer.off()
    
    def alert(self, times=3):
        """Multiple beeps for alert"""
        for _ in range(times):
            self.beep(0.1)
            time.sleep(0.1)


# ============================================
# web_server.py
# ============================================
# Simple web server for dashboard

import socket
import json

class WebServer:
    def __init__(self, port=80):
        self.port = port
        self.sock = None
        self.stats = {
            'fill_percentage': 0,
            'lid_openings': 0,
            'last_emptied': 'Never',
            'status': 'OK'
        }
    
    def start(self):
        """Start the web server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))
        self.sock.listen(1)
        self.sock.setblocking(False)
        print(f"Web server started on port {self.port}")
    
    def update_stats(self, fill_percentage, lid_openings, status):
        """Update statistics"""
        self.stats['fill_percentage'] = round(fill_percentage, 1)
        self.stats['lid_openings'] = lid_openings
        self.stats['status'] = status
    
    def handle_request(self):
        """Handle incoming HTTP requests (non-blocking)"""
        try:
            conn, addr = self.sock.accept()
            conn.settimeout(1.0)
            request = conn.recv(1024).decode()
            
            if 'GET / ' in request or 'GET /index' in request:
                response = self._generate_html()
            elif 'GET /api/stats' in request:
                response = self._generate_json()
            else:
                response = self._generate_404()
            
            conn.send(response.encode())
            conn.close()
        except OSError:
            pass  # No connection available, continue
        except Exception as e:
            print(f"Server error: {e}")
    
    def _generate_html(self):
        """Generate HTML dashboard"""
        fill = self.stats['fill_percentage']
        color = 'green' if fill < 50 else 'orange' if fill < 80 else 'red'
        
        html = f"""HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Smart Dustbin Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: Arial; text-align: center; margin: 50px; background: #f0f0f0; }}
        .container {{ max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .title {{ color: #333; }}
        .fill-bar {{ width: 100%; height: 40px; background: #ddd; border-radius: 20px; overflow: hidden; margin: 20px 0; }}
        .fill-level {{ height: 100%; background: {color}; transition: width 0.3s; }}
        .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .stat-box {{ padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .stat-label {{ font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="title">🗑️ Smart Dustbin</h1>
        <h2 style="color: {color};">{fill}% Full</h2>
        <div class="fill-bar">
            <div class="fill-level" style="width: {fill}%;"></div>
        </div>
        <div class="stats">
            <div class="stat-box">
                <div class="stat-value">{self.stats['lid_openings']}</div>
                <div class="stat-label">Lid Openings</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{self.stats['status']}</div>
                <div class="stat-label">Status</div>
            </div>
        </div>
        <p>Last Emptied: {self.stats['last_emptied']}</p>
        <p><small>Auto-refreshes every 5 seconds</small></p>
    </div>
</body>
</html>
"""
        return html
    
    def _generate_json(self):
        """Generate JSON API response"""
        response = f"""HTTP/1.1 200 OK
Content-Type: application/json

{json.dumps(self.stats)}
"""
        return response
    
    def _generate_404(self):
        """Generate 404 response"""
        return "HTTP/1.1 404 Not Found\n\nPage not found"


# ============================================
# notifications.py
# ============================================
# Notification system

import time

class NotificationManager:
    def __init__(self, buzzer_controller, led_controller):
        self.buzzer = buzzer_controller
        self.leds = led_controller
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5 minutes between alerts
    
    def check_and_alert(self, fill_percentage, threshold):
        """Check if alert needed and trigger if appropriate"""
        current_time = time.time()
        
        if fill_percentage >= threshold:
            # Only alert if cooldown period has passed
            if current_time - self.last_alert_time > self.alert_cooldown:
                self._trigger_full_alert()
                self.last_alert_time = current_time
                return True
        return False
    
    def _trigger_full_alert(self):
        """Trigger full bin alert"""
        print("ALERT: Bin is full!")
        self.buzzer.alert(3)
        self.leds.blink('red', 5, 0.3)


# ============================================
# main.py
# ============================================
# Main program

from machine import Pin
import time
import network
import config
from sensors import init_sensors, get_distance, calculate_fill_percentage
from actuators import ServoController, LEDController, BuzzerController
from web_server import WebServer
from notifications import NotificationManager

# Global statistics
lid_openings = 0
last_lid_open_time = 0

def connect_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to {config.WIFI_SSID}...")
        wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            print("WiFi connected!")
            print(f"IP Address: {wlan.ifconfig()[0]}")
            return True
        else:
            print("WiFi connection failed")
            return False
    return True

def main():
    global lid_openings, last_lid_open_time
    
    print("Initializing Smart Dustbin...")
    
    # Initialize sensors
    lid_trig, lid_echo, fill_trig, fill_echo = init_sensors(
        config.LID_SENSOR_TRIG,
        config.LID_SENSOR_ECHO,
        config.FILL_SENSOR_TRIG,
        config.FILL_SENSOR_ECHO
    )
    
    # Initialize actuators
    servo = ServoController(config.SERVO_PIN)
    leds = LEDController(config.LED_GREEN, config.LED_YELLOW, config.LED_RED)
    buzzer = BuzzerController(config.BUZZER_PIN)
    
    # Initialize notification manager
    notifier = NotificationManager(buzzer, leds)
    
    # Connect to WiFi and start web server
    wifi_connected = connect_wifi()
    web_server = None
    
    if wifi_connected:
        web_server = WebServer()
        web_server.start()
        leds.blink('green', 3)
    else:
        leds.blink('red', 3)
    
    print("Smart Dustbin ready!")
    buzzer.beep()
    
    # Main loop
    while True:
        try:
            # Check for approaching user
            lid_distance = get_distance(lid_trig, lid_echo)
            
            if lid_distance > 0 and lid_distance < config.LID_TRIGGER_DISTANCE:
                current_time = time.time()
                # Prevent multiple triggers in short time
                if current_time - last_lid_open_time > 2:
                    servo.open_lid()
                    lid_openings += 1
                    last_lid_open_time = current_time
                    buzzer.beep(0.1)
                    time.sleep(config.LID_OPEN_TIME)
                    servo.close_lid()
            
            # Check fill level
            fill_distance = get_distance(fill_trig, fill_echo)
            fill_percentage = calculate_fill_percentage(fill_distance, config.BIN_HEIGHT)
            
            # Update LED status
            leds.update_status(fill_percentage, config.HALF_THRESHOLD, config.FULL_THRESHOLD)
            
            # Check for full bin alert
            notifier.check_and_alert(fill_percentage, config.FULL_THRESHOLD)
            
            # Update web server stats
            if web_server:
                status = "FULL" if fill_percentage >= config.FULL_THRESHOLD else "OK"
                web_server.update_stats(fill_percentage, lid_openings, status)
                web_server.handle_request()
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            servo.close_lid()
            leds.all_off()
            buzzer.buzzer.off()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()