import xmlrunner
import unittest
import os
import sys
import json
from collections import OrderedDict
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import custom_script_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
from datetime import datetime, timedelta
import test_util as util
import logging
import copy
import requests
from test_util import *
from sim_functions import *


class CustomScriptTests(unittest.TestCase):
    def setUp(self):
        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        print("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)        

        ing_lib.register_session("SIDE A", 34)

        self.step = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "CUSTOM_SCRIPT",
            "execution_user_input": {
                "script_name": "my script one",
                "script_path": "path1/path2/py_script.py",
                "script_id": "1234abcd",
                "description": "test script",
                "hash": "abcdefg",
                "status": "ACTIVE",                                
                "timeout": 30,
                "inputs": [
                    {
                        "name": "var1",
                        "description": "first input var",
                        "phase": "AUTHORING",
                        "required": "YES",
                        "type": "INT",
                        "enumerations": [],
                        "value": "1"                                                                                                                     
                    },
                    {
                        "name": "var2",
                        "description": "second input var",
                        "phase": "AUTHORING",
                        "required": "NO",
                        "type": "ENUM",
                        "enumerations": [{"symbol": "SMALL"}, {"symbol": "MEDIUM"}, {"symbol": "LARGE"}],
                        "value": "MEDIUM"                                                                                                                     
                    },
                    {
                        "name": "var3",
                        "description": "second input var",
                        "phase": "EXECUTION",
                        "required": "YES",
                        "type": "BOOL",
                        "enumerations": [],
                        "value": "true"                                                                                                                     
                    }                                           
                ],
                "entries": [
                    {
                        "display_field": "out_var1",
                        "verification_status": "PENDING",
                        "entry_inputs": [
                            {
                                "name": "entry1",
                                "description": "First entry",
                                "phase": "AUTHORING",
                                "required": "YES",
                                "type": "INT",
                                "enumerations": [],
                                "value": "1"
                            },
                            {
                                "name": "entry2",
                                "description": "Second entry",
                                "phase": "EXECUTION",
                                "required": "NO",
                                "type": "INT",
                                "enumerations": [],
                                "value": "2"
                            }                                        
                        ],
                        "entry_outputs": [
                            {
                                "name": "out_var1",
                                "description": "First output variable",
                                "type": "INT"                                                                                                             
                            },
                            {
                                "name": "out_var2",
                                "description": "Second output variable",
                                "type": "INT"                                                                                                             
                            }                                        
                        ],
                        "entry_output_array": {
                            "name": "detail_data",
                            "description": "detail data of the entry",
                            "max_entries": 10,
                            "outputs": [
                                {
                                    "name": "detail_var1",
                                    "description": "Detailed variable 1",
                                    "visible": "YES",
                                    "type": "INT"
                                },
                                {
                                    "name": "detail_var2",
                                    "description": "Detailed variable 2",
                                    "visible": "YES",
                                    "type": "INT"
                                },
                                {
                                    "name": "detail_var3",
                                    "description": "Detailed variable 3",
                                    "visible": "NO",
                                    "type": "INT"
                                }                                                                                            
                            ]         
                        }
                    }
                ],
                "outputs": [
                    {
                        "name": "out1",
                        "description": "first output",
                        "type": "INT"                                                                                                             
                    },
                    {
                        "name": "out2",
                        "description": "second output",
                        "type": "INT"                                                                                                             
                    }                
                ],
                "output_array": {
                    "name": "output_array_var",
                    "description": "The only output array var",
                    "max_entries": 10,
                    "outputs": [
                        {
                            "name": "output_array_field1",
                            "description": "Output array field 1",
                            "visible": "YES",
                            "type": "INT"
                        },
                        {
                            "name": "output_array_field2",
                            "description": "Output array field 2",
                            "visible": "YES",
                            "type": "INT"
                        },
                        {
                            "name": "output_array_field3",
                            "description": "Output array field 3",
                            "visible": "NO",
                            "type": "INT"
                        },
                        {
                            "name": "output_array_field4",
                            "description": "Output array field 4",
                            "visible": "NO",
                            "type": "INT"
                        }                                        
                    ]          
                }     
            },
            "execution": {
                "meta_data": {
                    "time_started": "",
                    "status": ""
                },
                "results": {}
            }
        }

    def tearDown(self):
        pass

    def test_ideal_scenario(self):

        print("test_ideal_scenario")
        
        url = ing_lib.post_test_script_status()
        execution_user_input = self.step["execution_user_input"]
        cs_inputs_obj = ing_lib.CustomScriptInputs(execution_user_input)
        input_json = cs_inputs_obj.input_json
        output_json = copy.deepcopy(cs_inputs_obj.output_json)
                
        for j, entry in enumerate(execution_user_input["entries"]):
            for i, output in enumerate(entry["entry_outputs"]):
                name = output["name"]
                output_json["entries"][j]["entry_outputs"][name] = "{}".format(i)
                        
            for i in range(3):
                fields_dict = OrderedDict()
                for output in entry["entry_output_array"]["outputs"]:
                    name = output["name"]
                    fields_dict[name] = "{}".format(i)
                output_json["entries"][j]["entry_output_array"].append(fields_dict)
                
            entry["verification_status"] = "PENDING"
        
        for i, output in enumerate(execution_user_input["outputs"]):
            name = output["name"]
            output_json["outputs"][name] = "{}".format(i)
                                    
        for i in range(4):
            fields_dict = OrderedDict()
            for output in execution_user_input["output_array"]["outputs"]:
                name = output["name"]
                fields_dict[name] = "{}".format(i)
            output_json["output_array"].append(fields_dict)
            
        data = {
            "scriptRunId": "12345",
            "scriptName": "my script one",
            "scriptPath": "path1/path2/py_script.py",
            "scriptHash": "abcdefg",
            "inputs": input_json,
            "outputs": output_json,
            "total_intervals": 5,
            "end_status": "PASS"
        }
          
        r = requests.post(url, json=data, headers=ic.header, verify=False)
        self.assertEqual(r.status_code, 200)
        
        response = custom_script_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

        data = {
            "scriptRunId": "12345",
            "scriptName": "my script one",
            "scriptPath": "path1/path2/py_script.py",
            "scriptHash": "abcdefg",
            "inputs": input_json,
            "outputs": output_json,
            "total_intervals": 5,
            "end_status": "FAIL"
        }

        r = requests.post(url, json=data, headers=ic.header, verify=False)
        self.assertEqual(r.status_code, 200)

        response = custom_script_step.run(self.step)
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

    def test_polling(self):

        print("Testing polling for custom script status")
        url = ing_lib.post_test_script_status()
        execution_user_input = self.step["execution_user_input"]
        cs_inputs_obj = ing_lib.CustomScriptInputs(execution_user_input)
        input_json = cs_inputs_obj.input_json
        output_json = copy.deepcopy(cs_inputs_obj.output_json)
                
        for j, entry in enumerate(execution_user_input["entries"]):
            for i, output in enumerate(entry["entry_outputs"]):
                name = output["name"]
                output_json["entries"][j]["entry_outputs"][name] = "{}".format(i)
                        
            for i in range(3):
                fields_dict = OrderedDict()
                for output in entry["entry_output_array"]["outputs"]:
                    name = output["name"]
                    fields_dict[name] = "{}".format(i)
                output_json["entries"][j]["entry_output_array"].append(fields_dict)
                
            entry["verification_status"] = "PENDING"
        
        for i, output in enumerate(execution_user_input["outputs"]):
            name = output["name"]
            output_json["outputs"][name] = "{}".format(i)
                                    
        for i in range(4):
            fields_dict = OrderedDict()
            for output in execution_user_input["output_array"]["outputs"]:
                name = output["name"]
                fields_dict[name] = "{}".format(i)
            output_json["output_array"].append(fields_dict)
            
        data = {
            "scriptRunId": "12345",
            "scriptName": "my script one",
            "scriptPath": "path1/path2/py_script.py",
            "scriptHash": "abcdefg",
            "inputs": input_json,
            "outputs": output_json,
            "total_intervals": 5,
            "end_status": "PASS"
        }
        
        # /custom_script/status set to error 400
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/custom_script/status", errorflag="404", errormsg={"message":"Something bad happened"})
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)       
        print (r.status_code) 
        print(r.text)
        response = custom_script_step.run(self.step)
        print(json.dumps(response, indent=4))
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")
  

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))