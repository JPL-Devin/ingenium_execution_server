import time
from datetime import datetime, timedelta
from ingenium_embedded import ingenium_config as ic
import test_config as tc
import os
import jwt


# utility to determine if string associated to time types: ERT or SCET are acceptable datetime formats.
def is_iso (ftime):
  time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
  try:
     datetime.strptime(truncate_nano(ftime),time_format)
     return True
  except ValueError:
     return False

# datetime miliseconds can be up to 6 digits long, this shortens the miliseconds so that it works appropriately with date time formatting.
def truncate_nano (ftime):
  splittime = ftime.split('.')
  millis = str(splittime[1])
  # if number of digits after decimal point is greater than 6
  # meaning nano-precision, then truncate everything up to the 6th digit
  if len(millis) > 6:
    millis = millis[0:6]
  return (splittime[0]+'.'+millis)

# return the number of seconds since the epoch in string format
def get_current_time_str():
    return str(time.time())

def get_current_utc():
    current_time = datetime.utcnow()
    new_datetime = datetime.strftime(current_time, '%Y-%m-%dT%H:%M:%S.%f')  
    return new_datetime[:-3] 
    
# get current time in UTC DOY format (currently now used. Venue Service return time in UTC format)    
def get_current_doy():
    current_time = datetime.utcnow()
    new_datetime = datetime.strftime(current_time, '%Y-%jT%H:%M:%S.%f')  
    return new_datetime[:-3] 
    
def get_test_time():

    current_time = datetime.utcnow()
    start_time = current_time - timedelta(days=2)

    start_formatted_time = datetime.strftime(start_time, '%Y-%jT%H:%M:%S')
    end_formatted_time = datetime.strftime(current_time, '%Y-%jT%H:%M:%S')

    return start_formatted_time, end_formatted_time

def get_auth_header():

    exec_private_pem = os.environ.get('EXEC_VENUE_PRIVATE_PEM')
    token =  {'scopes': ['admin',
                            'config_mgmt',
                            'execute:sit',
                            'execute:testbed',
                            'execute:wsts',
                            'execute:other',
                            'basic'],
              'username': "pchung"}

    jwt_token = jwt.encode(token, exec_private_pem, algorithm="RS256")
    jwt_token_str = jwt_token.decode('utf-8')
    ic.venue_token = jwt_token_str
    ic.header["Authorization"] = "Bearer {}".format(ic.venue_token)
    return ic.header

def get_ing_auth_header():

    private_pem = os.environ.get('PRIVATE_PEM')
    token =  {'scopes': ['admin',
                            'config_mgmt',
                            'execute:sit',
                            'execute:testbed',
                            'execute:wsts',
                            'execute:other',
                            'basic'],
              'username': "pchung"}

    jwt_token = jwt.encode(token, private_pem, algorithm="RS256")
    jwt_token_str = jwt_token.decode('utf-8')
    ic.ing_token = jwt_token_str
    ic.header["Authorization"] = "Bearer {}".format(ic.ing_token)
    return ic.header


def get_venue_sim_auth_header():
    exec_private_pem = os.environ.get('EXEC_VENUE_PRIVATE_PEM')
    token =  {'scopes': ['admin',
                            'config_mgmt',
                            'execute:sit',
                            'execute:testbed',
                            'execute:wsts',
                            'execute:other',
                            'basic'],
              'username': "pchung"}

    jwt_token = jwt.encode(token, exec_private_pem, algorithm="RS256")
    jwt_token_str = jwt_token.decode('utf-8')
    tc.venue_token = jwt_token_str
    tc.venue_header["Authorization"] = "Bearer {}".format(tc.venue_token)
    return tc.venue_header  
