import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import test_util as util
from ingenium_embedded import bus_1553_step
import logging
import requests
from test_util import *
from sim_functions import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Bus1553Tests(unittest.TestCase):

    def setUp(self):

        get_venue_sim_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        # # login and set header token
        # ingenium_step_sdk.set_login_info(environment_variable=True)
        # ingenium_step_sdk.login()
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        # print("Shutting down MTAK session...")
        # ing_lib.ShutdownMTAK()

        # print("Starting MTAK session: {}".format(session_id))
        # ing_lib.StartMTAK(session=[int(session_id)])


        ing_lib.register_session("SIDE A", 10)


        self.step = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "BUS_1553",
            "execution_user_input": {
                "start_time": "CURRENT_TIME",
                "lookback": 0,
                "timeout": 10,
                "time_type": "SCET",
                "verify_wait": "VERIFY",
                "entries": [
                    {
                    "bus_1553_var": "TEST",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "GREATER_THAN",
                    "verification_values": [
                        "string"
                    ]
                    }
                ]
                },
            "execution": {
                "meta_data": {
                    "status": "",
                    "time_started": 1231231
                },
                "results": {}
            }
        }

    def tearDown(self):

        pass

    def test_no_present_integer(self):

        print("Integer: NOT_PRESENT")
        get_ing_auth_header()        
        get_auth_header()
        # LOAD INTEGER DATA 
        bus_data = configurable_bus_1553_entry("bus_int_not_present", "INT", "0", "0")
        url = ing_lib.post_1553_test_data()

        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Float data was posted to venue simulator")
        
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_int_not_present",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "NOT_PRESENT",
                    "verification_values": [
                        "0"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        print("res:", response)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "FAIL")
        self.assertEqual(single_entry_status, "FAIL")

    def test_no_present_float(self):

        print("Float: NOT_PRESENT")
        get_ing_auth_header()        
        get_auth_header()
        # LOAD INTEGER DATA 
        bus_data = configurable_bus_1553_entry("bus_float_not_present", "FLOAT", "0.0", "0.0")
        url = ing_lib.post_1553_test_data()

        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Float data was posted to venue simulator")
        
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_float_not_present",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "NOT_PRESENT",
                    "verification_values": [
                        "0"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        print("res:", response)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "FAIL")
        self.assertEqual(single_entry_status, "FAIL")


    def test_verify_float(self):

        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_float()
        url = ing_lib.post_1553_test_data()

        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Float data was not posted to venue simulator")

        # RECORD 
        print("Float: RECORD")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_float",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "RECORD",
                    "verification_values": [
                        "0"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        print(status)
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")
        
        
        get_ing_auth_header()
        get_auth_header()
        #EQUAL
        print("Float: EQUAL")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_float",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "1.23"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        get_ing_auth_header()
        get_auth_header()
        # GREATER THAN
        print("Float: Greater Than")

        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_float",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "GREATER_THAN",
                    "verification_values": [
                        "0.5"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        get_ing_auth_header()
        get_auth_header()
        # INCLUSIVE RANGE 
        print("Float: Inclusive Range")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_float",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "INCLUSIVE_RANGE",
                    "verification_values": [
                        "0.5", "2.0"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")
        
        #more than one entry
        get_ing_auth_header()
        get_auth_header()


        # CHANGE - EQUAL 
        ic.mil_1553_variables["bus_float"] = {
			"actual_value": 1.23
		}        

        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_float",
                    "raw_convert": "RAW",
                    "verify_on": "CHANGE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "0"
                    ]
                }
            ]
        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

    def test_verify_integer(self):

        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_integer()
        url = ing_lib.post_1553_test_data()

        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Integer data was not posted to venue simulator")

        # RECORD 
        print("Integer: RECORD")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "RECORD",
                    "verification_values": [
                        "0"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        # EQUAL
        get_ing_auth_header()        
        get_auth_header()
        print("Integer: RECORD")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "10"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")
        
        # GREATER THAN
        get_ing_auth_header()        
        get_auth_header()
        print("Integer: RECORD")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "GREATER_THAN",
                    "verification_values": [
                        "9"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        # INCLUSIVE RANGE 
        get_ing_auth_header()        
        get_auth_header()
        print("Integer: RECORD")
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "INCLUSIVE_RANGE",
                    "verification_values": [
                        "0", "11"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")


        # CHANGE - EQUAL 
        get_ing_auth_header()        
        get_auth_header()
        ic.mil_1553_variables["bus_integer"] = {
			"actual_value": 4
		}        

        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "CHANGE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "6"
                    ]
                }
            ]
        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")


    def test_verify_enum(self):

        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_enum()
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Enum data was posted to venue simulator")

        # RECORD
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_enum",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "RECORD",
                    "verification_values": [
                        "ROVER_START"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        # EQUAL - convert
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_enum",
                    "raw_convert": "CONVERT",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "ROVER_START"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        # EQUAL - raw
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_enum",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "1"
                    ]
                }
            ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")


        # CHANGE - EQUAL 
        get_ing_auth_header()        
        get_auth_header()
        ic.mil_1553_variables["bus_enum"] = {
			"actual_value": "ROVER_START"
		}        

        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_enum",
                    "raw_convert": "CONVERT",
                    "verify_on": "CHANGE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "ROVER_START"
                    ]
                }
            ]
        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        self.assertEqual(status, "ERROR")


        # CHANGE - EQUAL - FAIL
        get_ing_auth_header()        
        get_auth_header()
        ic.mil_1553_variables["bus_enum"] = {
			"actual_value": "ROVER_START"
		}        

        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_enum",
                    "raw_convert": "CONVERT",
                    "verify_on": "CHANGE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "ROVER_STOP"
                    ]
                }
            ]
        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        self.assertEqual(status, "ERROR")


    def test_verify_poly(self):

        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_poly()
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Poly data was posted to venue simulator")

        # EQUAL 
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_poly",
            "raw_convert": "CONVERT",
            "verify_on": "VALUE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "0.5e-9"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_poly",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "11101"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")

        # GREATER THAN 
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_poly",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "GREATER_THAN",
            "verification_values": [
                "0.2e-10"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")        


        # CHANGE - EQUAL

        get_ing_auth_header()        
        get_auth_header()
        ic.mil_1553_variables["bus_poly"] = {
			"actual_value": 0.5e-9
		}        

        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_poly",
            "raw_convert": "CONVERT",
            "verify_on": "CHANGE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "0.0"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        print(response)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")     

    def test_verify_binary(self):

        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_binary()
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Binary data was posted to venue simulator")


        # RECORD
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_binary",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "RECORD",
            "verification_values": [
                "0"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")  


        # EQUAL
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_binary",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "10101"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")  


        # CHANGE 

        get_ing_auth_header()        
        get_auth_header()

        ic.mil_1553_variables["bus_binary"] = {
			"actual_value": "10101"
		}        
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_binary",
            "raw_convert": "RAW",
            "verify_on": "CHANGE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "10101"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        self.assertEqual(status, "ERROR")


    def test_verify_hex(self):

        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_hex()
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Hex data was posted to venue simulator")


        # RECORD
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_hex",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "RECORD",
            "verification_values": [
                "0"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")  


        # EQUAL
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_hex",
            "raw_convert": "CONVERT",
            "verify_on": "VALUE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "0xDEAD"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")  


        # CHANGE 

        get_ing_auth_header()        
        get_auth_header()

        ic.mil_1553_variables["bus_hex"] = {
			"actual_value": "0xDEAD"
		}        
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_hex",
            "raw_convert": "RAW",
            "verify_on": "CHANGE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "0xDEAD"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        self.assertEqual(status, "ERROR")


        # LOAD FLOAT DATA 
        bus_data = []
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Hex data was posted to venue simulator")
        
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_hex",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "RECORD",
            "verification_values": [
                "0"
                ]
            }
        ]
        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "FAIL")
        self.assertEqual(single_entry_status, "FAIL")  


    def test_wait_bus_1553(self):
        get_ing_auth_header()        
        get_auth_header()
        self.step["execution_user_input"] = {
                "start_time": "CURRENT_TIME",
                "lookback": 0,
                "timeout": 10,
                "time_type": "SCET",
                "verify_wait": "WAIT",
                "entries": [
                    {
                        "bus_1553_var": "bus_binary",
                        "raw_convert": "RAW",
                        "verify_on": "VALUE",
                        "verification_condition": "EQUAL",
                        "verification_values": [
                            "10101"
                            ]
                        }
                ]
            }

        # load binary data 
        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_binary()
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)

        if r.status_code in [204, 200]:
            print("Binary data was posted to venue simulator")
        # test condition verified true


        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "PASS")
        self.assertEqual(single_entry_status, "PASS")  


        # test condition verified false 
        self.step["execution_user_input"]["entries"] = [
        {
            "bus_1553_var": "bus_binary",
            "raw_convert": "RAW",
            "verify_on": "VALUE",
            "verification_condition": "EQUAL",
            "verification_values": [
                "11111"
                ]
            }
        ]

        response = bus_1553_step.run(self.step)
        print(response)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "FAIL")
        self.assertEqual(single_entry_status, "FAIL")  

        # test no result from venue server

        # LOAD EMPTY BINARY DATA 
        bus_data = []
        url = ing_lib.post_1553_test_data()
        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Binary data was posted to venue simulator")

        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]
        self.assertEqual(status, "FAIL")
        self.assertEqual(single_entry_status, "FAIL")          


    def test_multiple_entries(self):
        
        # test multiple entries
        get_ing_auth_header()        
        get_auth_header()
        # LOAD FLOAT DATA 
        bus_data = bus_1553_integer()
        url = ing_lib.post_1553_test_data()

        r = requests.post(url, json=bus_data, headers=tc.venue_header, verify=False)
        print(r.status_code, r.text)
        if r.status_code in [204, 200]:
            print("Integer data was posted to venue simulator")

        self.step["execution_user_input"]["entries"] = [
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "10"
                    ]
                },
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "11"
                    ]
                },
                {
                    "bus_1553_var": "bus_integer",
                    "raw_convert": "RAW",
                    "verify_on": "VALUE",
                    "verification_condition": "EQUAL",
                    "verification_values": [
                        "10"
                    ]
                }                
            ]    
        response = bus_1553_step.run(self.step)
        status = response["execution"]["meta_data"]["status"]
        single_entry_status = response["execution"]["results"]["entries"][0]["verification_status"]


if __name__ == "__main__":
    unittest.main()