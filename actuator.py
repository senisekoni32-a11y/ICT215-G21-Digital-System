# Actuator control (servo, LEDs, buzzer)

from machine import Pin, PWM
import time

try:
    from config import SERVO_FREQ, SERVO_CLOSED_DUTY, SERVO_OPEN_DUTY
except ImportError:
    SERVO_FREQ = 50
    SERVO_CLOSED_DUTY = 1500
    SERVO_OPEN_DUTY = 7500

class ServoController:
    def __init__(self, pin):
        self.servo = PWM(Pin(pin))
        self.servo.freq(SERVO_FREQ)
        self.is_open = False
        self.close_lid()
    
    def open_lid(self):
        self.servo.duty_u16(SERVO_OPEN_DUTY)
        self.is_open = True
    
    def close_lid(self):
        self.servo.duty_u16(SERVO_CLOSED_DUTY)
        self.is_open = False
    
    def deinit(self):
        self.servo.deinit()

class LEDController:
    def __init__(self, green_pin, yellow_pin, red_pin):
        self.green = Pin(green_pin, Pin.OUT)
        self.yellow = Pin(yellow_pin, Pin.OUT)
        self.red = Pin(red_pin, Pin.OUT)
        self.all_off()
    
    def all_off(self):
        self.green.off()
        self.yellow.off()
        self.red.off()
    
    def update_status(self, fill_percentage, half_thresh=50, full_thresh=80):
        self.all_off()
        if fill_percentage >= full_thresh:
            self.red.on()
        elif fill_percentage >= half_thresh:
            self.yellow.on()
        else:
            self.green.on()
    
    def blink(self, led_color, times=3, delay=0.2):
        led = getattr(self, led_color.lower())
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
        self.buzzer.on()
        time.sleep(duration)
        self.buzzer.off()
    
    def alert(self, times=3):
        for _ in range(times):
            self.beep(0.1)
            time.sleep(0.1)
    
    def off(self):
        self.buzzer.off()
