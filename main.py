# Main program

from machine import Pin
import time
import network
import config
from sensor import init_sensors, get_distance, calculate_fill_percentage
from actuator import ServoController, LEDController, BuzzerController
from webserver import WebServer
from notification import NotificationManager

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
            
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            servo.close_lid()
            leds.all_off()
            buzzer.off()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
