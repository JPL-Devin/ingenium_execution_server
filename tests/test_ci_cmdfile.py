import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import cmd_file_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import test_util as util
import logging
import requests
import json
from test_util import *
from sim_functions import *



class CmdFileTests(unittest.TestCase):

    def setUp(self):

        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]

        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        # login and set header token

        # get session id environment variable
        """
        print("Shutting down MTAK session...")
        ing_lib.ShutdownMTAK()

        print("Starting MTAK session: {}".format(session_id))
        ing_lib.StartMTAK(session=[int(session_id)])
        """
        ing_lib.register_session("SIDE A", 10)

        self.step = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "CMD_FILE",
            "execution_user_input": {
                "data_path": "SIDE A",
                "entries": [
                    {
                    "file_type": 0,
                    "timeout": 10,
                    "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                    "onboard_path": "/eng/blah",
                    "overwrite": True,
                    "verify": True
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


    def test_cmd_binary_file_function(self):

        print("Loading EHA data")
        url = ing_lib.get_test_eha()
        for channel in ic.binary_file_channels:
            eha_data = test_eha_obj(3, channel, 1)
            r = requests.post(url, json=eha_data, headers=ic.header, verify=False)

        print("Load receipt config")
        url = ing_lib.get_receipt_configs()
        receipt = receipt_file()
        r = requests.post(url, json=receipt, headers=ic.header, verify=False)


        print("Nominal: Checking binary file command (overwrite=True)...")
        binary_file_dispatch = cmd_file_step.run(self.step)
        print(json.dumps(binary_file_dispatch, indent=4))
        result = binary_file_dispatch["execution"]["results"]["entries"][0]
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], True)
        self.assertEqual(util.is_iso(result["verified_time"]), True)


        print("Nominal: Command with overwrite=False")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": "0",
                "timeout": 20,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": "/eng/test",
                "overwrite": False,
                "verify": True
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        print(binary_file_dispatch)
        result = binary_file_dispatch["execution"]["results"]["entries"][0]
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], True)
        self.assertEqual(util.is_iso(result["verified_time"]), True)


        print("Nominal: Command with verify=False")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": 0,
                "timeout": 10,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": "/eng/blah",
                "overwrite": True,
                "verify": False
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        result = binary_file_dispatch["execution"]["results"]["entries"][0]

        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], False)
        self.assertEqual(result["verified_time"], "")

        print("Nominal: Command with overwite and verify = False")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": 0,
                "timeout": 10,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": "/eng/blah",
                "overwrite": False,
                "verify": False
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        result = binary_file_dispatch["execution"]["results"]["entries"][0]

        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], False)
        self.assertEqual(result["verified_time"], "")


    def test_off_nominal_error(self):

        print("Off-Nominal: No file path provided")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": 0,
                "timeout": 10,
                "file_path": None,
                "onboard_path": "/eng/blah",
                "overwrite": False,
                "verify": True
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")


        print("Off-Nominal: No onboard path provided")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": 0,
                "timeout": 10,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": None,
                "overwrite": False,
                "verify": False
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")



        print("Off-Nominal: unknown file type")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": "hello",
                "timeout": 10,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": None,
                "overwrite": False,
                "verify": False
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")



        print("Off-Nominal: No data path provided")
        self.step["execution_user_input"] =  {
            "data_path": None,
            "entries": [
                {
                "file_type": "hello",
                "timeout": 10,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": None,
                "overwrite": False,
                "verify": False
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")


        print("Off-Nominal: Wrong data path provided")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE B",
            "entries": [
                {
                "file_type": "hello",
                "timeout": 10,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": None,
                "overwrite": False,
                "verify": False
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")


        print("Off-Nominal: unknown file path")

        print("Force error: 404")
        url = ing_lib.get_forced_errors()
        msg = {"message":"File path not found"}
        forced_error = forced_error_obj("/cmd/binary_file", errorflag="404", errormsg=msg)
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)

        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": "0",
                "timeout": 10,
                "file_path": "/my/home/directory/shell.py",
                "onboard_path": "/eng/blah",
                "overwrite": False,
                "verify": True
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")

    def test_off_nominal_timeout(self):
        print("Force error: 408")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/cmd/binary_file", errorflag="408")
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)

        print("Off-Nominal: Coercing a timeout error")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                "file_type": 0,
                "timeout": 1,
                "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                "onboard_path": "/eng/blah",
                "overwrite": True,
                "verify": True
                }
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)
        self.assertEqual(binary_file_dispatch["execution"]["meta_data"]["status"], "ERROR")

    def test_string_selection(self):

        print("test cmd file string selection option")
        self.step["execution_user_input"] =  {
            "data_path": "SIDE A",
            "entries": [
                {
                    "file_type": 0,
                    "timeout": 1,
                    "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                    "onboard_path": "/eng/blah",
                    "overwrite": True,
                    "verify": True,
                    "string_selection": "A"
                },
                {
                    "file_type": 0,
                    "timeout": 1,
                    "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                    "onboard_path": "/eng/blah",
                    "overwrite": True,
                    "verify": True,
                    "string_selection": "B"
                },
                {
                    "file_type": 0,
                    "timeout": 1,
                    "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                    "onboard_path": "/eng/blah",
                    "overwrite": True,
                    "verify": True,
                    "string_selection": "AB"
                },
                {
                    "file_type": 0,
                    "timeout": 1,
                    "file_path": "/home/swanchr/Ingenium/GraphEHA.py",
                    "onboard_path": "/eng/blah",
                    "overwrite": True,
                    "verify": True,
                    "string_selection": "DEFAULT"
                },
            ]
        }

        binary_file_dispatch = cmd_file_step.run(self.step)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))

