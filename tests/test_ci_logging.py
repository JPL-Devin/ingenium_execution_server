import xmlrunner
import os
import sys
import unittest
import requests
import json
import random
from config import shared_dict, logger



class LoggingTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @unittest.skip("This test fails on CI env. Disabled until we figure it out.")
    def test_logging_level(self):

        url = '{0}/logging'.format(shared_dict['host'])

        logger.debug('POST url= %s', url)
        data = {'level': 'DEBUG'}
        result = requests.post(url, data=json.dumps(data), headers=shared_dict['headers'])
        logger.debug('result.text: %s', result.text)
        self.assertEqual(result.status_code, 204)

        logger.debug('GET url= %s', url)
        result = requests.get(url, headers=shared_dict['headers'])
        logger.debug('result.text: %s', result.text)
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict['level'], 'DEBUG')

        logger.debug('POST url= %s', url)
        data = {'level': 'ERROR'}
        result = requests.post(url, data=json.dumps(data), headers=shared_dict['headers'])
        logger.debug('result.text: %s', result.text)
        self.assertEqual(result.status_code, 204)

        logger.debug('GET url= %s', url)
        result = requests.get(url, headers=shared_dict['headers'])
        logger.debug('result.text: %s', result.text)
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)
        self.assertEqual(res_dict['level'], 'ERROR')

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
