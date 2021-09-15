#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import logging
import sys
import traceback

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage


TRACE_LEVEL_NUM = 5


def get_logger():
    logging.setLoggerClass(AirbyteNativeLogger)
    logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
    logger = logging.getLogger('airbyte.source.zabbix')
    logger.setLevel(TRACE_LEVEL_NUM)
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(AirbyteLogFormatter())
    logger.addHandler(handler)
    return logger


class AirbyteLogFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        log_message = AirbyteMessage(type="LOG", log=AirbyteLogMessage(level=record.levelname, message=message))
        return log_message.json(exclude_unset=True)


class AirbyteNativeLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name)
        self.valid_log_types = {"FATAL": 50, "ERROR": 40, "WARN": 30, "INFO": 20, "DEBUG": 10, "TRACE": 5}

    def log_by_prefix(self, msg, default_level):
        split_line = msg.split()
        first_word = next(iter(split_line), None)
        if first_word in self.valid_log_types:
            log_level = self.valid_log_types.get(first_word)
            rendered_message = " ".join(split_line[1:])
        else:
            log_level = self.valid_log_types.get(default_level, 20)
            rendered_message = msg
        self.log(log_level, rendered_message)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        msg = f"{msg}\n{traceback.format_exc()}"
        self._log(logging.ERROR, msg, args, **kwargs)

    def trace(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL_NUM):
            self._log(TRACE_LEVEL_NUM, msg, args, **kwargs)


class AirbyteLogger:
    def __init__(self):
        self.valid_log_types = ["FATAL", "ERROR", "WARN", "INFO", "DEBUG", "TRACE"]

    def log_by_prefix(self, message, default_level):
        split_line = message.split()
        first_word = next(iter(split_line), None)
        if first_word in self.valid_log_types:
            log_level = first_word
            rendered_message = " ".join(split_line[1:])
        else:
            log_level = default_level
            rendered_message = message
        self.log(log_level, rendered_message)

    def log(self, level, message):
        log_record = AirbyteLogMessage(level=level, message=message)
        log_message = AirbyteMessage(type="LOG", log=log_record)
        print(log_message.json(exclude_unset=True))

    def fatal(self, message):
        self.log("FATAL", message)

    def exception(self, message):
        message = f"{message}\n{traceback.format_exc()}"
        self.error(message)

    def error(self, message):
        self.log("ERROR", message)

    def warn(self, message):
        self.log("WARN", message)

    def info(self, message):
        self.log("INFO", message)

    def debug(self, message):
        self.log("DEBUG", message)

    def trace(self, message):
        self.log("TRACE", message)
