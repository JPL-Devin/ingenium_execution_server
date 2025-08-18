import xmlrunner
import os
import sys
import unittest
import requests
from config import shared_dict, logger
import json
import uuid
import traceback

from multiprocessing.pool import ThreadPool
import time



base_url = shared_dict['host']

venue_info = {
    'venue_id': '123',
    'name': 'venue 1',
    'description': 'my test venue',
    'ampcs_address': 'ampcs_address.jpl.nasa.gov',
    'sse_address': 'sse_address.jpl.nasa.gov',
    'location': 'Bld 321',
    'type': 'WSTS'
}

venue_info_2 = {
    'venue_id': '124',
    'name': 'venue 2',
    'description': 'my test venue 2',
    'ampcs_address': 'ampcs_address2.jpl.nasa.gov',
    'sse_address': 'sse_address2.jpl.nasa.gov',
    'location': 'Bld 322',
    'type': 'WSTS'
}

class KernelTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

     
    def test_run_step(self):
        execution_id = str(uuid.uuid4())

        self.register_execution(execution_id, venue_info)
        
        with open('manual_input_step.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id 
            # print json.dumps(step, indent=4)
            res_dict = self.run_step(execution_id, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        # run with different values
        new_user_input = {
            "entries": [
                {"name": "var1", "type": "FLOAT", "verify_on": "VALUE", "verification_condition": "RECORD", "verification_values": [], "actual_value": 10.2},
                {"name": "var2", "type": "FLOAT", "verify_on": "VALUE", "verification_condition": "RECORD", "verification_values": [], "actual_value": 20.3}
            ]
        }
        step['execution_user_input'] = new_user_input

        res_dict = self.run_step(execution_id, step)
        logger.debug('run_step res_dict: %s', json.dumps(res_dict, indent=4))

        new_user_input_entries = new_user_input['entries']

        for entry in new_user_input_entries:
            variable_name_value = self.get_variable_value(execution_id, entry['name'])
            logger.debug('variable_name_value: %s', json.dumps(variable_name_value, indent=4))
            self.assertEqual(variable_name_value['name'], entry['name'])
            self.assertEqual(variable_name_value['value']['actual_value'], entry['actual_value'])

        results_entries = res_dict['execution']['results']['entries']

        self.assertEqual(len(new_user_input_entries), len(results_entries))

        for entry in results_entries:
            self.assertEqual(entry['verification_status'], 'PASS')

        # test if get_variabe_value works as expected for a variable that does not exist
        
        name_value = self.get_variable_value(execution_id, 'key_that_does_not_exist', 200)

        self.assertEqual(name_value['name'], 'key_that_does_not_exist')
        self.assertTrue(name_value['value'] is None)

    def test_session_info(self):
        execution_id_1 = str(uuid.uuid4())
        execution_id_2 = str(uuid.uuid4())

        self.register_execution(execution_id_1, venue_info)
        self.register_execution(execution_id_2, venue_info_2)
        
        # set session for execution 1
        with open('gds_manual_step_dummy.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_1 
            step['execution_user_input']['entries'] = [
                {"data_path": "side A", "session_id": "123"},
                {"data_path": "side B", "session_id": "124"}
            ] 

            res_dict = self.run_step(execution_id_1, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        session_info_expected_1 = res_dict['execution']['results']['entries']

        # set session for execution 2
        # this should not interfere with execution 1
        with open('gds_manual_step_dummy.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_2 
            step['execution_user_input']['entries'] = [
                {"data_path": "side A", "session_id": "223"},
                {"data_path": "side B", "session_id": "224"}
            ]             

            res_dict = self.run_step(execution_id_2, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        session_info_expected_2 = res_dict['execution']['results']['entries']        

        # run a step for execution 1
        with open('cmd_step_dummy_session.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_1 

            res_dict = self.run_step(execution_id_1, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))      
        session_info_actual_1 = res_dict['execution']['results']['entries']  

        self.assertSequenceEqual(session_info_actual_1, session_info_expected_1)

        # run a step for execution 2
        with open('cmd_step_dummy_session.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_2 

            res_dict = self.run_step(execution_id_2, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))      
        session_info_actual_2 = res_dict['execution']['results']['entries']  

        self.assertSequenceEqual(session_info_actual_2, session_info_expected_2)


        # reset session for execuiton 1        
        # this should not interfere with execution 2
        with open('gds_manual_step_dummy.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_1 
            step['execution_user_input']['entries'] = [
                {"data_path": "side A", "session_id": "323"},
                {"data_path": "side B", "session_id": "324"}
            ] 

            res_dict = self.run_step(execution_id_1, step)        
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        session_info_expected_3 = res_dict['execution']['results']['entries']        

        # run a step for execution 1
        with open('cmd_step_dummy_session.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_1 

            res_dict = self.run_step(execution_id_1, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))      
        session_info_actual_3 = res_dict['execution']['results']['entries']  

        self.assertSequenceEqual(session_info_actual_3, session_info_expected_3)

        # run a step for execution 2
        with open('cmd_step_dummy_session.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_2 

            res_dict = self.run_step(execution_id_2, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))      
        session_info_actual_2 = res_dict['execution']['results']['entries']  

        self.assertSequenceEqual(session_info_actual_2, session_info_expected_2)   

        # run a step for execution 1 (async)           
        with open('manual_input_step_with_sleep.json') as data_file:
            step = json.load(data_file)
            res_dict = self.run_step(execution_id_1, step, 'ASYNC', 202)

        # while a step is running for execution 1, run a step for execution 2
        # This will use another Python kernel.
        with open('cmd_step_dummy_session.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_2 

            res_dict = self.run_step(execution_id_2, step)

        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))      
        session_info_actual_2 = res_dict['execution']['results']['entries']  

        self.assertSequenceEqual(session_info_actual_2, session_info_expected_2) 


      

    def test_run_error(self):
        execution_id = str(uuid.uuid4())

        with open('manual_input_step.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id

        # run with different values
        new_user_input = {
            "entries": [
                {"name": "_TEST_MODE_", "type": "STRING", "verify_on": "VALUE", "verification_condition": "RECORD", "verification_values": [], "actual_value": "RUN_ERROR"}
            ]
        }
        step['execution_user_input'] = new_user_input

        logger.debug('input step: %s', json.dumps(step, indent=4))

        res_dict = self.run_step(execution_id, step, 'SYNC', 200, 'ERROR')

        logger.debug('run response: %s', json.dumps(res_dict, indent=4))
        meta_data_error = res_dict['execution']['meta_data']['error']
        self.assertTrue(len(meta_data_error['message']) > 0)
        self.assertTrue(len(meta_data_error['details']) > 0)
        self.assertEqual(meta_data_error['error_type'], 'INGENIUM_SERVICE_ERROR')
        self.assertEqual(meta_data_error['error_source'], 'EXECUTION_SERVICE')
        self.assertEqual(meta_data_error['http_code_at_source'], 0)


    def test_halt(self):
        execution_id = str(uuid.uuid4())

        pool = ThreadPool(processes=2)
        res1 = pool.apply_async(self.worker_run, (execution_id,))
        res2 = pool.apply_async(self.worker_interrupt, (execution_id,))

        self.assertEqual(res2.get(), True)
        # without halt, it would take ~10 seconds
        self.assertLess(res1.get(), 5.0)

    def test_copy_state(self):
        execution_id_1 = str(uuid.uuid4())
        execution_id_2 = str(uuid.uuid4())

        self.register_execution(execution_id_1, venue_info)
        
        # set session for execution 1
        with open('gds_manual_step_dummy.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id_1 
            step['execution_user_input']['entries'] = [
                {"data_path": "side A", "session_id": "123"},
                {"data_path": "side B", "session_id": "124"}
            ] 

            res_dict = self.run_step(execution_id_1, step)

        session_info_expected = res_dict['execution']['results']['entries'] 

        res_dict = self.copy_execution_state(execution_id_1, execution_id_2)
        logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))

        logger.debug('execution_id_1: %s', execution_id_1)
        logger.debug('execution_id_2: %s', execution_id_2)
        self.assertEqual(len(res_dict), 10)
        self.assertEqual(res_dict[0]['name'], 'execution_id')
        self.assertEqual(res_dict[0]['value'], execution_id_2)
        self.assertEqual(res_dict[1]['name'], 'ampcs_session_information')
        self.assertSequenceEqual(res_dict[1]['value'], session_info_expected)
        self.assertEqual(res_dict[8]['name'], 'time_references')
        self.assertTrue(len(res_dict[8]['value']['LAST_STEP_START']) > 0)
        self.assertTrue(len(res_dict[8]['value']['LAST_STEP_END']) > 0)


    def worker_run(self, execution_id):
        logger.debug('worker_run: %s', execution_id)

        time0 = time.time()

        with open('manual_input_step_with_sleep.json') as data_file:
            step = json.load(data_file)
            step['execution_id'] = execution_id
            res_dict = self.run_step(execution_id, step, 'SYNC', 200, 'ERROR')
            logger.debug('worker_run res_dict: %s', json.dumps(res_dict, indent=4))            

            self.assertTrue(res_dict['execution']['meta_data']['error']['message'].find('A process in the process pool was terminated abruptly') > -1)



        time1 = time.time()

        elapsed_sec = time1-time0

        logger.debug('elapsed_sec: %s', elapsed_sec)

        return elapsed_sec

    def worker_interrupt(self, execution_id):
        logger.debug('worker_interrupt: %s', execution_id)
        time.sleep(2.0)
        self.halt_run(execution_id)
        logger.debug('worker_interrupt halted: %s', execution_id)

        return True


    def register_execution(self, execution_id, venue_info, expected_status=204):
        url = '{0}/executions/{1}'.format(base_url, execution_id)

        logger.debug('url: %s', url)

        logger.debug('register_execution venue_info: %s', json.dumps(venue_info, indent=4))

        result = requests.put(url,
            headers=shared_dict['headers'],
            data=json.dumps(venue_info))

        logger.debug('register_execution result.text: %s', result.text)
        self.assertEqual(result.status_code, expected_status)

    def copy_execution_state(self, execution_id, target_execution_id, expected_status=200):
        url = '{0}/executions/{1}/copy_state'.format(base_url, execution_id)

        logger.debug('url: %s', url)

        result = requests.post(url,
            headers=shared_dict['headers'],
            params={'target_execution_id': target_execution_id})

        logger.debug('copy_execution_state result.text: %s', result.text)
        self.assertEqual(result.status_code, expected_status)
        res_dict = json.loads(result.text)
        return res_dict          

    def run_step(self, execution_id, step, run_mode='SYNC', expected_status=200, expected_execution_status='PASS'):
        url = '{0}/executions/{1}/run'.format(base_url, execution_id)

        logger.debug('url: %s', url)

        logger.debug('run_step step: %s', json.dumps(step, indent=4))

        params = {'run_mode': run_mode}
        result = requests.post(url,
            headers=shared_dict['headers'],
            params=params,
            data=json.dumps(step))

        logger.debug('run_step result.text: %s', result.text)
        self.assertEqual(result.status_code, expected_status)
        res_dict = json.loads(result.text)

        if (expected_status == 200):
            self.assertEqual(res_dict['execution']['meta_data']['status'], expected_execution_status)
            if expected_execution_status == 'PASS':
                for entry in res_dict['execution']['results']['entries']:
                    if 'verification_status' in entry:
                        self.assertEqual(entry['verification_status'], 'PASS')
        else:
            logger.debug('res_dict: %s', json.dumps(res_dict, indent=4))
        return res_dict

    def halt_run(self, execution_id):
        url = '{0}/executions/{1}/halt'.format(base_url, execution_id)

        logger.debug('url: %s', url)

        result = requests.post(url, headers=shared_dict['headers'])

        self.assertEqual(result.status_code, 202)

    def get_config_value(self, execution_id, parameter_name):
        url = '{0}/executions/{1}/config_value'.format(base_url, execution_id)
        logger.debug('get_config_value url: %s', url)
        logger.debug('get_config_value parameter_name: %s', parameter_name)
        params = {'parameter_name': parameter_name}
        result = requests.get(url,
            headers=shared_dict['headers'],
            params=params)
        logger.debug('get_config_value result.status_code: %s', result.status_code)
        logger.debug('get_config_value result.text: %s', result.text)
        self.assertEqual(result.status_code, 200)
        res_dict = json.loads(result.text)

        return res_dict

    def get_variable_value(self, execution_id, variable_name, expected_code=200):

        logger.debug('get_variable_value variable_name: %s', variable_name)

        url = '{0}/executions/{1}/variable_value'.format(base_url, execution_id)
        params = {'variable_name': variable_name}
        result = requests.get(url,
            headers=shared_dict['headers'],
            params=params)
        logger.debug('result.text: %s', result.text)
        self.assertEqual(result.status_code, expected_code)

        if (result.status_code == 200):
            res_dict = json.loads(result.text)
        else:
            res_dict = None    

        return res_dict

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output="./test-reports/"))
