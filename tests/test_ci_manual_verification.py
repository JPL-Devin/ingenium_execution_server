import xmlrunner
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
from ingenium_embedded import manual_verification_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import traceback
import unittest
from test_util import *
from sim_functions import *
import test_util as util


class ManualVerificationTests(unittest.TestCase):

    def setUp(self):
        get_auth_header()
        get_ing_auth_header()
        ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
        self.step = {
            "execution_id": 1,
            "elem_id": "15",
            "step_type": "MANUAL_VERIFICATION",
            "variable": {"name": "manual_verification"},
            "execution_user_input": {
                "verification_text": "Done",
                "verification_status": "PASS"
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

    def test_make_sure_this_works(self):

        print("One example...")
        response = manual_verification_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["verification_text"], "Done")
        self.assertEqual(response["execution"]["results"]["verification_status"], "PASS")
        self.assertEqual(response["execution"]["meta_data"]["status"], "PASS")

        print("Change it up...")
        self.step["execution_user_input"]["verification_text"] = "This was bad"
        self.step["execution_user_input"]["verification_status"] = "FAIL"
        response = manual_verification_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["verification_text"], "This was bad")
        self.assertEqual(response["execution"]["results"]["verification_status"], "FAIL")
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

        print("Change data type...")
        self.step["execution_user_input"]["verification_text"] = 11
        self.step["execution_user_input"]["verification_status"] = "FAIL"
        response = manual_verification_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["verification_text"], 11)
        self.assertEqual(response["execution"]["results"]["verification_status"], "FAIL")
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

        print("Change to list data type..")
        self.step["execution_user_input"]["verification_text"] = ["hello", "there"]
        self.step["execution_user_input"]["verification_status"] = "FAIL"
        response = manual_verification_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["verification_text"], ["hello", "there"])
        self.assertEqual(response["execution"]["results"]["verification_status"], "FAIL")
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

        print("Change to dictionary data type...")
        self.step["execution_user_input"]["verification_text"] = { "name": "Paul"}
        self.step["execution_user_input"]["verification_status"] = "FAIL"
        response = manual_verification_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["verification_text"], { "name": "Paul"})
        self.assertEqual(response["execution"]["results"]["verification_status"], "FAIL")
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

        print("Change to None data type...")
        self.step["execution_user_input"]["verification_text"] = None
        self.step["execution_user_input"]["verification_status"] = "FAIL"
        response = manual_verification_step.run(self.step)
        self.assertEqual(response["execution"]["results"]["verification_text"], None)
        self.assertEqual(response["execution"]["results"]["verification_status"], "FAIL")
        self.assertEqual(response["execution"]["meta_data"]["status"], "FAIL")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))

