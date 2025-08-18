import getpass
import requests
import json
import uuid
from config import shared_dict
              
def create_kernel(base_url):
    execution_id = str(uuid.uuid4())
    params = {'execution_id': execution_id}

    url = base_url + '/kernels'

    print('Create execution environment at url:', url)

    result = requests.post(url,
        headers=shared_dict['headers'],
        data='',
        params=params)

    print(result.status_code)
    print(result.text)

    res_dict = json.loads(result.text)

    return res_dict

def get_kernel(base_url, execution_id):

    url = '{0}/kernels/{1}'.format(base_url, execution_id)

    print('get_kernel url:', url)

    result = requests.get(url,
        headers=shared_dict['headers'])

    print(result.status_code)
    print(result.text)

    res_dict = None
    if result.status_code == 200:
        res_dict = json.loads(result.text)

    return res_dict

def prepare_kernel(base_url, execution_id):

    url = '{0}/kernels/{1}/prepare'.format(base_url, execution_id)

    print('prepare_kernel url:', url)

    result = requests.post(url,
        headers=shared_dict['headers'])

    print(result.status_code)
    print(result.text)

    res_dict = None
    if result.status_code == 200:
        res_dict = json.loads(result.text)

    return res_dict

def get_kernels(base_url):

    url = '{0}/kernels'.format(base_url)

    print('get_kernels url:', url)

    result = requests.get(url,
        headers=shared_dict['headers'])

    print(result.status_code)
    print(result.text)

    res_dict = json.loads(result.text)

    return res_dict
                  
if __name__ == '__main__':

    base_url = 'http://localhost:9999/api/v1'
    
    res_dict = create_kernel(base_url)
    execution_id_1 = res_dict.get('execution_id')
    kernel_dict = get_kernel(base_url, execution_id_1)
    
    res_dict =  create_kernel(base_url)
    execution_id_2 = res_dict.get('execution_id')
    kernel_dict = get_kernel(base_url, execution_id_2)
    
    res_dict =  create_kernel(base_url)
    execution_id_3 = res_dict.get('execution_id')
    kernel_dict = get_kernel(base_url, execution_id_3)    
    
    kernels_dict = get_kernels(base_url)
    
    print('Prepare an existing kernel. Execution server should not create a new kernel and return 204 response.')
    kernel_dict_1 = get_kernel(base_url, execution_id_1)            
    prepare_kernel(base_url, execution_id_1)
    get_kernels(base_url)         
    
    check_again = input('Restart JKG and check kernel again? (y/n)')
    if check_again == "y":
        kernel_dict_2 = get_kernel(base_url, execution_id_2)        
        
        prepare_kernel(base_url, execution_id_2)
        get_kernels(base_url)        
        
    check_again = input('Restart execution service and check kernel again? (y/n)')

    if check_again == "y":
        kernel_dict_3 = get_kernel(base_url, execution_id_3) 
                
        prepare_kernel(base_url, execution_id_3)
        get_kernels(base_url)        
