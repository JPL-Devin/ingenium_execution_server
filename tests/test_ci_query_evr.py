import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import query_evr_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
from test_util import get_test_time
from sim_functions import *
import requests
from test_util import *
from sim_functions import *



class QueryEVRTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        # load string eha data
        url = ing_lib.get_test_evr()
        evr_data = test_evr_obj(5, evr_name=ic.binary_file_evr_name, evr_message="ACS_THRUSTER")
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)
        print(r.status_code, r.text)
        if r.status_code == 204:
            print("EVR data loaded")


    def setUp(self):

        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)


        start_time, end_time = get_test_time()


        # register session for testing
        ing_lib.register_session("SIDE B", 10)

        # base step json. Unit tests simply manipulate inputs to exact specific responses.
        self.step = {
            "elem_id": "uuid-step-4",
            "elem_type": "STEP",
            "execution_id": "uuid-execution-12",
            "description": "A step to update the venue configuration",
            "number": "1-4",
            "step_type": "QUERY_EVR",
            "variable": {"name": "sample_variable"},
            "code": {
                "name": "evr_query.run",
                "commit": "commit-hash-43faea",
                "release": "1.0"
            },
            "guard": "",
            "notices": [
                {
                    "category": "TESTBED_WARNING",
                    "message": "This is a warning for test bed"
                },
                {
                    "category": "PERSONNEL_CAUTION",
                    "message": "This is a caution for personnel"
                }
            ],
            "specification": {
                "evr_name": "",
                "evr_id": "",
                "evr_type": "",
                "evr_level": "",
                "start_time": "",
                "end_time": "",
                "duration": None,
                "time_type": "",
                "message_filter": "",
                "timeout": 240,
                "verification_condition": "RECORD",
                "verification_value": None,
                "data_path": ""
            },
            "execution_user_input": {
                "evr_name": None,
                "evr_id": None,
                "evr_type": None,
                "evr_level": None,
                "start_time": "CURRENT_TIME",
                "end_time": None,
                "duration": None,
                "time_type": "ERT",
                "message_filter": "",
                "timeout": 240,
                "verification_condition": "GREATER_THAN",
                "verification_value": 0,
                "data_path": "SIDE B"
            },
            "execution": {
                "meta_data": {
                    "test_conductor": "hongmank",
                    "status": "",
                    "time_started": "2017-02-16T19:20:30+01:00",
                    "time_completed": "2017-02-16T19:20:32+01:00",
                    "message": ""
                },
                "results": {
                }
            }
        }

        # made a variable to easily traverse to the user input values.
        self.step_user_input = self.step["execution_user_input"]

    def tearDown(self):
        pass

    def test_evr_id_can_cast_string_to_int(self):

        print("Provide nominal integer EVR id")
        self.step["execution_user_input"] = {
            "evr_name": None,
            "evr_id": "123",
            "evr_type": None,
            "evr_level": None,
            "start_time": "CURRENT_TIME",
            "end_time": None,
            "duration": None,
            "time_type": "ERT",
            "message_filter": "",
            "verification_condition": "GREATER_THAN",
            "data_path": "SIDE B"
        }

        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "PASS")

        print("Provide off nominal string as EVR id")
        self.step["execution_user_input"] = {
            "evr_name": None,
            "evr_id": "hello",
            "evr_type": None,
            "evr_level": None,
            "start_time": "CURRENT_TIME",
            "end_time": None,
            "duration": None,
            "time_type": "ERT",
            "message_filter": "",
            "verification_condition": "GREATER_THAN",
            "data_path": "SIDE B"
        }

        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")

    def test_ideal_scenario(self):
        print("Testing ideal scenario, with all required variables correctly formmatted...")
        evrs = query_evr_step.run(self.step)
        print("HERE",evrs)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "PASS")

    def test_return_values_test(self):
        print("Testing when 'timeout' and/or 'verification_value' is not provided they default to 0 in response...")
        self.step["execution_user_input"] = {
            "evr_name": None,
            "evr_id": None,
            "evr_type": None,
            "evr_level": None,
            "start_time": "CURRENT_TIME",
            "end_time": None,
            "duration": None,
            "time_type": "ERT",
            "message_filter": "",
            "verification_condition": "GREATER_THAN",
            "data_path": "SIDE B"
        }

        evrs = query_evr_step.run(self.step)
        results = evrs["execution"]["results"]
        self.assertEqual(results["verification_value"], 0)
        self.assertEqual(results["timeout"], 240)

    def test_ideal_scenario_returns_none(self):
        print("Remove EVR data")
        url = ing_lib.get_test_evr()
        evr_data = []
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

        print("Testing Chill EVR endpoint with correct data, but no EVR data is returned...")
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]['evr_data'], [])


    def test_malformed_datetime_formatting(self):

        print("Testing input SCLK time format for SCET time type...")
        self.step["execution_user_input"]["start_time"] = "527925356"
        self.step["execution_user_input"]["time_type"] = "SCET"
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")

        print("Testing input SCET time format (UTC) for SCLK time type...")
        self.step["execution_user_input"]["start_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["end_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["time_type"] = "SCLK"
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")

        print("Inputting both start and end date, with a duration returns an error... ")
        self.step["execution_user_input"]["start_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["end_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["duration"] = 600
        self.step["execution_user_input"]["time_type"] = "ERT"
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")

        print("Inputting an incorrect datetime format for SCET will return an error...")
        self.step["execution_user_input"]["start_time"] = "2017-01-01T18:07:59"
        self.step["execution_user_input"]["end_time"] = "2017-01-04T19:07:90"
        self.step["execution_user_input"]["duration"] = None
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")

    def test_malformed_evr_type_value(self):
        print("Passing non-enumerated option into 'EVR Type' field...")
        self.step["execution_user_input"]["evr_type"] = "NOT_REAL_OPTION"
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")

    def test_invalid_session_id(self):
        """
        A data path maps to a single session ID. This test will simulate providing a data path
        that is not available in the ampcs_session_information list.
        """
        self.step["execution_user_input"]["data_path"] = "SIDE_A"
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["meta_data"]["status"], "ERROR")


    def test_message_filters(self):
        """
        Message filters are applied once a list of evr's are returned from the query_evr_step request.
        When a message filter is present the list of EVR's is filtered to only return EVR's
        that match the message filter.
        """
        url = ing_lib.get_test_evr()
        evr_data = test_evr_obj(5, evr_name=ic.binary_file_evr_name, evr_message="ACS_THRUSTER")
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

        print("Checking message filter returns EVRs that exact match said message filter...")
        self.step["execution_user_input"]["message_filter"] = "ACS_THRUSTER"
        evrs = query_evr_step.run(self.step)
        print(evrs)

        print("Checking message filter return EVRs that are a partial match to said message filter...")
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["message_filter"] = "storedCommand"
        evrs = query_evr_step.run(self.step)


    def test_verification(self):

        print("Checking GREATER THAN verification....")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "GREATER_THAN"
        self.step["execution_user_input"]["verification_value"] = 0
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")

        print("Checking LESS THAN verification...")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "LESS_THAN"
        self.step["execution_user_input"]["verification_value"] = 10
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")

        print("Checking GREAT THAN OR EQUAL verification...")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "GREATER_THAN_OR_EQUAL"
        self.step["execution_user_input"]["verification_value"] = 0
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")

        print("Checking LESS THAN OR EQUAL verification...")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "LESS_THAN_OR_EQUAL"
        self.step["execution_user_input"]["verification_value"] = 10
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")

        print("Checking EQUAL verification...")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["verification_value"] = 5
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")

        print("Checking NOT EQUAL verification...")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["verification_value"] = 10
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")

        print("Checking RECORD verification...")
        self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
        self.step["execution_user_input"]["time_type"] = "ERT"
        self.step["execution_user_input"]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["verification_value"] = 0
        evrs = query_evr_step.run(self.step)
        self.assertEqual(evrs["execution"]["results"]["verification_status"], "PASS")


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))