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


import json
from typing import Dict

import pytest
from airbyte_cdk.logger import AirbyteLogFormatter, init_logger


@pytest.fixture(scope="session")
def logger():
    logger = init_logger("Test logger")
    return logger


def test_formatter(logger, caplog):
    formatter = AirbyteLogFormatter()
    logger.info("Test formatter")
    record = caplog.records[0]
    formatted_record = formatter.format(record)
    formatted_record_data = json.loads(formatted_record)
    assert formatted_record_data.get("type") == "LOG"
    log = formatted_record_data.get("log")
    assert isinstance(log, Dict)
    level = log.get("level")
    message = log.get("message")
    assert level == "INFO"
    assert message == "Test formatter"


def test_trace(logger, caplog):
    logger.trace("Test trace 1")
    record = caplog.records[0]
    assert record.levelname == "TRACE"
    assert record.message == "Test trace 1"


def test_debug(logger, caplog):
    logger.debug("Test debug 1")
    record = caplog.records[0]
    assert record.levelname == "DEBUG"
    assert record.message == "Test debug 1"


def test_info(logger, caplog):
    logger.info("Test info 1")
    logger.info("Test info 2")
    assert len(caplog.records) == 2
    first_record = caplog.records[0]
    assert first_record.levelname == "INFO"
    assert first_record.message == "Test info 1"


def test_warn(logger, caplog):
    logger.warn("Test warn 1")
    record = caplog.records[0]
    assert record.levelname == "WARNING"
    assert record.message == "Test warn 1"


def test_error(logger, caplog):
    logger.error("Test error 1")
    record = caplog.records[0]
    assert record.levelname == "ERROR"
    assert record.message == "Test error 1"


def test_fatal(logger, caplog):
    logger.fatal("Test fatal 1")
    record = caplog.records[0]
    assert record.levelname == "CRITICAL"
    assert record.message == "Test fatal 1"
