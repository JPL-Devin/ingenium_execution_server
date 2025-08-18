import xmlrunner
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'image'))
import unittest
from ingenium_embedded import environment_manual_step
from ingenium_embedded import ingenium_library as ing_lib
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_step_sdk
import logging
import requests
from test_util import *
from sim_functions import *
import test_util as util


class EnvironmentManualStepTests(unittest.TestCase):

	def setUp(self):
		
		get_ing_auth_header()
		get_auth_header()
		ic.venue_service_address= os.environ.get("VENUE_SIMULATOR_URL")
		ing_lib.register_session("SIDE A", 10)

		self.step = {
		"execution_id": "1",
		"elem_id": "15",
		"step_type": "ENVIRONMENT_MANUAL",
		"elem_type": "EXECUTION",
		"variable": {
			"name": "environment"
		},
			"execution_user_input": {
			"temperature": {
				"verification_condition": "GREATER_THAN",
				"verify_on": "VALUE",
				"verification_values": [10],
				"actual_value":  50
			},
			"humidity": {
				"verify_on": "VALUE",
				"verification_condition": "LESS_THAN",
				"verification_values": [5],
				"actual_value":  10
			}
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


	def test_ideal_scenario(self):

	    print("Checking environemnt manual input...")
	    response = environment_manual_step.run(self.step)
	    temp_result = response["execution"]["results"]["temperature"]
	    humidity_result = response["execution"]["results"]["humidity"]
	    self.assertEqual(temp_result["verification_status"], "PASS")
	    self.assertEqual(humidity_result["verification_status"], "FAIL")

	def test_cases(self):

	    print("Nominal: Equals")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  10.0
	        },
	        "humidity": {
	            "verification_condition": "EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  10.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    print("Nominal: Equals")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  10
	        },
	        "humidity": {
	            "verification_condition": "EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10],
	            "actual_value":  10.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")


	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  11.0
	        },
	        "humidity": {
	            "verification_condition": "EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  11.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")


	    print("Nominal: Not Equal")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "NOT_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "NOT_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "NOT_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  10.0
	        },
	        "humidity": {
	            "verification_condition": "NOT_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  10.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Record")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "RECORD",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "RECORD",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "RECORD",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  ""
	        },
	        "humidity": {
	            "verification_condition": "RECORD",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  ""
	        }
	    }
	    run = environment_manual_step.run(self.step)

	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Greater than")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [10.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Less than")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  10.0
	        },
	        "humidity": {
	            "verification_condition": "LESS_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  10.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value": 30.0
	        },
	        "humidity": {
	            "verification_condition": "LESS_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value":  30.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Greater than or equal")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "GREATER_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value": 15.0
	        },
	        "humidity": {
	            "verification_condition": "GREATER_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Less than or equal")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "LESS_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value": 30.0
	        },
	        "humidity": {
	            "verification_condition": "LESS_THAN_OR_EQUAL",
	            "verify_on": "VALUE",
	            "verification_values": [20.0],
	            "actual_value":  30.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Inclusive Range")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [15.0, 10.0],
	            "actual_value":  15.0
	        },
	        "humidity": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [15.0, 10.0],
	            "actual_value":  15.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [20.0, 10.0],
	            "actual_value": 40.0
	        },
	        "humidity": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [20.0, 10.0],
	            "actual_value":  40.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	    print("Nominal: Exclusive Range")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EXCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [15.0, 10.0],
	            "actual_value":  12.0
	        },
	        "humidity": {
	            "verification_condition": "EXCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [15.0, 10.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")
	    self.assertEqual(hum_status, "PASS")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EXCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [20.0, 10.0],
	            "actual_value": 20.0
	        },
	        "humidity": {
	            "verification_condition": "EXCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [20.0, 10.0],
	            "actual_value":  20.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    hum_status  = run["execution"]["results"]["humidity"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")
	    self.assertEqual(hum_status, "FAIL")

	def test_change(self):
	    print("Nominal: Change Equals")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [0.0],
	            "actual_value":  50.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    print("Nominal: Change Not Equal")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "NOT_EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [10.0],
	            "actual_value":  50.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "NOT_EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [0.0],
	            "actual_value":  50.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")


	    print("Nominal: Change Greater than")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "CHANGE",
	            "verification_values": [10.0],
	            "actual_value":  70.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "CHANGE",
	            "verification_values": [10.0],
	            "actual_value":  40.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")


	    print("Nominal: Change Less than")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN",
	            "verify_on": "CHANGE",
	            "verification_values": [50],
	            "actual_value":  70
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN",
	            "verify_on": "CHANGE",
	            "verification_values": [-50],
	            "actual_value":  40
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")


	    print("Nominal: Change Greater than or equal")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN_OR_EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [20],
	            "actual_value":  70
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN_OR_EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [50.0],
	            "actual_value":  40.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")


	    print("Nominal: Change Less than or equal")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN_OR_EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [20.0],
	            "actual_value":  70.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "LESS_THAN_OR_EQUAL",
	            "verify_on": "CHANGE",
	            "verification_values": [-100.0],
	            "actual_value":  40.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")



	    print("Nominal: Change Inclusive Range")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "CHANGE",
	            "verification_values": [20.0, 100.0],
	            "actual_value":  70.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "CHANGE",
	            "verification_values": [10.0, 20.90],
	            "actual_value":  40.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")


	    print("Nominal: Change Exclusive Range")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EXCLUSIVE_RANGE",
	            "verify_on": "CHANGE",
	            "verification_values": [19.0, 21.0],
	            "actual_value":  70.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "PASS")

	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "EXCLUSIVE_RANGE",
	            "verify_on": "CHANGE",
	            "verification_values": [-10.0, 50.0],
	            "actual_value":  40.0
	        }
	    }

	    run = environment_manual_step.run(self.step)
	    temp_status = run["execution"]["results"]["temperature"]["verification_status"]
	    self.assertEqual(temp_status, "FAIL")

	def test_off_nominal(self):

	    print("Off-Nominal: Not Present")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "NOT_PRESENT",
	            "verify_on": "VALUE",
	            "verification_values": [15.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")

	    print("Off-Nominal: Change Record")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "RECORD",
	            "verify_on": "CHANGE",
	            "verification_values": [15.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")

	    print("Off-Nominal: Change Not Present")
	    ic.environment_step_variables["temperature"] = {
	            "actual_value":  50.0
	            }

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "NOT_PRESENT",
	            "verify_on": "CHANGE",
	            "verification_values": [15.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")

	    print("Off-Nominal: input more than two verification values inclusive and exclusive range")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "INCLUSIVE_RANGE",
	            "verify_on": "VALUE",
	            "verification_values": [15.0, 10.0, 12.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")


	    print("Off-Nominal: input more than one verification values for mathematical operators")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "VALUE",
	            "verification_values": [15.0, 16.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")


	    print("Off-Nominal: non-float verification values")
	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "VALUE",
	            "verification_values": ["thirteen"],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")

	def test_off_nominal_change(self):

	    print("Off-Nominal: Change but no previous record")
	    ic.environment_step_variables["temperature"] = {}

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "GREATER_THAN",
	            "verify_on": "CHANGE",
	            "verification_values": [15.0],
	            "actual_value":  12.0
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    error_msg = run["execution"]["meta_data"]["status"]
	    self.assertEqual(error_msg, "ERROR")

	    self.step["execution_user_input"] = {
	        "temperature": {
	            "verification_condition": "RECORD",
	            "verify_on": "VALUE",
	            "verification_values": [10.0]
	        },
	        "humidity": {
	            "verification_condition": "RECORD",
	            "verify_on": "VALUE",
	            "verification_values": [10.0]
	        }
	    }
	    run = environment_manual_step.run(self.step)
	    self.assertEqual(run["execution"]["meta_data"]["status"], "FAIL")

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
