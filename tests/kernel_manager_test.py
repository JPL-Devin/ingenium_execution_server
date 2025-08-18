from tornado import gen
from tornado.ioloop import IOLoop
import uuid
import json
import traceback
import logging

logFormatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(thread)-d] [%(levelname)-5.5s]  %(message)s')
logger = logging.getLogger('Global')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

logger.propagate = False

logger.level = logging.DEBUG

from gateway.kernel_manager import KernelManager

@gen.coroutine
def main():
    gateway_url = 'http://0.0.0.0:8888'
    gateway_ws_url = 'ws://0.0.0.0:8888'

    execution_id = str(uuid.uuid4())

    kernel_manager = KernelManager(gateway_url, gateway_ws_url)

    kernel_connection = yield kernel_manager.create_kernel(execution_id)

    print('kernel_connection ', str(kernel_connection))

    try:
        code1 = 'x1=2'
        print('code1:', code1)
        res1 = yield kernel_manager.execute_code(execution_id, code1)
        print('res1:', res1)

        code2 = 'x2=x1+3'
        print('code2:', code2)
        res2 = yield kernel_manager.execute_code(execution_id, code2)
        print('res2:', res2)

        code3 = 'x2'
        print('code3: ', code3)
        res3 = yield kernel_manager.execute_code(execution_id, code3)
        print('res3:', res3)

        code4 = 'manual_input_step.run({\"a1\":2})'
        print('code4: ', code4)
        res4 = yield kernel_manager.execute_code(execution_id, code4)
        print('res4:', res4)

        print('kernels', json.dumps(kernel_manager.get_kernel_infos(), indent=4))

        print('shutdown kernel')
        yield kernel_manager.shutdown_kernel(kernel_connection.execution_id)

        print('kernels', json.dumps(kernel_manager.get_kernel_infos(), indent=4))
    except:
        logger.warn(traceback.format_exc())

    # print 'sleep'
    # yield gen.sleep(5)

    print('done')

if __name__ == '__main__':
    IOLoop.current().run_sync(main)
