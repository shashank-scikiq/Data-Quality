import logging
import sys
import inspect

def start_log():
	logger = logging.getLogger(__name__)
	if logger.handlers:
		return logger
	str_handler = logging.StreamHandler(sys.stdout)
	formatter = logging.Formatter('%(levelname)s: [%(asctime)s]:: %(message)s')
	str_handler.setFormatter(formatter)
	logger.addHandler(str_handler)
	logger.setLevel(logging.DEBUG)

	# Get the name of the module where the logger is being used
	frame = inspect.stack()[1]
	module = inspect.getmodule(frame[0])
	module_name = module.__name__ if module else 'Unknown module'

	# Log the module name
	logger.info(f"Logger started for module: {module_name}")
	return logger