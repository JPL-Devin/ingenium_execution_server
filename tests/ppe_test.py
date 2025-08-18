# example of the submit and use a callback pattern for the ProcessPoolExecutor
import time
from multiprocessing import current_process
from concurrent.futures import ProcessPoolExecutor
import os
import signal
import traceback

def get_pid():
    pid = current_process().pid
    print(f'pid: {pid}')
    return pid

# custom task that will sleep for a variable amount of time
def task(msg):
    # sleep for less than a second
    try:
        for i in range(5):
            time.sleep(1)
            print(f'msg {i}')
    except:
        print('except2')
        #print(traceback.format_exc())
    finally:
        print('finally2')

    return i
 
# custom callback function called on tasks when they complete
def my_callback(future):
    print('my callback')
    # retrieve the result
    ex = future.exception(None)
    if ex is None:
        print('<<<<<')
        try:
            res = future.result()
            print('my_callback res: ', res)
        except:
            print('Failed to get result')
        print('>>>>>')
    else:
        print('my_callback ex: ', ex)
 
# entry point
def main():
    # start the process pool
    with ProcessPoolExecutor(1) as executor:
        fut = executor.submit(get_pid)
        pid = fut.result()
        print(f'worker pid: {pid}') 

        future = executor.submit(task, 'hi')
        future.add_done_callback(my_callback)

        time.sleep(2)

        os.kill(pid, signal.SIGTERM)
        # wait for tasks to complete...
 
if __name__ == '__main__':
    main()