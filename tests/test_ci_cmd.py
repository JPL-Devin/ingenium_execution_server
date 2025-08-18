import xmlrunner
import unittest
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import test_util as util
from ingenium_embedded import cmd_step
from ingenium_embedded.logging_util import logger
import requests
from test_util import *
from sim_functions import *


class CmdTests(unittest.TestCase):

    def setUp(self):
        
        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        # # login and set header token
        # ingenium_step_sdk.set_login_info(environment_variable=True)
        # ingenium_step_sdk.login()

        # logger.debug("Clear any endpoints")
        # url = ing_lib.get_forced_errors()
        # forced_error = ["ALL"]
        # r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)
        
        # logger.debug("Reset command verification EVR data")
        # url = ing_lib.get_test_evr()
        # evr_data = []
        # requests.post(url, json=evr_data, headers=ic.header, verify=False)              

        # print("Shutting down MTAK session...")
        # ing_lib.ShutdownMTAK()

        # print("Starting MTAK session: {}".format(session_id))
        # ing_lib.StartMTAK(session=[int(session_id)])


        ing_lib.register_session("SIDE A", 29)


        self.fsw_json_input = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "CMD",
            "execution_user_input": {
                "data_path": "SIDE A",
                "entries": [
                    {
                      "hw_fsw": "FSW",
                      "timeout": 10,
                      "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
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

        self.hw_json_input = {
            "execution_id": "10",
            "elem_id": "1",
            "step_type": "CMD",
            "execution_user_input": {
                "data_path": "SIDE A",
                "entries": [
                    {
                      "hw_fsw": "HW",
                      "timeout": 10,
                      "cmd_string": "HDW_TWTA_DIS",
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


    def test_multiple_fsw_cmds(self):

        logger.debug("Test: multiple fsw comamnds, however first command fails so all subsequent command should not be sent")

        # venue_simulator does not currently use start_time and end_time.
        # provide dummy values to avoid errors in RealtimeEVR function.
        evrs = ing_lib.RealtimeEVR(data_path='SIDE A',
                                    start_time='2020-009T00:00:00',
                                    end_time='2020-009T00:00:10')
                                       
        logger.debug('Before setting eha. evrs:', extra={'data': evrs})     
        
        url = ing_lib.get_test_eha()
        
        # setting initial value for channels that are used for command verification
        for channel in ic.fsw_channels:
            eha_data = test_eha_obj(1, channel, 1)
            r = requests.post(url, json=eha_data, headers=ic.header, verify=False)

        url = ing_lib.get_receipt_configs()

        receipt = {
          "uplink_type": "immediate",
          "channels": [
            "CMD-9999"      # use an incorrect channel id
          ],
          "evrs": ic.fsw_evr_name
        }

        r = requests.post(url, json=receipt, headers=ic.header, verify=False)

        # add artificial delay
        forced_error = forced_error_obj("/cmd/fsw_cmd", errorflag="None", duration=2, delay_verify_evr=1, delay_verify_channels=4)
        url = ing_lib.get_forced_errors()
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)       

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": True
                },
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "SECOND_COMMAND",
                  "verify": True
                },
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "THIRD_COMMAND",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        self.assertTrue(len(dispatch["execution_user_input"]["entries"]), 3)
        self.assertTrue(len(dispatch["execution"]["results"]["entries"]), 1)

    def test_multiple_hw_cmds(self):

        logger.debug("Test: multiple hw comamnds, however first command fails so all subsequent command should not be sent")

        # venue_simulator does not currently use start_time and end_time.
        # provide dummy values to avoid errors in RealtimeEVR function.
        evrs = ing_lib.RealtimeEVR(data_path='SIDE A',
                                    start_time='2020-009T00:00:00',
                                    end_time='2020-009T00:00:10')
                                       
        logger.debug('Before setting eha. evrs:', extra={'data': evrs})     
        
        url = ing_lib.get_test_eha()

        for channel in ic.hw_channels:
            eha_data = test_eha_obj(1, channel, 1)
            r = requests.post(url, json=eha_data, headers=ic.header, verify=False)

        url = ing_lib.get_receipt_configs()

        receipt = {
          "uplink_type": "hardware",
          "channels": [
            "CMD-9999"      # use an incorrect channel id
          ],
          "evrs": ic.hw_evr_name
        }

        r = requests.post(url, json=receipt, headers=ic.header, verify=False)

        # add artificial delay
        forced_error = forced_error_obj("/cmd/hw_cmd", errorflag="None", duration=2, delay_verify_evr=1, delay_verify_channels=4)
        url = ing_lib.get_forced_errors()
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)       

        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 5,
                  "cmd_string": "HDW_TWTA_DIS",
                  "verify": True
                },
                {
                  "hw_fsw": "HW",
                  "timeout": 5,
                  "cmd_string": "SECOND_HW",
                  "verify": True
                },
                {
                  "hw_fsw": "HW",
                  "timeout": 5,
                  "cmd_string": "THIRD_HW",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        self.assertTrue(len(dispatch["execution_user_input"]["entries"]), 3)
        self.assertTrue(len(dispatch["execution"]["results"]["entries"]), 1)


    def test_fsw_cmd(self):

        logger.debug("Test all nominal inputs (verify=True)")

        # venue_simulator does not currently use start_time and end_time.
        # provide dummy values to avoid errors in RealtimeEVR function.
        evrs = ing_lib.RealtimeEVR(data_path='SIDE A',
                                    start_time='2020-009T00:00:00',
                                    end_time='2020-009T00:00:10')
                                       
        logger.debug('Before setting eha. evrs:', extra={'data': evrs})     
        
        url = ing_lib.get_test_eha()
        
        # setting initial value for channels that are used for command verification
        for channel in ic.fsw_channels:
            eha_data = test_eha_obj(1, channel, 1)
            r = requests.post(url, json=eha_data, headers=ic.header, verify=False)

        url = ing_lib.get_receipt_configs()

        receipt = receipt_fsw()

        r = requests.post(url, json=receipt, headers=ic.header, verify=False)

        # add artificial delay
        forced_error = forced_error_obj("/cmd/fsw_cmd", errorflag="None", duration=2, delay_verify_evr=1, delay_verify_channels=4)
        url = ing_lib.get_forced_errors()
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)       

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": True
                }
            ]
        }

        print('self.fsw_json_input', json.dumps(self.fsw_json_input, indent=4))
        dispatch = cmd_step.run(self.fsw_json_input)
        print('dispatch', json.dumps(dispatch, indent=4))

        logger.debug(dispatch)
        
        evrs = ing_lib.RealtimeEVR(data_path='SIDE A',
                                    start_time='2020-009T00:00:00',
                                    end_time='2020-009T00:00:10')                               
        logger.debug('After running step. evrs:', extra={'data': evrs})
                

        result = dispatch["execution"]["results"]["entries"][0]
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], True)
        self.assertEqual(util.is_iso(result["verified_time"]), True)
        
        logger.debug("test all nominal inputs without command verification")

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 30,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        result = dispatch["execution"]["results"]["entries"][0]
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], False)
        self.assertEqual(result["verified_time"], "")
    
        logger.debug("invoke timeout error")

        logger.debug("Add sleep time to endpoint")

        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/eha/realtime", errorflag="408", duration=10)
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)
        logger.debug(f'{r.status_code} {r.text}')  

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 2,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": True
                }
            ]
        }


        dispatch = cmd_step.run(self.fsw_json_input)
        logger.debug(dispatch)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        logger.debug("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)
        
      

    def test_hw_cmd(self):

        logger.debug("Nominal: All nominal inputs")

        logger.debug("Loading EHA data")
        url = ing_lib.get_test_eha()
        
        for channel in ic.hw_channels:
            eha_data = test_eha_obj(1, channel, 1)
            r = requests.post(url, json=eha_data, headers=ic.header, verify=False)


        logger.debug("Load receipt config")
        url = ing_lib.get_receipt_configs()
        receipt = receipt_hw()
        r = requests.post(url, json=receipt, headers=ic.header, verify=False)


        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "HDW_TWTA_DIS",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        result = dispatch["execution"]["results"]["entries"][0]
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], True)
        self.assertEqual(util.is_iso(result["verified_time"]), True)

        logger.debug("Nominal: All nominal inputs (verify=False)")

        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "HDW_TWTA_DIS",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        result = dispatch["execution"]["results"]["entries"][0]
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "PASS")
        self.assertEqual(result["radiated"], True)
        self.assertEqual(util.is_iso(result["radiated_time"]), True)
        self.assertEqual(result["verified"], False)
        self.assertEqual(result["verified_time"], "")

        logger.debug("invoke timeout error")

        logger.debug("Add sleep time to endpoint")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/eha/realtime", errorflag="404", duration=10)
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)
        logger.debug(f'{r.status_code} {r.text}')  

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "HDW_TWTA_DIS",
                  "verify": True
                }
            ]
        }


        dispatch = cmd_step.run(self.fsw_json_input)
        logger.debug(dispatch)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        logger.debug("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        logger.debug("Clear any endpoints")
        url = ing_lib.get_forced_errors()
        forced_error = ["ALL"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)


    def test_off_nominal_fail(self):

        logger.debug("HW Off-Nominal: Provide a flight software command to command hw (verify=False)")

        logger.debug("Load receipt config")
        url = ing_lib.get_receipt_configs()
        receipt = {
          "uplink_type": "hardware",
          "channels": [
            "CMD-9999"      # use an incorrect channel id
          ],
          "evrs": ic.hw_evr_name
        }
        r = requests.post(url, json=receipt, headers=ic.header, verify=False)


        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        logger.debug(dispatch)
        
        # step execution should fail since command verification would timeout
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "FAIL")
        self.assertEqual(dispatch["execution"]["results"]["entries"][0]['verified'], False)

        logger.debug("Load receipt config")
        url = ing_lib.get_receipt_configs()
        receipt = receipt_hw()
        r = requests.post(url, json=receipt, headers=ic.header, verify=False)



    def test_off_nominal_error(self):

        logger.debug("HW Off-Nominal: Provide an invalid command (verify=True)")
        logger.debug("Force error: 404")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/cmd/hw_cmd", errorflag="404")
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)

        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "NOT_REAL_HW",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        forced_error = ["/cmd/hw_cmd"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        logger.debug("HW Off-Nominal: Provide an invalid command (verify=False)")
        logger.debug("Force error: 404")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/cmd/hw_cmd", errorflag="404")
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)
        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "NOT_REAL_HW",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)

        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        forced_error = ["/cmd/hw_cmd"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        logger.debug("HW Off-Nominal: No data path provided")

        self.hw_json_input["execution_user_input"] = {
            "data_path": None,
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "HDW_TWTA_DIS",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        logger.debug("HW Off-Nominal: Wrong data path provided")

        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE B",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "HDW_TWTA_DIS",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        logger.debug("HW Off-Nominal: Provide an empty command string")

        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        logger.debug("HW Off-Nominal: Provide empty command string (verify=True)")

        self.hw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.hw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")


        logger.debug("FSW Off-Nominal: Provide an invalid command")
        logger.debug("Force error: 404")
        url = ing_lib.get_forced_errors()
        forced_error = forced_error_obj("/cmd/fsw_cmd", errorflag="404")
        r = requests.post(url, json=forced_error, headers=ic.header, verify=False)

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 30,
                  "cmd_string": "NOT_A_REAL_COMMAND",
                  "verify": True
                }
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        forced_error = ["/cmd/fsw_cmd"]
        r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        logger.debug("FSW Off-Nominal: No data path provided")

        self.fsw_json_input["execution_user_input"] = {
            "data_path": None,
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 30,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

        logger.debug("FSW Off-Nominal: Incorrect data path")

        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE B",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 30,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                }
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        self.assertEqual(dispatch["execution"]["meta_data"]["status"], "ERROR")

    def test_one_second_buffer(self):

        # try passing three cmd fsw's without verification. total time for the all three cmds to be dispatched should be more than 3 seconds. 
        
        start_time = time.time()
        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                },
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                },
                {
                  "hw_fsw": "FSW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                }                
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        end_time = time.time()

        time_delta = end_time - start_time 

        self.assertGreater(time_delta, 3)

        start_time = time.time()
        self.fsw_json_input["execution_user_input"] = {
            "data_path": "SIDE A",
            "entries": [
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                },
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                },
                {
                  "hw_fsw": "HW",
                  "timeout": 10,
                  "cmd_string": "ACS_FIRE_THRUSTER,2,2,100",
                  "verify": False
                }                
            ]
        }

        dispatch = cmd_step.run(self.fsw_json_input)
        end_time = time.time()

        time_delta = end_time - start_time 

        self.assertGreater(time_delta, 3)

    def test_side_selection_fsw(self):

      print("Test FSW string selection")
      self.fsw_json_input["execution_user_input"] = {
          "data_path": "SIDE A",
          "entries": [
              {
                "hw_fsw": "FSW",
                "timeout": 10,
                "cmd_string": "CMD_NO_OP",
                "verify": False,
                "string_selection": "A"
              },
              {
                "hw_fsw": "FSW",
                "timeout": 10,
                "cmd_string": "CMD_NO_OP",
                "verify": False,
                "string_selection": "B"
              },
              {
                "hw_fsw": "FSW",
                "timeout": 10,
                "cmd_string": "CMD_NO_OP",
                "verify": False,
                "string_selection": "AB"
              },
              {
                "hw_fsw": "FSW",
                "timeout": 10,
                "cmd_string": "CMD_NO_OP",
                "verify": False,
                "string_selection": "DEFAULT"
              }                              
          ]
      }

      dispatch = cmd_step.run(self.fsw_json_input)
      print(dispatch)

    def test_side_selection_hw(self):
      self.hw_json_input["execution_user_input"] = {
          "data_path": "SIDE A",
          "entries": [
            {
              "hw_fsw": "HW",
              "timeout": 10,
              "cmd_string": "CMD_NO_OP",
              "verify": False,
              "string_selection": "A"
            },
            {
              "hw_fsw": "HW",
              "timeout": 10,
              "cmd_string": "CMD_NO_OP",
              "verify": False,
              "string_selection": "B"
            },
            {
              "hw_fsw": "HW",
              "timeout": 10,
              "cmd_string": "CMD_NO_OP",
              "verify": False,
              "string_selection": "AB"
            },
            {
              "hw_fsw": "HW",
              "timeout": 10,
              "cmd_string": "CMD_NO_OP",
              "verify": False,
              "string_selection": "DEFAULT"
            }            
          ]
      } 

      dispatch = cmd_step.run(self.hw_json_input)

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))

