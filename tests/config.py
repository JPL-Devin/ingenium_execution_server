import time
import os
import jwt

import logging

logging.Formatter.converter = time.gmtime
logFormatter = logging.Formatter('[%(levelname)s]: [%(asctime)s.%(msecs)03dZ] - %(message)s', '%Y-%m-%dT%H:%M:%S')

logger = logging.getLogger('Global')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log_level_str = os.getenv('TEST_LOG_LEVEL', 'INFO')
level = logging.getLevelName(log_level_str)
logger.setLevel(level)
logger.addHandler(consoleHandler)

logger.propagate = False

def generate_token():
    iat = int(time.time())
    exp = iat + (30*60)
    
    private_pem = os.environ.get('PRIVATE_PEM')
    
    encoded = jwt.encode({'scopes': ['execute:wsts'],
                        'exp':exp,
                        'iat':iat,
                        'username':'hongmank'},
                         private_pem,
                         algorithm='RS256')
    
    # logger.debug('encoded: %s', encoded)
    return encoded

shared_dict = {}

server = os.environ.get('EXEC_SERVER_URL', 'http://127.0.0.1:9999')
api_path = '{0}/api/v4'.format(server)
logger.debug('api_path: %s', api_path)
shared_dict['host'] = api_path

headers = {'Content-Type': 'application/json',
              'Accept': 'application/json'}

token = generate_token()
token_str = token.decode('utf-8')
auth_header = 'Bearer {0}'.format(token_str)

logger.debug('auth_header: %s', auth_header)

headers['Authorization'] = auth_header

shared_dict['headers'] = headers






