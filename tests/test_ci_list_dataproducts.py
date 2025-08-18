import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from sim_functions import *
from test_util import *
import requests
import traceback
from test_util import get_test_time
from ingenium_embedded import ingenium_step_sdk
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import list_data_products_step
import xmlrunner
import unittest
import json
import copy


class ListDataProductsTests(unittest.TestCase):

    def setUp(self):

        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address = os.environ.get("VENUE_SIMULATOR_URL")
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        start_time, end_time = get_test_time()

        ing_lib.register_session("SIDE A", 58)

        self.step = {
            "execution_id": 1,
            "elem_id": "uuid-step-4",
            "step_type": "LIST_DATA_PRODUCTS",
            "variable": {"name": "data_products"},
            "execution_user_input": {
                "data_path": "SIDE A",
                "start_time": start_time,
                "end_time": None,
                "duration": 600,
                "time_type": "ERT",
                "timeout": 10,
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
                    "status": "",
                    "time_started": 12312312
                },
                "results": {}
            }
        }

    def tearDown(self):

        pass


    def test_bad_product_status_filter_inputs(self):

        print("Test Case: passing incorrect format for 'product status filter' field. Expect an error with appropriate error message.")
        self.step["execution_user_input"]["entries"] = [
            {
            "apid": 247,
            "product_status_filter": "all",
            "verification_condition": "LESS_THAN_OR_EQUAL",
            "verification_value": 3
            }
        ]

        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

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

        response = list_data_products_step.run(self.step) 
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_ideal_scenario(self):

        print("Load dataproduct")
        url = ing_lib.get_test_dp()
        dp_data = test_dp_obj(3, 247)
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)

        print("Checking list data products query...")
        response = list_data_products_step.run(self.step)
        print(response)
        products = response["execution"]["results"]["entries"][0]["products"]
        self.assertEqual(len(products),3)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

    def test_multiple_dataproducts_entries(self):

        print("Load dataproduct")
        url = ing_lib.get_test_dp()
        dp_data = test_dp_obj(3, 247)
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)

        print("Running multiple entries")
        self.step["execution_user_input"]["entries"].append(
            {
                "apid": 500,
                "product_status_filter": "ALL",
                "verification_condition": "GREATER_THAN",
                "verification_value": 0
            }
        )

        response = list_data_products_step.run(self.step)
        print(response)
        products = response["execution"]["results"]["entries"][0]["products"]
        self.assertEqual(len(products),3)
        products = response["execution"]["results"]["entries"][1]["products"]
        self.assertEqual(len(products),3)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

    def test_apid_inputs(self):

        print("Load dataproduct")
        url = ing_lib.get_test_dp()
        dp_data = []
        r = requests.post(url, json=dp_data, headers=ic.header, verify=False)

        # make a copy of step to avoid affecting tests later
        step = copy.deepcopy(self.step)
        print("Providing no apid")
        step["execution_user_input"]["entries"][0]["apid"] = None
        response = list_data_products_step.run(step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
        products = response["execution"]["results"]["entries"][0]["products"]
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")
        self.assertEqual(len(products),0)

        # make a copy of step to avoid affecting tests later
        step = copy.deepcopy(self.step)
        print("Providing an apid that can't be found...")
        step["execution_user_input"]["entries"][0]["apid"] = 1000
        response = list_data_products_step.run(step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
        products = response["execution"]["results"]["entries"][0]["products"]
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")
        self.assertEqual(len(products),0)

        # make a copy of step to avoid affecting tests later
        step = copy.deepcopy(self.step)
        print("Providing a non-integer apid...")
        step["execution_user_input"]["entries"][0]["apid"] = 'abc'
        response = list_data_products_step.run(step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
        products = response["execution"]["results"]["entries"][0]["products"]
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PENDING")
        self.assertEqual(len(products),0)

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
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Test Less than condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "LESS_THAN",
            "verification_value": 2
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Test Greater than or equal condition")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "GREATER_THAN_OR_EQUAL",
            "verification_value": 3
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Test Greater than or equal condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "GREATER_THAN_OR_EQUAL",
            "verification_value": 10
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Test Less than or equal condition")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "LESS_THAN_OR_EQUAL",
            "verification_value": 3
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Test Less than or equal condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "LESS_THAN_OR_EQUAL",
            "verification_value": 1
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Test equal condition")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "EQUAL",
            "verification_value": 3
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

        print("Test equal condition - FAIL")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "EQUAL",
            "verification_value": 10
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

        print("Test record condition")
        self.step["execution_user_input"]["entries"] = [
          {
            "apid": 247,
            "product_status_filter": "ALL",
            "verification_condition": "RECORD",
            "verification_value": 3
          }
        ]
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

    def test_time_inputs(self):

        print("Providing both a start and end times with duration...")
        self.step["execution_user_input"]["end_time"] = "2017-324T16:50:47"
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        self.step["execution_user_input"]["time_type"] = "SCLK"
        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_errors(self):

        print("Force a 408 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/dp", errorflag="408", errormsg={"message": "TIME OUT"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        self.step["execution_user_input"] = {
              "data_path": "SIDE A",
              "start_time": "CURRENT_TIME",
              "end_time": None,
              "duration": 600,
              "time_type": "ERT",
              "timeout": 10,
              "entries": [
                {
                  "apid": 247,
                  "product_status_filter": "ALL",
                  "verification_condition": "GREATER_THAN",
                  "verification_value": 0
                }
              ]
            }

        response = list_data_products_step.run(self.step)
        print(response)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_error_500(self):
        print("Force a 500 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/dp", errorflag="500", errormsg={"message": "THERE WAS AN ERROR"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)


        response = list_data_products_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
