import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import gds_manual_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import logging
import test_util as util
import requests
from test_util import *
from sim_functions import *



class GdsStepTests(unittest.TestCase):

    def setUp(self):
        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        self.session_id = 10
        self.step = {
        "elem_id": "uuid-step-4",
        "elem_type": "STEP",
        "execution_id": "uuid-execution-12",
        "description": "A step to get the venue configuration",
        "number": "1-4",
        "step_type": "GDS",
        "variable": {"name": "sample_variable"},
         "execution_user_input": {
             "entries": [
                {
                "data_path": "SIDE A",
                "session_id": 10
                },
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

    def test_default_cmd_string(self):

        print("Testing default cmd string input")

        self.step["execution_user_input"] = {
             "default_cmd_string": "AB",
             "entries": [
                {
                "data_path": "SIDE A",
                "session_id": 29
                }
             ]
          }

        step_exec = gds_manual_step.run(self.step)
        self.assertEqual(step_exec["execution"]["meta_data"]["status"], "PASS")

    def test_previous_sessions_cleared(self):


        print("Registering data path and session id...")
        gds_manual_step.run(self.step)
        
        # only session should be SIDE A
        for data_path in ic.ampcs_session_information:
            if data_path["data_path"] == "SIDE A":
                self.assertEqual(data_path["session_id"], int(self.session_id))

        print("Adding a different session")
        self.step["execution_user_input"]["entries"] = [{
            "data_path": "SIDE C",
            "session_id": 64
            }]
        gds_manual_step.run(self.step)

        # expecting to see only SIDE C, and list of length 1
        self.assertEqual(len(ic.ampcs_session_information), 1)
        for data_path in ic.ampcs_session_information:
            if data_path["data_path"] == "SIDE C":
                self.assertEqual(data_path["session_id"], 64)

    def test_ideal_scenario(self):

        print("Registering data path and session id...")
        this = gds_manual_step.run(self.step)

        #check session in sessions dict match one added
        session = ing_lib.get_session_information(self.step["execution_user_input"]["entries"][0]["data_path"])
        self.assertEqual(session, int(self.session_id))

        print("Adding more than one session...")
        self.step["execution_user_input"]["entries"] = [{
            "data_path": "SIDE C",
            "session_id": 64
            },
            {
            "data_path": "SIDE A",
            "session_id": int(self.session_id)
            }]
        gds_manual_step.run(self.step)

        print("Checking latest session variables dictionary...")
        for data_path in ic.ampcs_session_information:
            if data_path["data_path"] == "SIDE A":
                self.assertEqual(data_path["session_id"], int(self.session_id))
            elif data_path["data_path"] == "SIDE C":
                self.assertEqual(data_path["session_id"], 64)

        print("Providing multiple data paths to the same session id")
        self.step["execution_user_input"]["entries"] = [{
            "data_path": "SIDE C",
            "session_id": int(self.session_id)
            },
            {
            "data_path": "SIDE A",
            "session_id": int(self.session_id)
            },
            {
            "data_path": "SIDE B",
            "session_id": int(self.session_id)
            },
            {
            "data_path": "SIDE D",
            "session_id": 300
            }]

        gds_manual_step.run(self.step)

        for data_path in ic.ampcs_session_information:
            if data_path["data_path"] == "SIDE A":
                self.assertEqual(data_path["session_id"], int(self.session_id))
            elif data_path["data_path"] == "SIDE B":
                self.assertEqual(data_path["session_id"], int(self.session_id))
            elif data_path["data_path"] == "SIDE C":
                self.assertEqual(data_path["session_id"], int(self.session_id))
            elif data_path["data_path"] == "SIDE D":
                self.assertEqual(data_path["session_id"], 300)

    def test_overwrite_session(self):

        print("Registering data path and session id...")
        self.step["execution_user_input"]["entries"] = [{
            "data_path": "SIDE C",
            "session_id": 90
            }]
        gds_manual_step.run(self.step)

        # check to see if SIDE C is now registered to session 90 and not 64
        session = ing_lib.get_session_information(self.step["execution_user_input"]["entries"][0]["data_path"])
        self.assertEqual(session, 90)

        print("Overwrite data path with another session id...")
        ing_lib.register_session("SIDE A", 50)

        session = ing_lib.get_session_information("SIDE A")
        self.assertEqual(session, 50)

        print("Checking latest session variables dictionary...")
        for data_path in ic.ampcs_session_information:
            if data_path["data_path"] == "SIDE A":
                self.assertEqual(data_path["session_id"], 50)
            elif data_path["data_path"] == "SIDE C":
                self.assertEqual(data_path["session_id"], 90)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
