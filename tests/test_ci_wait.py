import xmlrunner
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import wait_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import unittest
from datetime import datetime, timedelta
from test_util import *



class WaitStepTests(unittest.TestCase):

    def setUp(self):
        
        # login and set header token
        get_ing_auth_header()
        get_auth_header()

        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        self.step = {
            "execution_id": 1,
            "elem_id": "uuid-step-4",
            "step_type": "WAIT_STEP",
            "variable": {"name": "wait"},
            "execution_user_input": {
                "wait_type": "DURATION",
                "time_value": "4"
            },
            "execution": {
                "meta_data": {
                    "status": "",
                    "time_started": 1231231
                },
                "results": {}
            }
        }

    def calculate_until_time_doy(self):

        future_time = datetime.utcnow() + timedelta(seconds=10)
        parsed = datetime.strftime(future_time, '%Y-%jT%H:%M:%S')
        return parsed

    def calculate_until_time_iso(self):

        future_time = datetime.utcnow() + timedelta(seconds=10)
        parsed = datetime.strftime(future_time, '%Y-%m-%dT%H:%M:%S')
        return parsed

    def verify_response_structure(self, entry):

        self.assertIsInstance(entry["wait_type"], (str, type(None)))
        self.assertIsInstance(entry["time_value"], (str, type(None)))

    def tearDown(self):

        pass

    def test_ideal(self):

        print("Checking an easy duration...")
        response = wait_step.run(self.step)
        self.verify_response_structure(response["execution"]["results"])

        time_value = self.calculate_until_time_iso()
        print("Checking an until duration...")
        self.step["execution_user_input"]["wait_type"] = "UNTIL"
        self.step["execution_user_input"]["time_value"] = time_value
        response = wait_step.run(self.step)
        self.verify_response_structure(response["execution"]["results"])

    def test_until_time_formats(self):

        print("Passing a DOY formmated time without 'z'")
        time_value = self.calculate_until_time_doy()
        self.step["execution_user_input"] = {
            "wait_type": "UNTIL",
            "time_value": time_value
        }

        response = wait_step.run(self.step)
        self.verify_response_structure(response["execution"]["results"])

        print("Passing an ISO formmated time")
        time_value = self.calculate_until_time_iso()
        self.step["execution_user_input"] = {
            "wait_type": "UNTIL",
            "time_value": time_value
        }

        response = wait_step.run(self.step)
        self.verify_response_structure(response["execution"]["results"])

    def test_odd_until_times(self):

        print("Pass earlier date than now...")
        self.step["execution_user_input"]["wait_type"] = "UNTIL"
        self.step["execution_user_input"]["time_value"] = "2017-11-20T00:15:00"
        response = wait_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Pass integer instead of date...")
        self.step["execution_user_input"]["time_value"] = "1234"
        response = wait_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Pass invalid date format")
        self.step["execution_user_input"]["wait_type"] = "UNTIL"
        self.step["execution_user_input"]["time_value"] = "2017-1120T00:15:00"
        response = wait_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


    def test_odd_duration_times(self):

        print("Checking passing non-integer value...")
        self.step["execution_user_input"]["time_value"] = "hellothere"
        response = wait_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Providing date as a duration time...")
        self.step["execution_user_input"]["time_value"] = "2017-11-20T00:15:00"
        response = wait_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_float_time(self):

        print("Test using float duration value...")
        self.step["execution_user_input"]["wait_type"] = "DURATION"
        self.step["execution_user_input"]["time_value"] = "4.3"        
        response = wait_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")        


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))

