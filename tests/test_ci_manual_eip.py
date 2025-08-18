import xmlrunner
import unittest
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import manual_eip_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import logging
import test_util as util
import requests
from test_util import *
from sim_functions import *



class ManualEIPTests(unittest.TestCase):

    def setUp(self):
        # login and set header token
        get_ing_auth_header()
        get_auth_header()
        ic.venue_service_address = os.environ.get("VENUE_SIMULATOR_URL")
        # print("Clear any endpoints")
        # url = ing_lib.get_forced_errors()
        # forced_error = ["ALL"]
        # r = requests.delete(url, json=forced_error, headers=ic.header, verify=False)

        self.session_id = 10
        self.step = {
        "elem_id": "uuid-step-4",
        "elem_type": "STEP",
        "execution_id": "uuid-execution-12",
        "description": "A step to get the venue configuration",
        "number": "1-4",
        "step_type": "MANUAL_EIP",
        "variable": {"name": "sample_variable"},
         "execution_user_input": {
            "entries": [
                {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "Volt",
                "min_value": "string",
                "max_value": "string",
                "actual_value": "string",
                "measured_unit": "string"
                }
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

    def test_non_numerics(self):

        print("use non numeric for min value")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "Hello", 
                "max_value": "5000", 
                "actual_value": "2000", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "ERROR")

        print("use non numeric for max value")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "10", 
                "max_value": "Hello", 
                "actual_value": "2000", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "ERROR")

    def test_no_max_min_value(self):

        print("testing a no max value scenario (MegaOhm)")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "1", 
                "max_value": "", 
                "actual_value": "2000", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "1", 
                "max_value": "", 
                "actual_value": "0.5", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "FAIL")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "1", 
                "max_value": "", 
                "actual_value": "OL", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")


        print("testing a no max value scenario (Ohm)")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "1", 
                "max_value": "", 
                "actual_value": "2000", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "1", 
                "max_value": "", 
                "actual_value": "0.5", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "FAIL")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "1", 
                "max_value": "", 
                "actual_value": "OL", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")

        
        print("testing a no min value scenario (MegaOhm)")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "", 
                "max_value": "5000", 
                "actual_value": "2000", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "", 
                "max_value": "5000", 
                "actual_value": "7000", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "FAIL")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "MegaOhm", 
                "min_value": "", 
                "max_value": "5000", 
                "actual_value": "OL", 
                "measured_unit": "MegaOhm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "FAIL")

        print("testing a no min value scenario (Ohm)")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "", 
                "max_value": "5000", 
                "actual_value": "2000", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "", 
                "max_value": "5000", 
                "actual_value": "7000", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "FAIL")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "", 
                "max_value": "5000", 
                "actual_value": "OL", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "FAIL")

        print("testing a no min/max value scenario (Ohm)")

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "", 
                "max_value": "", 
                "actual_value": "2000", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")        

        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "2NDARY PWR ECMEU TO FGS-3 OP HTR, WA", 
                "icds": "013-013-003", 
                "from": "1", 
                "to": "CHS", 
                "unit": "Ohm", 
                "min_value": "", 
                "max_value": "", 
                "actual_value": "OL", 
                "measured_unit": "Ohm"
            }
        ]
        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, "PASS")    

    def test_volts(self):

        print("VOLT: testing value inside params")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volt",
                    "min_value": "0",
                    "max_value": "20",
                    "actual_value": "10",
                    "measured_unit": "Volt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("VOLT: testing value right on max value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volt",
                    "min_value": "0",
                    "max_value": "20",
                    "actual_value": "20",
                    "measured_unit": "Volt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("VOLT: testing value right on min value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volt",
                    "min_value": "0",
                    "max_value": "20",
                    "actual_value": "0",
                    "measured_unit": "Volt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("VOLT: testing value beyond the min")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volt",
                    "min_value": "10",
                    "max_value": "20",
                    "actual_value": "9",
                    "measured_unit": "Volt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

        print("VOLT: testing value beyond the max")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volt",
                    "min_value": "10",
                    "max_value": "20",
                    "actual_value": "21",
                    "measured_unit": "Volt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')



    def test_milivolts(self):

        print("MILIVOLT: testing value inside params")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "miliVolt",
                    "min_value": "1000",
                    "max_value": "2000",
                    "actual_value": "1400",
                    "measured_unit": "miliVolt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("MILIVOLT: testing value right on max value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "miliVolt",
                    "min_value": "1000",
                    "max_value": "2000",
                    "actual_value": "2000",
                    "measured_unit": "miliVolt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("MILIVOLT: testing value right on min value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "miliVolt",
                    "min_value": "1000",
                    "max_value": "2000",
                    "actual_value": "1000",
                    "measured_unit": "miliVolt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("MILIVOLT: testing value beyond the min")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "miliVolt",
                    "min_value": "1000",
                    "max_value": "2000",
                    "actual_value": "2000.01",
                    "measured_unit": "miliVolt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

        print("MILIVOLT: testing value beyond the max")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "miliVolt",
                    "min_value": "1000",
                    "max_value": "2000",
                    "actual_value": "999",
                    "measured_unit": "miliVolt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

    def test_ohm(self):

        print("OHM: testing value inside params")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "50",
                    "max_value": "100",
                    "actual_value": "65",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("OHM: testing value right on max value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "50",
                    "max_value": "100",
                    "actual_value": "100",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("OHM: testing value right on min value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "50",
                    "max_value": "100",
                    "actual_value": "50",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("OHM: testing value beyond the min")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "50",
                    "max_value": "100",
                    "actual_value": "100.01",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

        print("OHM: testing value beyond the max")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "50",
                    "max_value": "100",
                    "actual_value": "101",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

    def test_kiloOhm(self):

        print("KILOOHM: testing value inside params")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "KiloOhm",
                    "min_value": "5000",
                    "max_value": "10000",
                    "actual_value": "6500",
                    "measured_unit": "KiloOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("KILOOHM: testing value right on max value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "KiloOhm",
                    "min_value": "5000",
                    "max_value": "10000",
                    "actual_value": "10000",
                    "measured_unit": "KiloOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("KILOOHM: testing value right on min value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "KiloOhm",
                    "min_value": "5000",
                    "max_value": "10000",
                    "actual_value": "5000",
                    "measured_unit": "KiloOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("KILOOHM: testing value beyond the min")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "KiloOhm",
                    "min_value": "5000",
                    "max_value": "10000",
                    "actual_value": "4999.99",
                    "measured_unit": "KiloOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

        print("KILOOHM: testing value beyond the max")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "KiloOhm",
                    "min_value": "5000",
                    "max_value": "10000",
                    "actual_value": "10000.01",
                    "measured_unit": "KiloOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

    def test_megaOhm(self):

        print("MEGAOHM: testing value inside params")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "650",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("MEGAOHM: testing value right on max value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "1000",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("KILOOHM: testing value right on min value")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "500",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("KILOOHM: testing value beyond the min")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "499.99",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

        print("KILOOHM: testing value beyond the max")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "1000.01",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')



    def test_ol(self):

        print("OL: test incorrect use of 'ol'")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "ol",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')

        print("OL: test incorrect use of 'ol")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "5000000",
                    "max_value": "10000000",
                    "actual_value": "oL",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')


        print("OL: test incorrect use of 'ol")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "5000000",
                    "max_value": "10000000",
                    "actual_value": "Ol",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')


        print("OL: test applying 'OL' to volts")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volts",
                    "min_value": "5000000",
                    "max_value": "10000000",
                    "actual_value": "OL",
                    "measured_unit": "Volts"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')


        print("OL: OL with max value set")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "5000000",
                    "max_value": "10000000",
                    "actual_value": "OL",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'FAIL')

        print("OL: OL with max value not set")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "5000000",
                    "max_value": "",
                    "actual_value": "OL",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

    def test_mismatched_error_units(self):

        print("Unit: Ohm, Measured unit: Volt")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "500",
                    "measured_unit": "Volt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')

        print("Unit: miliVolt, Measured unit: MegaOhm")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "miliVolt",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "500",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')

        print("Unit: MegaOhm, Measured unit: miliVolt")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "MegaOhm",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "500",
                    "measured_unit": "miliVolt"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')

        print("Unit: Volt, Measured unit: Ohm")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Volt",
                    "min_value": "500",
                    "max_value": "1000",
                    "actual_value": "500",
                    "measured_unit": "Ohm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'ERROR')


    def test_mix_and_convert(self):
        print("Testing mix and convert Ohm types")
        print("Unit: Ohm, Measured unit: MegaOhm")
        self.step["execution_user_input"]["entries"] = [
                {
                    "signal_name": "TestSignal",
                    "icds": "1231231",
                    "from": "1",
                    "to": "2",
                    "unit": "Ohm",
                    "min_value": "5000000",
                    "max_value": "10000000",
                    "actual_value": "5",
                    "measured_unit": "MegaOhm"
                }
            ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')
        print("Unit: MegaOhm, Measured unit: KiloOhm")
        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "MegaOhm",
                "min_value": "5",
                "max_value": "10",
                "actual_value": "5000",
                "measured_unit": "KiloOhm"
            }
        ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("Unit: KiloOhm, Measured unit: MegaOhm")
        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "KiloOhm",
                "min_value": "5000",
                "max_value": "10000",
                "actual_value": "5",
                "measured_unit": "MegaOhm"
            }
        ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("Unit: KiloOhm, Measured unit: Ohm")
        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "KiloOhm",
                "min_value": "5",
                "max_value": "10",
                "actual_value": "6000",
                "measured_unit": "Ohm"
            }
        ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("Unit: Ohm, Measured unit: KiloOhm")
        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "Ohm",
                "min_value": "5000",
                "max_value": "10000",
                "actual_value": "6",
                "measured_unit": "KiloOhm"
            }
        ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("Testing mix and convert Volt types")
        print("Unit: Volt, Measured unit: miliVolt")
        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "Volt",
                "min_value": "5",
                "max_value": "10",
                "actual_value": "7000",
                "measured_unit": "miliVolt"
            }
        ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

        print("Unit: miliVolt, Measured unit: Volt")
        self.step["execution_user_input"]["entries"] = [
            {
                "signal_name": "TestSignal",
                "icds": "1231231",
                "from": "1",
                "to": "2",
                "unit": "miliVolt",
                "min_value": "5000",
                "max_value": "10000",
                "actual_value": "7",
                "measured_unit": "Volt"
            }
        ]

        res = manual_eip_step.run(self.step)
        status = res["execution"]["meta_data"]["status"]
        self.assertEqual(status, 'PASS')

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
