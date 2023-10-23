import unittest
from unittest.mock import patch
import mock.GPIO as GPIO
from mock.RTC import RTC
from IntelligentOffice import IntelligentOffice
from IntelligentOfficeError import IntelligentOfficeError


class IntelligentOfficeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.int_off = IntelligentOffice()

    @patch.object(GPIO, "input")
    def test_object_not_detected_infrared(self, mock_input):
        # Non-zero value -> nothing is detected in front of the sensor
        mock_input.return_value = 1337
        is_occupied = self.int_off.check_occupancy()
        self.assertEqual(False, is_occupied)

    @patch.object(GPIO, "input")
    def test_object_detected_infrared(self, mock_input):
        # Zero value -> something is in front of the sensor
        mock_input.return_value = 0
        is_occupied = self.int_off.check_occupancy()
        self.assertEqual(True, is_occupied)

