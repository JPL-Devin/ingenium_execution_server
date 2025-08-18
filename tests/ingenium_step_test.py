
#######################  Imports ########################

from ingenium_embedded import ingenium_step_sdk
from ingenium_embedded import ingenium_config as ic
from ingenium_embedded import ingenium_library
import _thread
import json


####################### Set your configuration variables #############################

# Note this should all be contained within either the ingenium step sdk library or the ingenium_config file



# Defines the step to import and test.
StepToTest="get_config_step"

# Define the JSON for the step
step = {
    "elem_id": "uuid-step-4",
    "elem_type": "STEP",
    "execution_id": "uuid-execution-12",
    "description": "A step to get the venue configuration",
    "number": "1-4",
    "step_type": "VENUE_CONFIG_GET",
    "variable": {"name": "sample_variable"},
    "code": {
        "name": "get_venue_config.run",
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
        "parameters": [
            {"name": "elem_name", "type": "string", "design_exec" : "design", "lookup":"VenueConfig", "default" : "StarCamera"}
        ],
        "min_count": 1,
        "max_count": -1
    },
    "execution_user_input": {
        "entries": [
            {"config_elem_name": "StarCamera"},
            {"config_elem_name": "INSTRUMENT1"},
            {"config_elem_name": "FSW_IMAGE_1"}
        ]
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
            "venue_id": "venue_id_198",
            "venue_name": "MY_WSTS_7",
			"entries": [
                {"config_elem_name": "StarCamera", "type": "EM", "status": "INSTALLED", "serial": "SN 20323232"},
                {"config_elem_name": "INSTRUMENT1", "type": "SIMULATOR", "status": "INSTALLED", "serial": "V3.2"},
                {"config_elem_name": "FSW_IMAGE_1", "type": "FLIGHT", "status": "INSTALLED", "serial": "3.0.1"}
            ]
        }
    }
}


ic.venue_id="7d06288a-debb-49f1-8cfd-05e9000a8d4a"

########################   Launching the step    ################################################

# Set the login information
ingenium_step_sdk.set_login_info(environment=True)

# Login to an Ingenium instance (to get a token)
ingenium_step_sdk.login()

# Convert the Step to JSON
step=json.loads(json.dumps(step))

# Import Launch the desired step
SteptoExecute=__import__(StepToTest)
SteptoExecute.run(step)

venues=ingenium_step_sdk.get_venues()
for venue in venues:
    print(venue['venue_id'],venue['name'])
    ingenium_step_sdk.get_config(venue['venue_id'])




















