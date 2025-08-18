import unittest
import json

from config import shared_dict
from test_ci_execution_server import KernelTest

class ConfigTest(KernelTest):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_config(self):
        execution_id = 'm2020-ingenium-10000'
        
        config_value = self.get_config_value(execution_id, 'ampcs_session_information')
        
        print ('config_value:', json.dumps(config_value, indent=4))        

if __name__ == '__main__':
    ct = ConfigTest()
    ct.test_get_config()
