import json_logging, logging, sys

# log is initialized without a web framework name
json_logging.init_non_web(enable_json=True)

logger = logging.getLogger("test-logger")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

logger.info("test logging statement")
