# Sensor control functions

from machine import Pin, time_pulse_us
import time

try:
    from config import SENSOR_TIMEOUT
except ImportError:
    SENSOR_TIMEOUT = 30000

def get_distance(trig_pin, echo_pin, timeout=None):
    """Measure distance using HC-SR04 ultrasonic sensor"""
    if timeout is None:
        timeout = SENSOR_TIMEOUT
    
    try:
        trig_pin.low()
        time.sleep_us(2)
        trig_pin.high()
        time.sleep_us(10)
        trig_pin.low()
        
        pulse_time = time_pulse_us(echo_pin, 1, timeout)
        
        if pulse_time < 0:
            return -1
        
        distance = (pulse_time / 2) / 29.1
        
        if distance > 400:
            return -1
        
        return round(distance, 2)
        
    except Exception as e:
        print(f"Distance measurement error: {e}")
        return -1

def init_sensors(lid_trig, lid_echo, fill_trig, fill_echo):
    """Initialize ultrasonic sensors"""
    try:
        lid_trig_pin = Pin(lid_trig, Pin.OUT)
        lid_echo_pin = Pin(lid_echo, Pin.IN)
        fill_trig_pin = Pin(fill_trig, Pin.OUT)
        fill_echo_pin = Pin(fill_echo, Pin.IN)
        
        lid_trig_pin.low()
        fill_trig_pin.low()
        
        time.sleep_ms(100)
        
        print(f"Sensors initialized: Lid(Trig={lid_trig}, Echo={lid_echo}), "
              f"Fill(Trig={fill_trig}, Echo={fill_echo})")
        
        return lid_trig_pin, lid_echo_pin, fill_trig_pin, fill_echo_pin
        
    except Exception as e:
        print(f"Sensor initialization failed: {e}")
        raise

def calculate_fill_percentage(distance, bin_height):
    """Calculate fill percentage based on distance measurement"""
    if distance <= 0:
        return 0
    
    if distance > bin_height:
        return 0
    
    fill_percentage = ((bin_height - distance) / bin_height) * 100
    
    return round(max(0, min(100, fill_percentage)), 1)
