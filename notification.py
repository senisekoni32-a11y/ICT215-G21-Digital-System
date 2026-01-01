# Notification system

import time

class NotificationManager:
    def __init__(self, buzzer_controller, led_controller, alert_cooldown=300):
        self.buzzer = buzzer_controller
        self.leds = led_controller
        self.last_alert_time = 0
        self.alert_cooldown = alert_cooldown
        self.alert_active = False
    
    def check_and_alert(self, fill_percentage, threshold):
        """Check if alert needed and trigger if appropriate"""
        current_time = time.time()
        
        if fill_percentage >= threshold:
            if current_time - self.last_alert_time > self.alert_cooldown:
                self._trigger_full_alert()
                self.last_alert_time = current_time
                self.alert_active = True
                return True
        else:
            self.alert_active = False
        
        return False
    
    def _trigger_full_alert(self):
        """Trigger full bin alert"""
        try:
            print("ALERT: Bin is full!")
            self.buzzer.alert(3)
            self.leds.blink('red', 5, 0.3)
        except Exception as e:
            print(f"Alert error: {e}")
    
    def reset_alert(self):
        """Manually reset alert timer"""
        self.last_alert_time = 0
        self.alert_active = False
    
    def set_cooldown(self, seconds):
        """Set custom alert cooldown period"""
        if seconds > 0:
            self.alert_cooldown = seconds
