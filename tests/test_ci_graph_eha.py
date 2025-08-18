import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import graph_eha_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import time
from test_util import get_test_time
import requests
from test_util import *
from sim_functions import *



class GraphEHATests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # load string eha data
        get_auth_header()
        get_ing_auth_header()
        get_venue_sim_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")

        url = ing_lib.get_test_eha()
        eha_data = graph_eha_test_data(6)
        r = requests.post(url, json=eha_data, headers=tc.venue_header, verify=False)
        print(r.text)
        if r.status_code == 204:
            print("Graph EHA data loaded")

    def setUp(self):

        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=tc.venue_header, verify=False)

        # login and set header token
        get_auth_header()

        """
        print("Shutting down MTAK session...")
        ing_lib.ShutdownMTAK()

        print("Starting MTAK session: {}".format(session_id))
        ing_lib.StartMTAK(session=[int(session_id)])
        """

        # register session for testing
        ing_lib.register_session("SIDE A", 10)

        # get test times
        start_time, end_time = get_test_time()


        # base step json. Unit tests simply manipulate inputs to exact specific responses.
        self.step = {
            "elem_id": "uuid-step-4",
            "elem_type": "STEP",
            "execution_id": "uuid-execution-12",
            "description": "A step to update the venue configuration",
            "number": "1-4",
            "step_type": "GRAPH_EHA",
            "variable": {"name": "sample_variable"},
            "code": {
                "name": "eha_graph.run",
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
                "channel_id": "",
                "channel_name": "",
                "start_time": "",
                "end_time": "",
                "duration": None,
                "time_type": "",
                "timeout": 240,
                "channel_type": "",
                "dn_eu": "",
                "data_path": ""
            },
            "execution_user_input": {
                "channel_id": "GRP-1500",
                "start_time": start_time,
                "end_time": end_time,
                "duration": None,
                "time_type": "ERT",
                "timeout": 20,
                "channel_type": "FSW_RECORDED",
                "dn_eu": "DN",
                "data_path": "SIDE A"
            },
            "execution": {
                "meta_data": {
                    "test_conductor": "hongmank",
                    "status": "PASS",
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

    def test_ideal_scenario(self):

        print("Testing ideal scenario, with all required variables correctly formmatted...")
        graph = graph_eha_step.run(self.step)
        self.assertEqual(graph["execution"]["meta_data"]["status"], "PASS")
        data = graph["execution"]["results"]["channel_data"]
        self.assertEqual(len(data), 6)


    def test_different_channelid_inputs(self):


        print("Providing an unknown channel id")
        self.step["execution_user_input"]["channel_id"] = "HEY-1230"
        graph = graph_eha_step.run(self.step)
        self.assertEqual(graph["execution"]["results"]['channel_data'], [])

        print("Providing an integer as a channel id...")
        self.step["execution_user_input"]["channel_id"] = 9876
        graph = graph_eha_step.run(self.step)
        self.assertEqual(graph["execution"]["results"]['channel_data'], [])


    def test_ideal_scenario_returns_none(self):
        print("Testing Chill EVR endpoint with correct data, but no EVR data is returned...")
        self.step["execution_user_input"]["channel_id"] = "HEY-1230"
        self.step["execution_user_input"]["start_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["end_time"] = "2016-219T19:07:00"
        self.step["execution_user_input"]["time_type"] = "ERT"
        graph = graph_eha_step.run(self.step)
        self.assertEqual(graph["execution"]["results"]['channel_data'], [])


    def test_valid_inputs_with_SCET_time(self):
        print("Testing SCET time format, with correctly formattted parameters...")
        self.step_user_input["start_time"] = "2017-234T19:40:22"
        self.step_user_input["end_time"] = "2017-234T19:42:21"
        self.step_user_input["time_type"] = "SCET"
        graph = graph_eha_step.run(self.step)
        self.assertEqual(graph["execution"]["meta_data"]["status"], "PASS")
        data = graph["execution"]["results"]["channel_data"]
        self.assertEqual(len(data), 6)



    def test_malformed_datetime_formatting(self):

        print("Testing input SCLK time format for SCET time type...")
        self.step["execution_user_input"]["start_time"] = "527925356"
        self.step["execution_user_input"]["end_time"] = "527925400"
        self.step["execution_user_input"]["time_type"] = "SCET"
        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


        print("Testing input SCET time format (UTC) for SCLK time type...")
        self.step["execution_user_input"]["start_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["end_time"] = "2016-200T12:42:00"
        self.step["execution_user_input"]["time_type"] = "SCLK"
        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Inputting both start and end date, with a duration returns an error... ")
        self.step["execution_user_input"]["start_time"] = "2016-200T12:41:30"
        self.step["execution_user_input"]["end_time"] = "2016-200T12:42:00"
        self.step["execution_user_input"]["time_type"] = "SCET"
        self.step["execution_user_input"]["duration"] = 600
        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

        print("Inputting an incorrect datetime format for SCET will return an error...")
        self.step["execution_user_input"]["start_time"] = "2017-01-01T18:07:59"
        self.step["execution_user_input"]["end_time"] = "2017-01-04T19:07:0"
        self.step["execution_user_input"]["time_type"] = "SCET"
        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


    def test_invalid_session_id(self):

        print("Testing when data path is not found in sessions/data path list, throws an error...")
        self.step["execution_user_input"]["data_path"] = "SIDE_A"
        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


    def test_forced_error_404(self):

        print("Force a 404 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/eha/chill", errorflag="404", errormsg={"message": "RESOURCE NOT FOUND"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_errors_500(self):

        print("Force a 500 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/eha/chill", errorflag="500", errormsg={"message": "SERVER ERROR"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_errors_408(self):

        print("Force a 408 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/eha/chill", errorflag="408", errormsg={"message": "TIMED OUT!"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = graph_eha_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
