import os
import jwt
import json
import getpass
from functools import wraps
import requests

public_pem = os.environ.get('PUBLIC_PEM')

options = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}

def require_jwt(*required_scopes):
    def decorator(func):
        @wraps(func)
        def wrapper(jwt_token):
            print('required_scopes:', required_scopes)
            
            set_expected = set(required_scopes)
            
            try:
                jwt_decoded = jwt.decode(
                    jwt_token,
                    public_pem,
                    algorithms=['RS256'],
                    options=options
                )
                
                print('jwt_decoded:', json.dumps(jwt_decoded, indent=4))
                
                actual_scopes = jwt_decoded['scopes']
                
                set_actual = set(actual_scopes)
                
                if len(set_expected) > 0 and len(set_expected.intersection(set_actual)) == 0:
                    raise Exception('Requirement not met')                
                
                return func(jwt_token)
            
            except Exception as e:
                print('Error:', e)
                        
            # if len(set_expected) > 0 and len(set_expected.intersection(set_actual)) == 0:
            #    raise Exception('Requirement not met')
                
        return wrapper
    return decorator

@require_jwt('admin', 'execution')
def test_jwt1(jwt_token):
    print('test_jwt1 executed.')

@require_jwt('execute:wsts')
def test_jwt2(jwt_token):
    print('test_jwt2 executed.')
    
@require_jwt()
def test_jwt3(jwt_token):
    print('test_jwt3 executed.')
    
@require_jwt('big_scope')
def test_jwt4(jwt_token):
    print('test_jwt4 executed.')
        
if __name__ == '__main__':
    
    auth_url = 'https://100.64.153.42/api/v1/login'
    
    user_name = input('username:')
    password = getpass.getpass('password:')
    
    if len(password) > 0:
        print('login to:', auth_url)
        result = requests.get(auth_url, auth=requests.auth.HTTPBasicAuth(user_name, password), verify=False)
        if result.status_code == 200:
            res_dict = json.loads(result.text)
            jwt_token = res_dict['access_token']
            test_jwt1(jwt_token)
            
            test_jwt2(jwt_token)
            
            test_jwt3(jwt_token)
            
            test_jwt4(jwt_token)
        else:
            raise Exception('Authentication failed. status_code: {0}'.format(result.status_code))
    else:
        print('Authentication skipped')

    
