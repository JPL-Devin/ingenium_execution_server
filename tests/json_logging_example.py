# This example shows how the logger can be set up to use a custom JSON format.
import logging
import json
import traceback
from datetime import datetime
import copy
import json_logging
import sys
from collections import OrderedDict

json_logging.ENABLE_JSON_LOGGING = True


def extra(**kw):
    '''Add the required nested props layer'''
    return {'extra': {'props': kw}}


class CustomJSONLog(logging.Formatter):
    """
    Customized logger
    """
    python_log_prefix = 'python.'
    def get_exc_fields(self, record):
        if record.exc_info:
            return self.format_exception(record.exc_info)
        elif record.exc_text:
            return record.exc_text
        else:
            return ''

    @classmethod
    def format_exception(cls, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    def format(self, record):
        json_log_object = OrderedDict()
        json_log_object['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        json_log_object['level'] = record.levelname
        json_log_object['message'] = record.getMessage()
        if hasattr(record, 'user_name'):
            json_log_object['user_name'] = record.user_name
        if hasattr(record, 'service'):
            json_log_object['service'] = record.service
        if hasattr(record, 'event'):
            json_log_object['event'] = record.event
        if hasattr(record, 'data'):
            json_log_object['data'] = record.data            

        if self.get_exc_fields(record):
            if 'data' not in json_log_object:
                json_log_object['data'] = OrderedDict()
                json_log_object['data']['details'] = [self.get_exc_fields(record)]
            else:
                details = json_log_object['data'].get('details', None)
                if details is None:
                    json_log_object['data']['details'] = [self.get_exc_fields(record)]
                elif isinstance(details, list):
                    details.append(self.get_exc_fields(record))
                else:
                    # keep the details 
                    pass

        return json.dumps(json_log_object)


def logger_init():
    json_logging.init(custom_formatter=CustomJSONLog)

# You would normally import logger_init and setup the logger in your main module - e.g.
# main.py

logger_init()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stderr))

if __name__ == '__main__':
    logger.info('Starting')
    logger.info('With some data', extra = {'service': 'EXEC_SERVER', 'event': 'ADD_STEP', 'data': {'error_type': 'USER_INPUT_ERROR'}})
    try:
        1/0
    except: # noqa pylint: disable=bare-except
        logger.exception('You cannot divide by zero')