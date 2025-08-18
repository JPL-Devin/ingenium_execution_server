import requests
import getpass
import json

auth_url='https://ingenium.cld.jpl.nasa.gov/auth_service/api/v1/login'
headers = {'Content-Type': 'application/json',
              'Accept': 'application/json'}
              
if __name__ == '__main__':
    
    user_name = input('username:')
    password = getpass.getpass('password:')
    
    if len(password) > 0:
        result = requests.get(auth_url, auth=requests.auth.HTTPBasicAuth(user_name, password), verify=False)
        if result.status_code == 200:
            res_dict = json.loads(result.text)
            headers['Authorization'] = 'Bearer {0}'.format(res_dict['access_token'])
        else:
            raise Exception('Authentication failed. status_code: {0}'.format(result.status_code))
    else:
        print('User credential was not provided')    

    result = requests.get('http://localhost:9999/api/v1/kernels', headers=headers)
    print('result.status_code:', result.status_code)    
    print('result.text:', result.text)
    
    url = 'http://localhost:9999/api/v1/kernels/m2020-ingenium-10009/halt'
    result = requests.post(url, headers=headers)
    print('result.status_code:', result.status_code)    
    print('result.text:', result.text)
