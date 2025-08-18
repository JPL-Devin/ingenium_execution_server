import xmlrunner
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
import unittest
from ingenium_embedded import manual_input_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import logging
from test_util import *
from sim_functions import *
import test_util as util
import copy
import json

class ManualInputTests(unittest.TestCase):

    def setUp(self):
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        get_auth_header()
        get_ing_auth_header()

        ing_lib.register_session("SIDE A", 10)

        self.step = {
            "execution_id": 1,
            "elem_id": "15",
            "step_type": "MANUAL_INPUT",
            "variable": {"name": "manual_input"},
            "execution_user_input": {
                "entries": [
                    {
                        "name": "test",
                        "type": "STRING",
                        "verification_condition": "EQUAL",
                        "verify_on": "VALUE",
                        "verification_values": ["30"],
                        "actual_value": "50"
                    }
                ]
            },
            "execution": {
                "meta_data": {
                    "status": "",
                    "time_started": 123123123
                },
                "results": {}
            }
        }

    def tearDown(self):
        pass

    def test_no_verification_value_input(self):

        self.step["execution_user_input"]["entries"] = [
                    {
                        "name": "test",
                        "type": "STRING",
                        "verification_condition": "EQUAL",
                        "verify_on": "VALUE",
                        "verification_values": [],
                        "actual_value": "50"
                    }
                ]
        
        response = manual_input_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_all_the_string_validation_things(self):

        print("Providing a 'GREATER_THAN' and 'LESS_THAN' for a string type...")
        self.step["execution_user_input"]["entries"][0]["type"] = "STRING"

        for condition in ["GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL", "INCLUSIVE_RANGE", "EXCLUSIVE_RANGE"]:
            self.step["execution_user_input"]["entries"][0]["verification_condition"] = condition
            response = manual_input_step.run(self.step)
            self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Providing EQUAL for string type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "test"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["test"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["other"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")


        print("Providing NOT_EQUAL for string type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "test"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["other"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["test"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing RECORD for string type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "test"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["entries"][0]["actual_value"] = ""
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")


        print("Providing CONTAINS for string type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "CONTAINS"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["ace"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "aces"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        #Change: EQUAL (pass)
        ic.manual_input_variables["test"] = {
                    "type": "STRING",
                    "actual_value": "previous"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["previous"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "False"
        response = manual_input_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        #Change: NOT_EQUAL (pass)
        ic.manual_input_variables["test"] = {
                    "type": "STRING",
                    "actual_value": "previous"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["False"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "False"
        response = manual_input_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")



    def test_all_the_boolean_validation_things(self):

        print("Providing mathematical operators for a boolean type...")
        self.step["execution_user_input"]["entries"][0]["type"] = "BOOLEAN"
        for condition in ["GREATER_THAN", "LESS_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN_OR_EQUAL", "INCLUSIVE_RANGE", "EXCLUSIVE_RANGE"]:
            self.step["execution_user_input"]["entries"][0]["verification_condition"] = condition
            response = manual_input_step.run(self.step)
            self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Providing EQUAL for boolean type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["type"] = "BOOLEAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["TRUE"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "TRUE"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["FALSE"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing NOT_EQUAL for boolean type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["FALSE"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "TRUE"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Providing RECORD for boolean type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["FALSE"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "TRUE"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["FALSE"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = ""
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")


        print("Providing CHANGE for Equal...")
        #Change: EQUAL (pass)
        ic.manual_input_variables["test"] = {
                    "type": "BOOLEAN",
                    "actual_value": "False"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["False"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "False"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        # Change: EQUAL (fail)
        ic.manual_input_variables["test"] = {
                    "type": "BOOLEAN",
                    "actual_value": "False"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["True"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "False"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        #Change: NOT_EQUAL (pass)
        ic.manual_input_variables["test"] = {
                    "type": "BOOLEAN",
                    "actual_value": "False"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["True"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "False"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        #Change: NOT_EQUAL (pass)
        ic.manual_input_variables["test"] = {
                    "type": "BOOLEAN",
                    "actual_value": "False"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["False"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "False"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Off-Nominal: Equal with more than 1 value")
        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "BOOLEAN",
                "verification_condition": "EQUAL",
                "verify_on": "VALUE",
                "verification_values": ["true", "false"],
                "actual_value": "false"
            }
        ]

        response = manual_input_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Off-Nominal: Equal with no verification values")
        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "BOOLEAN",
                "verification_condition": "EQUAL",
                "verify_on": "VALUE",
                "verification_values": [],
                "actual_value": "false"
            }
        ]

        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Off-Nominal: Record on boolean type")
        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "BOOLEAN",
                "verification_condition": "RECORD",
                "verify_on": "CHANGE",
                "verification_values": [],
                "actual_value": "false"
            }
        ]

        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


    def test_all_the_integer_validation_things(self):

        print("Providing GREATER_THAN for integer type...")
        self.step["execution_user_input"]["entries"][0]["type"] = "INTEGER"
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "VALUE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "GREATER_THAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["30"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing LESS_THAN for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "LESS_THAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing GREATER_THAN_OR_EQUAL for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "GREATER_THAN_OR_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "1"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Proving LESS_THAN_OR_EQUAL for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "LESS_THAN_OR_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "1"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing EQUAL for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing NOT_EQUAL for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing RECORD for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")


        # TODO: invalid condition type for integer
        print("Providing CONTAINS for integer type...")

        # make a copy not to be affected by the previous tests
        step = copy.deepcopy(self.step)
        step["execution_user_input"]["entries"][0]["verification_condition"] = "CONTAINS"
        step["execution_user_input"]["entries"][0]["verification_values"] = ["10"]
        step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PENDING")

        print("Providing INCLUSIVE_RANGE for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "INCLUSIVE_RANGE"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10","20"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "15"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "31"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing EXCLUSIVE_RANGE for integer type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EXCLUSIVE_RANGE"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10","20"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "15"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "31"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing CHANGE for integer type...")
        #Change: EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "INTEGER",
                    "actual_value": "20"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["30"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "50"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["-20"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "30"

        response = manual_input_step.run(self.step)

    def test_all_the_float_validation_things(self):

        print("Providing GREATER_THAN for float type...")
        self.step["execution_user_input"]["entries"][0]["type"] = "FLOAT"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "GREATER_THAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10.5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["30.12"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing LESS_THAN for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "LESS_THAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10.4"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.1"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10.1"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing GREATER_THAN_OR_EQUAL for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "GREATER_THAN_OR_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.8"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.8"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.7"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.15"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "1.9"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Testing Greater than or equal for decimal precision")
        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "FLOAT",
                "verification_condition": "GREATER_THAN_OR_EQUAL",
                "verify_on": "VALUE",
                "verification_values": ["50.0"],
                "actual_value": "49.99999999999"
            }
        ]

        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Proving LESS_THAN_OR_EQUAL for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "LESS_THAN_OR_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.4"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.4"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.2"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "1.4"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.6"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.2"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Testing Less than or equal for decimal precision")
        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "FLOAT",
                "verification_condition": "LESS_THAN_OR_EQUAL",
                "verify_on": "VALUE",
                "verification_values": ["50.0"],
                "actual_value": "49.99999999999"
            }
        ]

        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")


        print("Providing EQUAL for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.34"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.34"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.2"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing NOT_EQUAL for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.6"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.78"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing RECORD for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "RECORD"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5.3"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.23"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Providing INCLUSIVE_RANGE for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "INCLUSIVE_RANGE"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10.5","20.5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "15.4"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.2"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "31.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Testing Inclusive Range for decimal precision")
        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "FLOAT",
                "verification_condition": "INCLUSIVE_RANGE",
                "verify_on": "VALUE",
                "verification_values": ["50.0", "60.0"],
                "actual_value": "49.99999999999"
            }
        ]

        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"] = [
            {
                "name": "test",
                "type": "FLOAT",
                "verification_condition": "INCLUSIVE_RANGE",
                "verify_on": "VALUE",
                "verification_values": ["50.0", "60.0"],
                "actual_value": "49.99"
            }
        ]

        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing EXCLUSIVE_RANGE for float type...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EXCLUSIVE_RANGE"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10.5","20.5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "15.1"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "10.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20.5"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "5.34"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        self.step["execution_user_input"]["entries"][0]["actual_value"] = "31.12"
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Providing CHANGE for float type...")

        #Change: EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "20.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["30"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "50.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        # Change special case: EQUAL where change is 0.0
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "20.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["0"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "20.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        #Change: GREATER_THAN
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "20.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "GREATER_THAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["5"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "30.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        #Change: LESS_THAN
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "20.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "LESS_THAN"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["15"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "30.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")


        # Change: LESS_THAN_OR_EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "20.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "LESS_THAN_OR_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "30.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        # Change: GREATER_THAN_OR_EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "20.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "GREATER_THAN_OR_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "30.1"
        response = manual_input_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")


        #Change special case: decimal precision test for EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "50.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["50"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "100.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")


        #Change special case: just for kicks, negative decimal precision test for EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "100.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["-50"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "50.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        #Change special case: decimal precision test for NOT_EQUAL
        ic.manual_input_variables["test"] = {
                    "type": "FLOAT",
                    "actual_value": "50.1"
        }
        self.step["execution_user_input"]["entries"][0]["verify_on"] = "CHANGE"
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "NOT_EQUAL"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["50"]
        self.step["execution_user_input"]["entries"][0]["actual_value"] = "100.1"
        response = manual_input_step.run(self.step)

        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        #TODO: off nominal cases: wrong verification values types, unsupported conditions, etc.

    def test_more_off_nominals(self):

        print("Off-Nominal: no verification values")
        self.step["execution_user_input"]["entries"][0]["verification_values"] = []
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


        print("Off-Nominal: Providing more than 1 value with 'EQUAL' condition...")
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["test", "hey"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Off-Nominal: Providing more than 2 values for 'INCLUSIVE_RANGE'...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "INCLUSIVE_RANGE"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["10", "4", "5"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Off-Nominal: Providing non integer values for 'EXCLUSIVE RANGE'...")
        self.step["execution_user_input"]["entries"][0]["verification_condition"] = "EXCLUSIVE_RANGE"
        self.step["execution_user_input"]["entries"][0]["verification_values"] = ["hello", "there"]
        response = manual_input_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))

