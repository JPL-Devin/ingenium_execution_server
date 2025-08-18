import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import verify_eha_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
from datetime import datetime, timedelta
import test_util as util
import logging
import requests
from test_util import get_ing_auth_header, get_auth_header, get_current_utc
from sim_functions import string_eha_channel, boolean_eha_channel, integer_eha_channel, float_eha_channel, signed_integer_eha_channel, \
	any_string_eha_channel, configurable_eha_value
import copy
import json


class VerifyEHATests(unittest.TestCase):

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


		url = ing_lib.get_test_eha()
		eha_data = signed_integer_eha_channel()
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)
		if r.status_code == 204:
			print("Signed Int data loaded")



	def setUp(self):

		# login and set header token
		get_ing_auth_header()
		get_auth_header()

		print("Clear any endpoints")
		url = ing_lib.get_forced_errors()
		forced_error = ["ALL"]
		r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)


		# ing_lib.ShutdownMTAK()
		#
		# # start an MTAK session
		# print("Starting MTAK session: {}".format(session_id))
		# ing_lib.StartMTAK(session=[int(session_id)])


		ing_lib.register_session("SIDE A", 10)

		self.input_time_format = '%Y-%jT%H:%M:%S'
		self.ert_start_time = datetime.strftime(datetime.utcnow(), self.input_time_format)

		self.step = {
		"execution_id": "10",
		"elem_id": "1",
		"step_type": "VERIFY_EHA",
		"execution_user_input": {
				"start_time": "CURRENT_TIME",
				"timeout": 5,
				"lookback": 0,
				"entries": [
				{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["FALSE"]
				}
		]
		},
		"execution": {
				"meta_data": {
					"time_started": 12323
				},
				"results": {}
		}
		}

	def tearDown(self):
		pass

	def test_multiple(self):
		'''
		ehas = ing_lib.RealtimeEHA(data_path='SIDE A', channel_id='ING-123142', 
		    start_time=get_current_utc(), end_time=get_current_utc(), timeout=5,
		    min_results=0)
		print(f'test_multiple before ehas: {json.dumps(ehas, indent=4)}')
		'''

		url = ing_lib.get_test_eha()
		eha_data = any_string_eha_channel("PASS", "ING-123142")
		r = requests.post(url, json=eha_data, headers=ic.header, verify=False)

		self.assertEqual(r.status_code, 204)

		if r.status_code == 204:
			print("String/Enum EHA data loaded")

		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "ING-63452243234",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["P"]
				},
				{
				"channel_type": "FLIGHT",
				"channel_id": "ING-123142",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["P"]
				},				
				{
				"channel_type": "FLIGHT",
				"channel_id": "ING-123142",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["P"]
				},
		
		]
		
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")
		self.assertEqual(response["execution"]["results"]["entries"][1]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][2]["verification_status"], "PASS")

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
		
		response = verify_eha_step.run(self.step)
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
		
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

	def test_status_type(self):
        # DN
		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["0"]
				}]

		response = verify_eha_step.run(self.step)
		
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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
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
				},
				{
				"channel_type": "FLIGHT",
				"channel_id": "YH-5632",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["1"]
				},
				{
				"channel_type": "FLIGHT",
				"channel_id": "FG-01231",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["1"]
				},
				{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["1"]
				}			
				]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")


		print("Nominal: Greater than")
		# make a copy not to be affected by the previous tests
		step = copy.deepcopy(self.step)
		print(json.dumps(step, indent=4))
		step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["-1"]
				}]

		response = verify_eha_step.run(step)
		print(json.dumps(response, indent=4))
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Less than")
		step = copy.deepcopy(self.step)
		step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["15"]
				}]

		response = verify_eha_step.run(step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Greater than or Equal to")
		step = copy.deepcopy(self.step)
		step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["0"]
				}]

		response = verify_eha_step.run(step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Less than or Equal to")
		step = copy.deepcopy(self.step)
		step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["15"]
				}]

		response = verify_eha_step.run(step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Exclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["-1", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Nominal: Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Not Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		# EU's with Channel Type String
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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Off-Nominal: Greater Than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		print("Off-Nominal: Greater Than or Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Exclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["1", "2"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Inclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["1", "2"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


		# EU's with channel type integer
		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["10.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Not Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["10.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Record")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "RECORD",
				"verification_values": ["10.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Not Present")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "NOT_PRESENT",
				"verification_values": ["10.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Nominal: Greater than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["0.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Greater than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["10.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Less than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["100.5S"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PENDING")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "")

		print("Nominal: Less than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["10.0"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Exclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["0.5", "11.4"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Nominal: Inclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0.5", "10.0"]
				}]


		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

	def test_boolean_type(self):

		# DN tests
		print("BOOLEAN Nominal: Equal")
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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1"]
				}]

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
		print(response)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "0")

		print("Off-Nominal: Contains")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "CONTAINS",
				"verification_values": ["NU"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["15"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")


		print("Nominal: Greater than or Equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["-1"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Less than or Equal to")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["15"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Exclusive range")
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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Nominal: Inclusive range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["0", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		print("Off-Nominal: Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Not Equal with more than 1 ver. value")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "VALUE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["15", "20"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		# EU's with Channel type boolean
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

		response = verify_eha_step.run(self.step)
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
				"verification_condition": "EQUAL",
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")

		print("Off-Nominal: Greater Than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN",
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less Than")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Greater Than or Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "GREATER_THAN_OR_EQUAL",
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Less than or equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN_OR_EQUAL",
				"verification_values": ["True"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Exclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EXCLUSIVE_RANGE",
				"verification_values": ["1", "2"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		print("Off-Nominal: Inclusive Range")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "INCLUSIVE_RANGE",
				"verification_values": ["1", "2"]
				}]

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["10"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "FAIL")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1000"]
				}]

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["1000"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["-1", "5000"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["-1", "4000"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

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
				"verification_condition": "EQUAL",
				"verification_values": ["5"]
				}]
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

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
				"verification_values": ["-5"]
				}]
		response = verify_eha_step.run(self.step)
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
				"verification_values": ["-10"]
				}]
		response = verify_eha_step.run(self.step)
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
				"verification_values": ["6"]
				},
				{
				"channel_type": "FLIGHT",
				"channel_id": "CMD-1000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "DN",
				"verify_on": "CHANGE",
				"verification_condition": "LESS_THAN",
				"verification_values": ["6"]
				}				
			]
		response = verify_eha_step.run(self.step)
		print(response)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")
		self.assertEqual(response["execution"]["results"]["entries"][1]["actual_value"], "5")
	
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
				"verification_values": ["-6"]
				}]
		response = verify_eha_step.run(self.step)
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
				"verification_values": ["6"]
				}]
		response = verify_eha_step.run(self.step)
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
				"verification_values": ["10","5"]
				}]
		response = verify_eha_step.run(self.step)
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
				"verification_values": ["10","1"]
				}]
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

    #need a channel to get float
	def test_float_type(self):

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
				"channel_type": "FLIGHT",
				"channel_id": "DMX-5000",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "VALUE",
				"verification_condition": "EQUAL",
				"verification_values": ["20.7"]
				}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "20.7")

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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["100"]
				}]

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["100.7"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["-1", "100"]
				}]

		response = verify_eha_step.run(self.step)
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
				"verification_values": ["-1", "100"]
				}]

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

	def test_no_matching_channels(self):

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

		response = verify_eha_step.run(self.step)
		status = response["execution"]["results"]["entries"][0]["verification_status"]
		self.assertEqual(status, "FAIL")
	
	def test_off_nom_scen(self):

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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

	def test_change_strings_boolean(self):

		# STRING, EQUAL
		print("Nominal: Channel type: String, Equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "EU",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				"ENGAGE"
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
				"channel_type": "SSE",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["ENGAGE"]
				}]
		response = verify_eha_step.run(self.step)

		# STRING, NOT_EQUAL
		print("Nominal: Channel type: String, Not Equal")
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "EU",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				"ENGAGE"
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
				"channel_type": "SSE",
				"channel_id": "IMG-0261",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["STOP"]
				}]
		response = verify_eha_step.run(self.step)
		status = response["execution"]["meta_data"]["status"]
		self.assertEqual(status, "ERROR")

		# BOOLEAN, EQUAL
		print("Nominal: Channel type: Boolean, Equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "EU",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				"False"
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
				"channel_type": "SSE",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "EQUAL",
				"verification_values": ["True"]
				}]
		response = verify_eha_step.run(self.step)
		status = response["execution"]["meta_data"]["status"]
		self.assertEqual(status, "ERROR")


		# BOOLEAN, NOT_EQUAL
		print("Nominal: Channel type: Boolean, Not Equal")
		ic.channel_variables["10:WRX-0001"] = {
			"channel_type": "SSE",
			"channel_id": "WRX-0001",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "EU",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
				"False"
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
				"channel_type": "SSE",
				"channel_id": "WRX-0001",
				"channel_name": None,
				"data_path": "SIDE A",
				"dn_eu": "EU",
				"verify_on": "CHANGE",
				"verification_condition": "NOT_EQUAL",
				"verification_values": ["False"]
				}]
		response = verify_eha_step.run(self.step)
		status = response["execution"]["meta_data"]["status"]
		self.assertEqual(status, "ERROR")



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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Equal")
		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "FLIGHT",
			  "channel_id": "CMD-1001",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "VALUE",
			  "verification_condition": "EQUAL",
			  "verification_values": ["10"]
			  }]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "10.0")

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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["1000"]
			  }]

		response = verify_eha_step.run(self.step)
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

		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["1000"]
			  }]

		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["-1", "5000"]
			  }]

		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["-1", "4000"]
			  }]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "15")

		print("Nominal: Change Equal")
		ic.channel_variables["10:CMD-1001"] = {
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
			  "channel_id": "CMD-1001",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "DN",
			  "verify_on": "CHANGE",
			  "verification_condition": "EQUAL",
			  "verification_values": ["5"]
			  }]
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

		print("Nominal: Change Not Equal")
		ic.channel_variables["10:CMD-1001"] = {
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
			  "channel_id": "CMD-1001",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "DN",
			  "verify_on": "CHANGE",
			  "verification_condition": "NOT_EQUAL",
			  "verification_values": ["-5"]
			  }]
		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["-10"]
			  }]
		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["6"]
			  }]
		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["-6"]
			  }]
		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["6"]
			  }]
		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["10","5"]
			  }]
		response = verify_eha_step.run(self.step)
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
			  "verification_values": ["10","1"]
			  }]
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")
		self.assertEqual(response["execution"]["results"]["entries"][0]["actual_value"], "5")

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

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")


	def test_time_formats(self):

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
		response = verify_eha_step.run(self.step)
		print(response)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# ISO/UTC format
		self.step["execution_user_input"]["start_time"] = "2018-12-30T12:00:00"
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# CURRENT_TIME
		self.step["execution_user_input"]["start_time"] = "CURRENT_TIME"
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# LAST STEP START
		ic.time_references['LAST_STEP_START'] = "2018-12-30T12:00:00.123Z"
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_START"
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# LAST STEP END
		ic.time_references['LAST_STEP_END'] = "2018-12-30T12:00:00.123Z"
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_END"
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# LAST STEP START - ERROR
		ic.time_references['LAST_STEP_START'] = ""
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_START"
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		# LAST STEP END - ERROR
		ic.time_references['LAST_STEP_END'] = ""
		self.step["execution_user_input"]["start_time"] = "LAST_STEP_END"
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

	def test_eu_string_booleans(self):

		# Selected EU. Channel will return a STATUS (string) response. Expecting ERROR
		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "SSE",
			  "channel_id": "IMG-0261",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "VALUE",
			  "verification_condition": "EXCLUSIVE_RANGE",
			  "verification_values": [-1, 0.1]
		}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		# Selected EU. Channel will return a STATUS (string) response. This case is a PASS
		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "SSE",
			  "channel_id": "IMG-0261",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "VALUE",
			  "verification_condition": "EQUAL",
			  "verification_values": ["ENGAGE"]
		}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")


		# Selected EU. Channel will return a Boolean response. Expecting ERROR
		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "SSE",
			  "channel_id": "WRX-0001",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "VALUE",
			  "verification_condition": "EXCLUSIVE_RANGE",
			  "verification_values": [-1, 0.1]
		}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		# Selected EU. Channel will return a Boolean response. This case is a PASS
		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "SSE",
			  "channel_id": "WRX-0001",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "VALUE",
			  "verification_condition": "EQUAL",
			  "verification_values": ["True"]
		}]

		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

		# Additional test to make sure on change is working as expected

		#Integer, on change, nominal
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
			"dn": "1",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "10",
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
			  "verification_values": ["5"]
			  }]
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")

		# Integer, on change, off nominal
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
			"dn": "1",
			"eu": 12,
			"session_id": 0,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "HELLO",
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
			  }]
		response = verify_eha_step.run(self.step)
		print(response)
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		#Float, on change, nominal
		print('ampcs_session_information', json.dumps(ic.ampcs_session_information, indent=4))
		ic.channel_variables["10:DMX-5000"] = {
			"channel_type": "SSE",
			"channel_id": "DMX-5000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
			  10
			],
			"dn": "1",
			"eu": 12,
			"session_id": 10,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "100.0",
			"verification_status": "PASS"
		}

		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "FLIGHT",
			  "channel_id": "DMX-5000",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "CHANGE",
			  "verification_condition": "LESS_THAN",
			  "verification_values": ["90"]
			  }]
		response = verify_eha_step.run(self.step)
		self.assertEqual(response["execution"]["results"]["entries"][0]["verification_status"], "PASS")		

		# Float, on change, off nominal
		ic.channel_variables["10:DMX-5000"] = {
			"channel_type": "SSE",
			"channel_id": "DMX-5000",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "RECORD",
			"verification_values": [
			  10
			],
			"dn": "1",
			"eu": 12,
			"session_id": 10,
			"channel_status": "string",
			"sclk": "string",
			"ert": "string",
			"scet": "string",
			"actual_value": "WRONG",
			"verification_status": "PASS"
		}
		self.step["execution_user_input"]["entries"] = [{
			  "channel_type": "FLIGHT",
			  "channel_id": "DMX-5000",
			  "channel_name": None,
			  "data_path": "SIDE A",
			  "dn_eu": "EU",
			  "verify_on": "CHANGE",
			  "verification_condition": "LESS_THAN",
			  "verification_values": ["90"]
			  }]
		self.step["execution"]["meta_data"] = {
			"time_started": "",
			"status": "PENDING",
			"error": {},
			"time_completed": "",
			"time_updated": "",
			"status_message": ""
		}
		print('self.step', json.dumps(self.step, indent=4))
		response = verify_eha_step.run(self.step)
		print('response', json.dumps(response, indent=4))	
		self.assertEqual(response["execution"]["meta_data"]["status"], "ERROR")

		# String, on change, nominal
		ic.channel_variables["10:IMG-0261"] = {
			"channel_type": "SSE",
			"channel_id": "IMG-0261",
			"channel_name": "string",
			"data_path": "string",
			"dn_eu": "DN",
			"verify_on": "VALUE",
			"verification_condition": "CHANGE",
			"verification_values": [
			  10
			],
			"dn": "1",
			"eu": 12,
			"session_id": 10,
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
		response = verify_eha_step.run(self.step)
		print('response', json.dumps(response, indent=4))
		status = response["execution"]["meta_data"]["status"]
		self.assertEqual(status, "ERROR")

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
			"dn": "1",	
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
		response = verify_eha_step.run(self.step)	
		status = response["execution"]["meta_data"]["status"]
		self.assertEqual(status, "ERROR")		

if __name__ == '__main__':
	unittest.main()

