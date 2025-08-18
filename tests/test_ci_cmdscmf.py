import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import cmd_scmf_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import test_util as util
import logging
import requests
from test_util import *
from sim_functions import *



class CmdscmfTests(unittest.TestCase):

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

        valid_scmf = "/home/swanchr/TEST_SCMF.scmf"
        self.step = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "MANUAL_INPUT",
            "execution_user_input": {
                        "data_path": "SIDE A",
                        "entries": [
                            {
                            "file_type": "0",
                            "timeout": 10,
                            "file_path": valid_scmf,
                            "verify": False
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

            self.assertIsInstance(dispatch["file_type"], str)
            self.assertIsInstance(dispatch["file_path"], (str, type(None)))
            self.assertIsInstance(dispatch["verify"], bool)
            self.assertIsInstance(dispatch["radiated"], bool)
            self.assertEqual(util.is_iso(dispatch["radiated_time"]), True)

    def test_cmd_scmf_function(self):

        print("Load scmf config immediate")
        url = ing_lib.get_scmf_config()
        config = scmf_config(uplink_type="immediate", message="ACS_THRUSTER")
        r = requests.post(url, json=config, headers=ic.header, verify=False)

        # with current implementation, scmf api endpoints need to be run with disableChecks=True
        print("Checking scmf command (disable_checks = True)...")
        dispatch = cmd_scmf_step.run(self.step)
        print(dispatch)
        self.verify_response_structure(dispatch["execution"]["results"]["entries"])

    def test_cmd_scmf_hw(self):

        print("Load scmf config hardware")
        url = ing_lib.get_scmf_config()
        config = scmf_config(uplink_type="hardware", message="STAR_CAMERA")
        r = requests.post(url, json=config, headers=ic.header, verify=False)

        print("Checking scmf command (disable_checks = True)...")
        dispatch = cmd_scmf_step.run(self.step)
        print(dispatch)
        self.verify_response_structure(dispatch["execution"]["results"]["entries"])

    def test_cmd_scmf_file(self):

        print("Load scmf config hardware")
        url = ing_lib.get_scmf_config()
        config = scmf_config(uplink_type="file", message="/this/directory")
        r = requests.post(url, json=config, headers=ic.header, verify=False)

        print("Checking scmf command (disable_checks = True)...")
        dispatch = cmd_scmf_step.run(self.step)
        print(dispatch)
        self.verify_response_structure(dispatch["execution"]["results"]["entries"])


    def test_cmd_scmf_invalid_file_path_inputs(self):

        print("Providing invalid file path...")
        print("Force error: 404")
        url = ing_lib.get_forced_errors()
        msg = {"message": "Resource was not found"}
        forced_error = forced_error_obj("/cmd/scmf", errorflag="404", errormsg=msg)
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)

        self.step["execution_user_input"]["entries"][0]["file_path"] = "/thisuser/thisfolder/thisfile.py"
        dispatch = cmd_scmf_step.run(self.step)
        print(dispatch)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")


        print("Providing NO file path...")
        self.step["execution_user_input"]["entries"][0]["file_path"] = ""
        dispatch = cmd_scmf_step.run(self.step)
        print(dispatch)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        forced_error = ["/cmd/scmf"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)


    def test_cmd_scmf_invalid_data_path(self):

        print("Providing an invalid data path...")
        self.step["execution_user_input"]["data_path"] = "SIDE B"
        dispatch = cmd_scmf_step.run(self.step)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")


    def test_cmd_scmf_timeout_error(self):
        print("Force error: 408")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/cmd/scmf", errorflag="408")
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)

        print("Providing a very short timeout for SCMF command, expecting timeout error...")
        self.step["execution_user_input"]["entries"][0]["timeout"] = 1
        dispatch = cmd_scmf_step.run(self.step)
        print(dispatch)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
