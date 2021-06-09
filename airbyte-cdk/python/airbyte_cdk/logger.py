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


import traceback

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage


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
