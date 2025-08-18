import time
from datetime import datetime
print('starting run', datetime.utcnow())
t0 = time.time()
import sys
import json
import importlib

t1 = time.time()

if __name__ == '__main__':

    time0 = time.time()
    if len(sys.argv) < 3:
        print('USAGE: python run_step.py input_step_path output_step_path')
        sys.exit(1)

    input_step_path = sys.argv[1]
    output_step_path = sys.argv[2]

    print('input_step_path', input_step_path)
    print('output_step_path', output_step_path)

    time1 = time.time()

    with open(input_step_path) as input_file:
        input_step = json.load(input_file)

    code_name = input_step['code']['name']

    module_name = code_name.split('.')[0]

    full_module_name = f'ingenium_embedded.{module_name}'

    time2 = time.time()    

    step_module = importlib.import_module(full_module_name)

    time3 = time.time()

    output_step = step_module.run(input_step)

    time4 = time.time()

    with open(output_step_path, 'w') as output_file:
        json.dump(output_step, output_file)

    time5 = time.time()    

    print('time1-time0:', time1-time0)
    print('time2-time1:', time2-time1)
    print('time3-time2:', time3-time2)
    print('time4-time3:', time4-time3)
    print('time5-time4:', time5-time4)

    t2 = time.time()

    print('t1-t0:', t1-t0)
    print('t2-t1:', t2-t1)

    print('ending run', datetime.utcnow())



