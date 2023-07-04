import datetime as dt
import inspect
import logging
import logging.handlers
import sys
from typing import Callable


class MyFormatter(logging.Formatter):
    """Custom formatter for logging
    """
    converter = dt.datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        """! @brief redefinition of format of log
        """
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d %H:%M:%S")
            s = "%s,%03d" % (t, record.msecs)
        return s


class Logger:
    """Simple logger with a pretty log header
       the method error returns the value 1
       the method critical terminates a script work
    """

    def __init__(self):
        formatter = MyFormatter(
            fmt='[%(asctime)s] - %(levelname)-6s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S.%f')

        logger_name = __name__
        stack_items = inspect.stack()
        for i in range(len(stack_items)):
            if stack_items[i].filename.endswith("ci_common_utils/logger.py"):
                logger_name = ".".join(stack_items[i + 1].filename.split("/")[-3:])[:-3]

        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @classmethod
    def __prepare_log_line(cls, func_name: str, func: Callable) -> Callable:
        def wrapper(*args):
            prefix = ""
            stack_items = inspect.stack()
            for i in range(len(stack_items)):
                if stack_items[i].filename.endswith("ci_common_utils/logger.py"):
                    filepath = stack_items[i + 1].filename
                    line_number = stack_items[i + 1].lineno

                    # show last 3 path items only
                    filepath = "/".join(filepath.split("/")[-3:])
                    prefix = f"[{filepath}:{line_number}]"
                    break
            if prefix:
                args = list(args)
                args[0] = f"{prefix} # {args[0]}"
            func(*args)
            if func_name == "critical":
                sys.exit(1)
            elif func_name == "error":
                return 1
            return 0

        return wrapper

    def __getattr__(self, function_name: str):
        if not hasattr(self._logger, function_name):
            return super().__getattr__(function_name)
        return self.__prepare_log_line(function_name, getattr(self._logger, function_name), )
