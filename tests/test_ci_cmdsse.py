import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import cmd_sse_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import logging
from test_util import *
import requests
from sim_functions import *



class CmdsseTests(unittest.TestCase):

    def setUp(self):
        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

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
            "step_type": "MANUAL_INPUT",
            "execution_user_input": {
                        "data_path": "SIDE A",
                        "entries": [
                            {
                            "timeout": 15,
                            "cmd_string": "flight 123 1 23.1"
                            }
                        ]
                    },
                "execution": {
                    "meta_data": {
                        "status": "",
                        "time_started": 123123
                    },
                    "results": {}
                }
        }

    def tearDown(self):

        pass


    def verify_response_structure(self, dispatches):

        for dispatch in dispatches:

            self.assertIsInstance(dispatch["timeout"], (int, type(None)))
            self.assertIsInstance(dispatch["cmd_string"], (str, type(None)))
            self.assertIsInstance(dispatch["radiated"], bool)
            self.assertIsInstance(dispatch["radiated_time"], str)

    def test_cmd_sse_function(self):


        print("Checking sse command...")
        dispatch = cmd_sse_step.run(self.step)
        results = dispatch["execution"]
        self.assertEqual(results["meta_data"]["status"], "PASS")
        self.verify_response_structure(dispatch["execution"]["results"]["entries"])

        print("Providing no cmd string...")
        self.step["execution_user_input"]["entries"][0]["cmd_string"] = ""
        dispatch = cmd_sse_step.run(self.step)
        results = dispatch["execution"]
        self.assertEqual(results["meta_data"]["status"], "ERROR")


    def test_cmd_sse_invalid_data_path(self):

        print("Providing an invalid data path...")
        self.step["execution_user_input"] = {
                    "data_path": "SIDE B",
                    "entries": [
                        {
                        "timeout": 15,
                        "cmd_string": "flight 123 1 23.1"
                        }
                    ]
                }
        dispatch = cmd_sse_step.run(self.step)
        results = dispatch["execution"]
        self.assertEqual(results["meta_data"]["status"], "ERROR")



    def test_cmd_sse_timeout_error(self):

        print("Force error: 408")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/cmd/sse", errorflag="408", errormsg={'message': 'timeout!'}, duration=0)
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)


        print("Providing a very short timeout for SSE command, expecting timeout error...")

        self.step["execution_user_input"] = {
                    "data_path": "SIDE A",
                    "entries": [
                        {
                        "timeout": 1,
                        "cmd_string": "flight 123 1 23.1"
                        }
                    ]
                }
        dispatch = cmd_sse_step.run(self.step)
        results = dispatch["execution"]
        self.assertEqual(results["meta_data"]["status"], "ERROR")


    def test_dummy_code(self):

        print("Checking dummy code...")
        response = cmd_sse_step.run_dummy(self.step)

        print("Checking user input...")
        user_input = response["execution_user_input"]

        self.assertEqual(user_input["data_path"], "SIDE A")
        self.assertIsInstance(user_input["entries"], list)

        print("Checking results metadata...")
        metadata = response["execution"]["meta_data"]
        self.assertEqual(metadata["status"], "PASS")

        print("Checking results...")
        results = response["execution"]["results"]["entries"][0]

        results_object = {
               'timeout':10,
               'cmd_string':'flight 123 42 1231',
               'radiated':True,
               'radiated_time':'2017-032T00:23:03'
            }

        self.assertEqual(results, results_object)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
