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

    @patch.object(RTC, "get_current_day")
    @patch.object(RTC, "get_current_time_string")
    def test_open_blinds_on_working_day(self, mock_time, mock_day):
        mock_time.return_value = "08:00:00"
        mock_day.return_value = "MONDAY"
        self.int_off.manage_blinds_based_on_time()
        self.assertEqual(True, self.int_off.blinds_open)

    @patch.object(RTC, "get_current_day")
    @patch.object(RTC, "get_current_time_string")
    def test_close_blinds_on_working_day(self, mock_time, mock_day):
        mock_time.return_value = "20:00:00"
        mock_day.return_value = "WEDNESDAY"
        self.int_off.manage_blinds_based_on_time()
        self.assertEqual(False, self.int_off.blinds_open)

    @patch.object(RTC, "get_current_day")
    @patch.object(RTC, "get_current_time_string")
    def test_open_blinds_on_non_working_day(self, mock_time, mock_day):
        mock_time.return_value = "08:00:00"
        mock_day.return_value = "SUNDAY"
        self.int_off.manage_blinds_based_on_time()
        self.assertEqual(False, self.int_off.blinds_open)

    @patch.object(RTC, "get_current_day")
    @patch.object(RTC, "get_current_time_string")
    def test_close_blinds_on_non_working_day(self, mock_time, mock_day):
        mock_time.return_value = "20:00:00"
        mock_day.return_value = "SATURDAY"
        self.int_off.manage_blinds_based_on_time()
        self.assertEqual(False, self.int_off.blinds_open)

    @patch.object(GPIO, "input")
    def test_low_light_level_with_office_worker(self, mock_input):
        # 0 -> someone is in the office
        # 450 -> the light level is too low
        mock_input.side_effect = [0, 450]
        self.int_off.manage_light_level()
        self.assertEqual(True, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_low_light_level_with_no_office_worker(self, mock_input):
        # 100 -> no one is in the office
        # 450 -> the light level is too low
        mock_input.side_effect = [100, 450]
        self.int_off.manage_light_level()
        self.assertEqual(False, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_high_light_level_with_office_worker(self, mock_input):
        # 0 -> someone is in the office
        # 600 -> the light level is too high
        mock_input.side_effect = [0, 600]
        self.int_off.manage_light_level()
        self.assertEqual(False, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_high_light_level_with_no_office_worker(self, mock_input):
        # 100 -> no one is in the office
        # 600 -> the light level is too high
        mock_input.side_effect = [100, 600]
        self.int_off.manage_light_level()
        self.assertEqual(False, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_light_level_from_600_to_525_with_office_worker(self, mock_input):
        mock_input.side_effect = [0, 600, 0, 525]
        self.int_off.manage_light_level()
        self.int_off.manage_light_level()
        self.assertEqual(False, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_light_level_from_600_to_525_and_office_worker_leaves(self, mock_input):
        mock_input.side_effect = [0, 600, 100, 525]
        self.int_off.manage_light_level()
        self.int_off.manage_light_level()
        self.assertEqual(False, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_light_level_from_450_to_525_with_office_worker(self, mock_input):
        mock_input.side_effect = [0, 450, 0, 525]
        self.int_off.manage_light_level()
        self.int_off.manage_light_level()
        self.assertEqual(True, self.int_off.light_on)

    @patch.object(GPIO, "input")
    def test_light_level_from_450_to_525_and_office_worker_leaves(self, mock_input):
        mock_input.side_effect = [0, 450, 100, 525]
        self.int_off.manage_light_level()
        self.int_off.manage_light_level()
        self.assertEqual(False, self.int_off.light_on)
