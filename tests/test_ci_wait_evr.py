import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import wait_evr_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
from datetime import datetime, timedelta
import test_util as util
import logging
import requests
import json
from test_util import *
from sim_functions import *



class WaitEVRTests(unittest.TestCase):

    def setUp(self):

        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        # ic.run_mode = 'ASYNC'
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        """
        ing_lib.ShutdownMTAK()

        # start an MTAK session
        print("Starting MTAK session: {}".format(session_id))
        ing_lib.StartMTAK(session=[int(session_id)])
        """

        ing_lib.register_session("SIDE B", 305)

        self.input_time_format = '%Y-%jT%H:%M:%S'
        ert_start_time = datetime.strftime(datetime.utcnow(), self.input_time_format)
        ert_end_time = datetime.strftime(datetime.utcnow(), self.input_time_format)

        self.step = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "WAIT_EVR",
            "execution_user_input": {
                "data_path": "SIDE B",
                "start_time": "CURRENT_TIME",
                "lookback": 0,
                "timeout": 5,
                "entries": [
                {
                    "evr_name": ic.binary_file_evr_name,
                    "evr_id": "",
                    "evr_type": "",
                    "evr_level": "",
                    "message_filter": "",
                    "verification_condition": "EXISTS"
                }              
                ]
            },
            "execution": {
                "meta_data": {
                    "time_started": 123123123,
                    "status": ""
                },
                "results": {}
            }
        }

        print("Nominal EVRs added")
        url = ing_lib.get_test_evr()
        evr_data = test_evr_obj(5, evr_name=ic.binary_file_evr_name, evr_message="ACS_THRUSTER")
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

        evr_data = test_evr_obj(5, evr_name="ANOTHER_EVR", evr_message="EDL_ROVER")
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

    def tearDown(self):

        pass


    def test_ideal_scenario(self):

        print("All nominal inputs")
        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

    def test_filtering_realtime(self):

        print("Filtering SSE/FSW evrs (using realtime)")
        # post evr data - 3 sse entries and 1 fsw recorded and 2 fsw realtime
        evr_data = [
            {
                "evrName": "test_evr_sse",
                "sessionId": 0,
                "vcId": 0,
                "eventId": 0,
                "evrLevel": "string",
                "fromSSE": True,
                "evrMessage": "test",
                "evrModule": "string",
                "sclk": get_current_time_str(),
                "ert": get_current_utc(),
                "scet": get_current_utc(),
                "isRecorded": False
          },
           {
                "evrName": "test_evr_fsw_recorded",
                "sessionId": 0,
                "vcId": 0,
                "eventId": 0,
                "evrLevel": "string",
                "fromSSE": False,
                "evrMessage": "test",
                "evrModule": "string",
                "sclk": get_current_time_str(),
                "ert": get_current_utc(),
                "scet": get_current_utc(),
                "isRecorded": True
          },
           {
                "evrName": "test_evr_sse",
                "sessionId": 0,
                "vcId": 0,
                "eventId": 0,
                "evrLevel": "string",
                "fromSSE": True,
                "evrMessage": "test",
                "evrModule": "string",
                "sclk": get_current_time_str(),
                "ert": get_current_utc(),
                "scet": get_current_utc(),
                "isRecorded": False
          },
           {
                "evrName": "test_evr_fsw_realtime",
                "sessionId": 0,
                "vcId": 0,
                "eventId": 0,
                "evrLevel": "string",
                "fromSSE": False,
                "evrMessage": "test",
                "evrModule": "string",
                "sclk": get_current_time_str(),
                "ert": get_current_utc(),
                "scet": get_current_utc(),
                "isRecorded": False
          },
           {
                "evrName": "test_evr_sse",
                "sessionId": 0,
                "vcId": 0,
                "eventId": 0,
                "evrLevel": "string",
                "fromSSE": True,
                "evrMessage": "test",
                "evrModule": "string",
                "sclk": get_current_time_str(),
                "ert": get_current_utc(),
                "scet": get_current_utc(),
                "isRecorded": False
          },
           {
                "evrName": "test_evr_fsw_realtime",
                "sessionId": 0,
                "vcId": 0,
                "eventId": 0,
                "evrLevel": "string",
                "fromSSE": False,
                "evrMessage": "test",
                "evrModule": "string",
                "sclk": get_current_time_str(),
                "ert": get_current_utc(),
                "scet": get_current_utc(),
                "isRecorded": False
          },          
        ]

        url = ing_lib.get_test_evr()
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)
        print(r.status_code, r.text)

        # run tests
        # search for sse types
        self.step["execution_user_input"]["entries"] = [{
            "evr_name": "test_evr_sse",
            "evr_id": None,
            "evr_type": "SSE",
            "evr_level": None,
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        entries = response["execution"]["results"]["entries"][0]["evr_data"]
        
        for entry in entries: 
            self.assertEqual(entry.get("evr_name"), "test_evr_sse")
        
        # search for fsw recorded
        self.step["execution_user_input"]["entries"] = [{
            "evr_name": "test_evr_fsw_recorded",
            "evr_id": None,
            "evr_type": "FSW_RECORDED",
            "evr_level": None,
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        entries = response["execution"]["results"]["entries"][0]["evr_data"]
        
        for entry in entries: 
            self.assertEqual(entry.get("evr_name"), "test_evr_fsw_recorded")        

        # search for fsw realtime type
        self.step["execution_user_input"]["entries"] = [{
            "evr_name": "test_evr_fsw_realtime",
            "evr_id": None,
            "evr_type": "FSW_REALTIME",
            "evr_level": None,
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        entries = response["execution"]["results"]["entries"][0]["evr_data"]

        for entry in entries: 
            self.assertEqual(entry.get("evr_name"), "test_evr_fsw_realtime")

    def test_no_returned_data(self):

        print("Load no evr data")
        url = ing_lib.get_test_evr()
        evr_data = []
        requests.post(url, json=evr_data, headers=ic.header, verify=False)

        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", duration=8)
        requests.post(url, json=error, headers=ic.header, verify=False)


        self.step["execution_user_input"]["entries"] = [{
            "evr_name": "NAME_HERE",
            "evr_id": None,
            "evr_type": None,
            "evr_level": None,
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")


    def test_no_matching_evr_id(self):

        print("Load no evr data")
        url = ing_lib.get_test_evr()
        evr_data = []
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", duration=8)
        requests.post(url, json=error, headers=ic.header, verify=False)


        self.step["execution_user_input"]["entries"] = [
            {
                "evr_name": None,
                "evr_id": 123,
                "evr_type": None,
                "evr_level": None,
                "message_filter": None,
                "verification_condition": "EXISTS"
            },
            {
                "evr_name": "THIS_IS_NOT_THE_ONE",
                "evr_id": 123,
                "evr_type": None,
                "evr_level": None,
                "message_filter": None,
                "verification_condition": "EXISTS"
            }

        ]
        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
        
        for entry in response["execution"]['results']['entries']:
            self.assertEqual(entry["verification_status"], "FAIL")



    def test_no_matching_evr_type(self):

        print("Load no evr data")
        url = ing_lib.get_test_evr()
        evr_data = []
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", duration=8)
        requests.post(url, json=error, headers=ic.header, verify=False)

        self.step["execution_user_input"]["entries"] = [{
            "evr_name": None,
            "evr_id": None,
            "evr_type": "FSW_NOT_HERE",
            "evr_level": None,
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        # evr_type is constrained by Ingenium. If a wrong evr_type is provided,
        # that is an Ingenium error.
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")


    def test_no_matching_evr_level(self):

        print("Load no evr data")
        url = ing_lib.get_test_evr()
        evr_data = []
        r = requests.post(url, json=evr_data, headers=ic.header, verify=False)

        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", duration=8)
        requests.post(url, json=error, headers=ic.header, verify=False)

        self.step["execution_user_input"]["entries"] = [{
            "evr_name": None,
            "evr_id": None,
            "evr_type": None,
            "evr_level": "NOT_REAL",
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

    def test_mixed_up_stuff(self):

        url = ing_lib.get_test_evr()
        evr_data = test_evr_obj(5, evr_name=ic.binary_file_evr_name, evr_message="ACS_THRUSTER")
        requests.post(url, json=evr_data, headers=ic.header, verify=False)

        self.step["execution_user_input"]["entries"] = [{
            "evr_name": "HISTORY_WORD_OVERFLOW",
            "evr_id": 123,
            "evr_type": None,
            "evr_level": None,
            "message_filter": None,
            "verification_condition": "EXISTS"
        }]
        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")


    def test_forced_error_408(self):

        print("Force a 408 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", errorflag="408", errormsg={"message": "TIME OUT"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


    def test_forced_error_404(self):

        print("Force a 404 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", errorflag="404", errormsg={"message": "RESOURCE NOT FOUND"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    def test_forced_error_500(self):

        print("Force a 500 error")
        url = ing_lib.get_forced_errors()
        error = forced_error_obj("/evr/realtime", errorflag="500", errormsg={"message": "THERE WAS AN ERROR"})
        r = requests.post(url, json=error, headers=ic.header, verify=False)

        response = wait_evr_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))