import time

from IntelligentOfficeError import IntelligentOfficeError
import mock.GPIO as GPIO
from mock.RTC import RTC


class IntelligentOffice:
    # Pin number definition
    INFRARED_PIN = 11
    RTC_PIN = 16
    SERVO_PIN = 18
    PHOTO_PIN = 22  # photoresistor
    LED_PIN = 29
    CO2_PIN = 31
    FAN_PIN = 32

    LUX_MIN = 500
    LUX_MAX = 550

    DC_OPEN = (180 / 18) + 2
    DC_CLOSED = (0 / 18) + 2

    def __init__(self):
        """
        Constructor
        """
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.INFRARED_PIN, GPIO.IN)
        GPIO.setup(self.PHOTO_PIN, GPIO.IN)
        GPIO.setup(self.SERVO_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)
        GPIO.setup(self.CO2_PIN, GPIO.IN)
        GPIO.setup(self.FAN_PIN, GPIO.OUT)

        self.rtc = RTC(self.RTC_PIN)
        self.pwm = GPIO.PWM(self.SERVO_PIN, 50)
        self.pwm.start(0)

        self.blinds_open = False
        self.light_on = False
        self.fan_switch_on = False

    def check_occupancy(self) -> bool:
        """
        Checks if the infrared distance sensor on the ceiling detects something in front of it.
        :param pin: The data pin of the sensor that is being checked (e.g., INFRARED_PIN1).
        :return: True if the infrared sensor detects something, False otherwise.
        """
        result = GPIO.input(self.INFRARED_PIN)
        if result == 0:
            return True
        else:
            return False

    def manage_blinds_based_on_time(self) -> None:
        """
        Uses the RTC and servo motor to open/close the blinds based on current time and day.
        The system fully opens the blinds at 8:00 and fully closes them at 20:00
        each day except for Saturday and Sunday.
        """
        current_time = time.strptime(RTC.get_current_time_string(), "%H:%M:%S")
        hour = current_time.tm_hour
        minutes = current_time.tm_min
        sec = current_time.tm_sec
        day = RTC.get_current_day()

        if day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
            if hour == 8 and minutes == 0 and sec == 0:
                self.change_servo_angle(self.DC_OPEN)
                self.blinds_open = True
            elif hour == 20 and minutes == 0 and sec == 0:
                self.change_servo_angle(self.DC_CLOSED)
                self.blinds_open = False
        elif day in ["SATURDAY", "SUNDAY"]:
            pass
        else:
            raise IntelligentOfficeError

    def manage_light_level(self) -> None:
        """
        Tries to maintain the actual light level inside the office, measure by the photoresistor,
        between LUX_MIN and LUX_MAX.
        If the actual light level is lower than LUX_MIN the system turns on the smart light bulb.
        On the other hand, if the actual light level is greater than LUX_MAX, the system turns off the smart light bulb.

        Furthermore, When the worker leaves the office (i.e., the office is now vacant), the intelligent office system
        stops regulating the light level in the office and then turns off the smart light bulb.
        When the worker goes back into the office, the system resumes regulating the light level
        """
        if self.check_occupancy():
            light_level = GPIO.input(self.PHOTO_PIN)
            if light_level < self.LUX_MIN:
                self.turn_on_light()
            elif light_level > self.LUX_MAX:
                self.turn_off_light()
        else:
            self.turn_off_light()

    def turn_on_light(self) -> None:
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        self.light_on = True

    def turn_off_light(self) -> None:
        GPIO.output(self.LED_PIN, GPIO.LOW)
        self.light_on = False

    def monitor_air_quality(self) -> None:
        """
        Use the carbon dioxide sensor to monitor the level of CO2 in the office.
        If the amount of detected CO2 is greater than or equal to 800 PPM, the system turns on the
        switch of the exhaust fan until the amount of CO2 is lower than 500 PPM.
        """
        c02_level = GPIO.input(self.CO2_PIN)
        if c02_level >= 800:
            GPIO.output(self.FAN_PIN, GPIO.HIGH)
            self.fan_switch_on = True
        elif c02_level < 500:
            GPIO.output(self.FAN_PIN, GPIO.LOW)
            self.fan_switch_on = False

    def change_servo_angle(self, duty_cycle: float) -> None:
        """
        Changes the servo motor's angle by passing to it the corresponding PWM duty cycle signal
        :param duty_cycle: the length of the duty cycle
        """
        GPIO.output(self.SERVO_PIN, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)
        GPIO.output(self.SERVO_PIN, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
