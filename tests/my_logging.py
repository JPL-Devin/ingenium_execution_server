import logging

logFormatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(thread)-d] [%(levelname)-5.5s]  %(message)s')
logger = logging.getLogger('Global')

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

fileHandler = logging.FileHandler('log.txt', 'w')
logger.addHandler(fileHandler)    
fileHandler.setFormatter(logFormatter)

