import traceback
import json
import sys

def produce_exception(recursion_level=2):
    sys.stdout.flush()
    if recursion_level:
        produce_exception(recursion_level-1)
    else:
        x = 2/0.0

def call_function(f, recursion_level=2):
    if recursion_level:
        return call_function(f, recursion_level-1)
    else:
        return f()
        
if __name__ == '__main__':
    
    try:
        produce_exception(5)
    except Exception as e:
        print (dir(e))
        print ('str(e):', str(e))   
        print ('traceback.format_exc(1):', traceback.format_exc(1))
        print ('traceback.format_exc():', traceback.format_exc())
    
   
    
    try:
        produce_exception(5)
    except Exception as e:
        raise