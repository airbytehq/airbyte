#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
