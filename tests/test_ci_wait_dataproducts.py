import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from sim_functions import *
from test_util import *
import requests
from test_util import get_test_time
from datetime import datetime, timedelta
import traceback
from ingenium_embedded import ingenium_step_sdk
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import wait_data_products_step
import xmlrunner
import unittest
import json
import copy

class WaitDataProductsTests(unittest.TestCase):

    def setUp(self):

        print("Clear any endpoints")
        ic.venue_service_address = os.environ.get("VENUE_SIMULATOR_URL")
        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error,
                            headers=ic.header, verify=False)

        start_time, end_time = get_test_time()

        # # register session for testing
        ing_lib.register_session("SIDE A", 35)

        self.step = {
            "elem_id": "uuid-step-4",
            "elem_type": "STEP",
            "execution_id": "uuid-execution-12",
            "description": "A step to update the venue configuration",
            "number": "1-4",
            "step_type": "WAIT_DATA_PRODUCTS",
            "variable": {"name": "data_products"},
            "execution_user_input": {
                "data_path": "SIDE A",
                "start_time": "CURRENT_TIME",
                "lookback": 0,
                "timeout": 5,
                "entries": [
                    {
                      "apid": 247,
                      "product_status_filter": "ALL",
                      "verification_condition": "GREATER_THAN",
                      "verification_value": 0
                    }
                ]
            },
            "execution": {
                "meta_data": {
                    "test_conductor": "hongmank",
                    "status": "",
                    "time_started": "2017-02-16T19:20:30+01:00",
                    "time_completed": "2017-02-16T19:20:32+01:00",
                    "message": ""
                },
                "results": []
            }
        }

    def tearDown(self):

        pass

    def test_multiple_entries_with_timeout(self):

        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "GREATER_THAN",
                "verification_value": 1000
            },
            {
                "apid": 400,
                "product_status_filter": "ALL",
                "verification_condition": "GREATER_THAN",
                "verification_value": 0
            },
            {
                "apid": 500,
                "product_status_filter": "ALL",
                "verification_condition": "GREATER_THAN",
                "verification_value": 0
            }
        ] 
        response = wait_data_products_step.run(self.step)
        products = response["execution"]["meta_data"]["status"]
        self.assertEqual(products, "FAIL")


    def test_ideal_scenario(self):

        print("Load dataproduct")
        url = ing_lib.get_test_dp()
        dp_data = test_dp_obj(3, 247)
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)
        print(r.status_code)
        print("Checking wait data products embedded code...")
        response = wait_data_products_step.run(self.step)
        products = response["execution"]["results"]["entries"][0]["products"]
        print(response)

        self.assertEqual(len(products), 3)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PASS")


    def test_bad_product_status_filter_inputs(self):

        print("Test Case: passing incorrect format for 'product status filter' field. Expect an error with appropriate error message.")
        
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "all",
                "verification_condition": "GREATER_THAN_OR_EQUAL",
                "verification_value": 3
            }
        ]        
        response = wait_data_products_step.run(self.step)

        print("Test case: Execute dataproducts with multiple entries, mixture of good and bad product filter inputs")
        
        self.step["execution_user_input"]["entries"] = [
            {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "LESS_THAN_OR_EQUAL",
            "verification_value": 3
            },
            {
            "apid": 247,
            "product_status_filter": "all",
            "verification_condition": "LESS_THAN_OR_EQUAL",
            "verification_value": 3
            }
        ]

        response = wait_data_products_step.run(self.step) 
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_force_fail(self):

        print("Remove all data products")

        print("Force a fail")
        url = ing_lib.get_test_dp()
        dp_data = []
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)
        print("Checking wait data products embedded code...")
        response = wait_data_products_step.run(self.step)
        print(response)
        products = response["execution"]["results"]["entries"][0]["products"]

        self.assertEqual(len(products), 0)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

    def test_apid_inputs(self):
        print("Load dataproduct")
        url = ing_lib.get_test_dp()
        dp_data = []
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)

        print("Providing no apid")
        self.step["execution_user_input"]["entries"][0]["apid"] = None
        response = wait_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

        print("Providing an apid that can't be found...")
        self.step["execution_user_input"]["entries"][0]["apid"] = 1000
        response = wait_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

        print("Providing a non-integer apid...")
        self.step["execution_user_input"]["entries"][0]["apid"] = 'abc'
        print('self.step', json.dumps(self.step, indent=4))
        response = wait_data_products_step.run(self.step)
        print('response', json.dumps(response, indent=4))
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PENDING")

    def test_verification(self):

        print("Load 3 data products")
        url = ing_lib.get_test_dp()
        dp_data = test_dp_obj(3, 247)
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)
        self.assertEqual(r.status_code, 204)

        print("Test Less than condition")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "LESS_THAN",
                "verification_value": 5
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PASS")

        print("Test Less than condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "LESS_THAN",
                "verification_value": 2
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

        print("Test Greater than or equal condition")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "GREATER_THAN_OR_EQUAL",
                "verification_value": 3
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PASS")

        print("Test Greater than or equal condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "GREATER_THAN_OR_EQUAL",
                "verification_value": 5
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

        print("Test Less than or equal condition")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "LESS_THAN_OR_EQUAL",
                "verification_value": 3
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PASS")

        print("Test Less than or equal condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "LESS_THAN_OR_EQUAL",
                "verification_value": 1
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

        print("Test equal condition")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "EQUAL",
                "verification_value": 3
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PASS")

        print("Test equal condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "EQUAL",
                "verification_value": 5
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "FAIL")

        print("Test record condition")
        self.step["execution_user_input"]["entries"] = [
            {
                "apid": 247,
                "product_status_filter": "ALL",
                "verification_condition": "RECORD",
                "verification_value": 3
            }
        ]
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["results"]
                         ["entries"][0]["verification_status"], "PASS")

    def test_invalid_product_status(self):

        print("Providing an un-enumerated dp status...")
        self.step["execution_user_input"]["entries"][0]["verification_value"] = "NUMBER"
        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_errors(self):

        print("Force a 408 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj(
            "/dp", errorflag="408", errormsg={"message": "TIME OUT"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        self.step["execution_user_input"] = {
            "data_path": "SIDE A",
            "start_time": "CURRENT_TIME",
            "end_time": "",
            #   "duration": 600,
            "time_type": "ERT",
            "timeout": 5,
            "entries": [
                {
                    "apid": 247,
                    "product_status_filter": "ALL",
                    "verification_condition": "GREATER_THAN",
                    "verification_value": 0
                }
            ]
        }

        response = wait_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_error_500(self):
        print("Force a 500 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj(
            "/dp", errorflag="500", errormsg={"message": "THERE WAS AN ERROR"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = wait_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
