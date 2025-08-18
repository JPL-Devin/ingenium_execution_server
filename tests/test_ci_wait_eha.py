import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import wait_eha_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
from datetime import datetime, timedelta
import test_util as util
import logging
import requests
from test_util import *
from sim_functions import *
import json

class WaitEHATests(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        # login and set header token
		get_ing_auth_header()
		get_auth_header()
		# load string eha data
		url = ing_lib.get_test_eha()
		eha_data = string_eha_channel()
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)

		if r.status_code == 204:
			print("String/Enum EHA data loaded")

		# load boolean eha data
		url = ing_lib.get_test_eha()
		eha_data = boolean_eha_channel()
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		if r.status_code == 204:
			print("Boolean EHA data loaded")

		# load integer eha data
		url = ing_lib.get_test_eha()
		eha_data = integer_eha_channel()
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		if r.status_code == 204:
			print("Integer EHA data loaded")

		# load float eha data
		url = ing_lib.get_test_eha()
		eha_data = float_eha_channel()
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		if r.status_code == 204:
			print("Float EHA data loaded")


		eha_data = signed_integer_eha_channel()
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		if r.status_code == 204:
			print("Float EHA data loaded")

	def setUp(self):

        # login and set header token
		get_ing_auth_header()
		get_auth_header()


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

		ing_lib.register_session("SIDE A", 10)

		self.input_time_format = '%Y-%jT%H:%M:%S'
		ert_start_time = datetime.strftime(datetime.utcnow(), self.input_time_format)

		self.step = {
			"execution_id": "10",
			"elem_id": "1",
			"step_type": "WAIT_EHA",
			"execution_user_input": {
				"start_time": "CURRENT_TIME",
				"lookback": 5,
				"timeout": 5,
				"entries": [
					{
					"channel_type": "FLIGHT",
					"channel_id": "DMX-5000",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "EU",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
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


	def test_multiple_ehas_like(self):

		self.step["execution_user_input"]["entries"] = [
				{
					"channel_type": "FLIGHT",
					"channel_id": "IMG-00023s",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
				},
				{
					"channel_type": "FLIGHT",
					"channel_id": "WRX-0001xfg",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
				},
				{
					"channel_type": "FLIGHT",
					"channel_id": "CMD-1000sdf",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
				}
		]

		response = wait_eha_step.run(self.step)


	def test_no_present_integer(self):

		url = ing_lib.get_test_eha()
		eha_data = configurable_eha_value("0", 0, "SIGNED_INT", "ABC-123")
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		if r.status_code == 204:
			print("Signed integer EHA data loaded")

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "ABC-123",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["0"]
				}]
		
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

	def test_no_present_float(self):

		url = ing_lib.get_test_eha()
		eha_data = configurable_eha_value("0.0", 0.0, "FLOAT", "ABC-456")
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		print(r.text)
		if r.status_code == 204:
			print("Float EHA data loaded")

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "ABC-456",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["0.0"]
				}]
		
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")


	def test_status_type(self):
		#DN's
		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [
				{
					"channel_type": "FLIGHT",
					"channel_id": "IMG-0261",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
				},
				{
					"channel_type": "FLIGHT",
					"channel_id": "WRX-0001",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
				},
				{
					"channel_type": "FLIGHT",
					"channel_id": "CMD-1000",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "VALUE",
					"verification_condition": "EQUAL",
					"verification_values": ["0"]
				}
		]

		response = wait_eha_step.run(self.step)

		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Greater than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Less than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Exclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-1", "10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Inclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0", "5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Change Equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "0",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Change Not Equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "1",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
					"channel_type": "FLIGHT",
					"channel_id": "IMG-0261",
					"channel_name": None,
					"data_path": "SIDE A",
					"dn_eu": "DN",
					"verify_on": "CHANGE",
					"verification_condition": "EQUAL",
					"verification_values": ["1"]
				}
				]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["EN"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Nominal: Equal Wait")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "FFF-0101",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)

		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Change Greater than")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Change Greater than or equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Change Less than")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Change Less than or equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")


		print("Nominal: Change Inclusive range")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0", "5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		print("Nominal: Change Exclusive range")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-1", "5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		# EU's

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["ENGAGE"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "ENGAGE")


		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["NULL"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "ENGAGE")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["NULL"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "ENGAGE")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["NULL"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["EN"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "ENGAGE")

		print("Nominal: Change Equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "ENGAGE",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["ENGAGE"]
				}]
		print('self.step', json.dumps(self.step, indent=4))
		response = wait_eha_step.run(self.step)
		print('response', json.dumps(response, indent=4))
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PENDING")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "")

		print("Nominal: Change Not Equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "ENGAGE",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["NULL"]
				}]
		print('self.step', json.dumps(self.step, indent=4))
		response = wait_eha_step.run(self.step)
		print('response', json.dumps(response, indent=4))
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PENDING")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "")

		print("Off-Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["15"]
				}]

		print('self.step', json.dumps(self.step, indent=4))
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
		print('response', json.dumps(response, indent=4))

		print("Off-Nominal: Greater than or Equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less than or Equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		print("Off-Nominal: Exclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		print("Off-Nominal: Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Not Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Non existent channel")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_REAL",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")


	def test_boolean_type(self):

		# DN's
		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)

		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Greater than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Less than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Exclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-1", "10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Inclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0", "5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Change Equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "0",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")


		print("Nominal: Change Not Equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "1",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["0"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "-1")

		#updated
		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["EN"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Nominal: Equal Wait")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "FFF-0101",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}]

		response = wait_eha_step.run(self.step)

		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Change Greater than")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "0",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Change Greater than or equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Change Less than")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Change Less than or equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Change Inclusive range")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0", "5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Change Exclusive range")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 0,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-1", "5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		#EU's
		print("BOOLEAN Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["True"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "True")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["False"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "True")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["False"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "True")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["False"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Change Equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "EU",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "True",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["True"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Nominal: Change Not Equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "EU",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "True",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["False"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["NU"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

		print("Off-Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Greater than or Equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less than or Equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		print("Off-Nominal: Exclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		print("Off-Nominal: Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Not Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")



	def test_integer_type(self):

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Greater than or equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Less than or equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Exclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-1", "25"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-1", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")
	
	def test_this(self):
		print("Nominal: Change Equal")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 15,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				},
				{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}			
			]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Change Not Equal")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Greater than")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-100"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Less than")

		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Greater than or equal")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["-100"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Less than or equal")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Inclusive range")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-100","20"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Exclusive range")
		ic.channel_variables["10:CMD-1000"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-100","20"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Off-Nominal: Change no matching record found")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_REAL_CHANNEL",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


	def test_float_type(self):

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["10.5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.5")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["30.5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Greater than or equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Less than or equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["30.5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Exclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-1", "30.5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-1", "30.5"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

	def test_no_matching_channels(self):
		pass
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "SSE",
				"channel_id": "WOW-1234",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": [-1, 0.1]
				}]

		response = wait_eha_step.run(self.step)
		status = response["execution"]["results"]["entries"][0]["verification_status"]
		self.assertEqual(status, "FAIL")



	def test_signed_integer_type(self):

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["10"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Greater than or equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["-1"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Less than or equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Exclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-1", "25"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-1", "20"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Change Equal")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Not Equal")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Greater than")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-100"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Less than")

		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["10"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Greater than or equal")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["-100"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Less than or equal")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["5"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Inclusive range")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["-100","20"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Exclusive range")
		ic.channel_variables["10:CMD-1001"] = {
			"channel_type": "SSE",
			"channel_id": "CMD-1001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				10
			],
			"dn": "0.0",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": 10,
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-100","20"]
				}]
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Off-Nominal: Change no matching record found")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_REAL_CHANNEL",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
				}]

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


	def test_wait_times(self):

		print("Nominal: wait full length for EHA with no results")

		url = ing_lib.get_forced_errors()
		error = forced_error_obj("/eha/realtime_multi", duration=8)
		requests.post(url, json=error, headers=ic.header, verify=False)

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_REAL_CHANNEL",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
		}]		
	
		response = wait_eha_step.run(self.step)
		print(json.dumps(response, indent=4))
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

		print("Nominal: wait full length for multiple EHA with no results")
		
		self.step["execution_user_input"]["entries"] = [
			{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_REAL_CHANNEL",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
			},
			{
				"channel_type": "FLIGHT",
				"channel_id": "ANOTHER_CHANNEL_NOT",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
			}			
		]		
	
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

		for entry in response["execution"]['results']['entries']:
			self.assertEqual(entry["verification_status"], "FAIL")


	def test_one_success_one_fail(self):
		
		print("Nominal: Two steps, first one succeeds, second one passes") 
		self.step["execution_user_input"]["entries"] = [
			{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["0"]
			},
			{
				"channel_type": "FLIGHT",
				"channel_id": "ANOTHER_CHANNEL_NOT",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
			}			
		]		
	
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

		for entry in response["execution"]["results"]["entries"]:
			if entry["channel_id"] == "WRX-1000":
				entry["verification_status"] == "PASS"
			elif entry["channel_id"] == "ANOTHER_CHANNEL_NOT":
				entry["verification_status"] == "FAIL"

	def test_one_fail_one_success(self):
		pass
		print("Nominal: Two steps, first one fails, second one succeeds")

		url = ing_lib.get_forced_errors()
		error = forced_error_obj("/eha/realtime_multi", duration=8)
		requests.post(url, json=error, headers=ic.header, verify=False)

		self.step["execution_user_input"]["entries"] = [
			{
				"channel_type": "FLIGHT",
				"channel_id": "ANOTHER_CHANNEL_NOT",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
			},				
			{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["0"]
			}		
		]		

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
		
		for entry in response["execution"]["results"]["entries"]:
			if entry["channel_id"] == "WRX-1000":
				entry["verification_status"] == "PASS"
			elif entry["channel_id"] == "ANOTHER_CHANNEL_NOT":
				entry["verification_status"] == "FAIL"

	def test_two_fail_two_success(self):
		pass
		print("Nominal: Four steps, FAIL-PASS-FAIL-PASS")

		url = ing_lib.get_forced_errors()
		error = forced_error_obj("/eha/realtime_multi", duration=8)
		requests.post(url, json=error, headers=ic.header, verify=False)

		self.step["execution_user_input"]["entries"] = [
			{
				"channel_type": "FLIGHT",
				"channel_id": "ANOTHER_CHANNEL_NOT",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
			},				
			{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["0"]
			},
			{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_THE_DROIDS",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
			},		
			{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["0"]
			}				
		]		

		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
		
		for entry in response["execution"]["results"]["entries"]:
			if entry["channel_id"] in ["WRX-1000", "NOT_THE_DROIDS"]:
				entry["verification_status"] == "PASS"
			elif entry["channel_id"] in ["ANOTHER_CHANNEL_NOT", "NOT_THE_DROIDS"]:
				entry["verification_status"] == "FAIL"


	def test_error_returned_from_venue_server(self):
		pass
		print("Nominal: Error returned from venue server")

		url = ing_lib.get_forced_errors()
		error = forced_error_obj("/eha/realtime_multi", errorflag="404", errormsg={"message": "SERVER ERROR"}, duration=0)
		r = requests.post(url, json=error, headers=ic.header, verify=False)
		print(r.text)

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "NOT_REAL_CHANNEL",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["15"]
		}]		
	
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

	def test_time_formats(self):
		pass
		self.step["execution_user_input"] = {
			"start_time": "CURRENT_TIME",
			"timeout": 30,
			"lookback": 30,
			"entries": [
				{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15"]
				}
			]
		}

		# DOY format
		self.step["execution_user_input"]["start_time"] = "2018-364T12:00:00"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# ISO/UTC format
		self.step["execution_user_input"]["start_time"] = "2018-12-30T12:00:00"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# CURRENT_TIME
		self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# LAST STEP START
		ic.time_references['LAST_STEP_START'] = "2018-12-30T12:00:00.123Z"
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_START"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# LAST STEP END
		ic.time_references['LAST_STEP_END'] = "2018-12-30T12:00:00.123Z"
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_END"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# LAST STEP START - ERROR
		ic.time_references['LAST_STEP_START'] = ""
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_START"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		# LAST STEP END - ERROR
		ic.time_references['LAST_STEP_END'] = ""
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_END"
		response = wait_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
