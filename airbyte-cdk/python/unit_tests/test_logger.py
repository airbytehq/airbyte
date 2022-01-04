#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import logging
import subprocess
import sys
from typing import Dict

import pytest
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage


@pytest.fixture(scope="session")
def logger():
    logger = logging.getLogger("airbyte.Testlogger")
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


def test_level_transform(logger, caplog):
    formatter = AirbyteLogFormatter()
    logger.warning("Test level transform warn")
    logger.critical("Test level transform critical")
    record_warn = caplog.records[0]
    record_critical = caplog.records[1]
    formatted_record_warn = formatter.format(record_warn)
    formatted_record_warn_data = json.loads(formatted_record_warn)
    log_warn = formatted_record_warn_data.get("log")
    level_warn = log_warn.get("level")
    formatted_record_critical = formatter.format(record_critical)
    formatted_record_critical_data = json.loads(formatted_record_critical)
    log_critical = formatted_record_critical_data.get("log")
    level_critical = log_critical.get("level")
    assert level_warn == "WARN"
    assert level_critical == "FATAL"


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


def test_unhandled_logger():
    cmd = "from airbyte_cdk.logger import init_logger; init_logger('airbyte'); raise 1"
    expected_message = (
        "exceptions must derive from BaseException\n"
        "Traceback (most recent call last):\n"
        '  File "<string>", line 1, in <module>\n'
        "TypeError: exceptions must derive from BaseException"
    )
    log_message = AirbyteMessage(type="LOG", log=AirbyteLogMessage(level="FATAL", message=expected_message))
    expected_output = log_message.json(exclude_unset=True)

    with pytest.raises(subprocess.CalledProcessError) as err:
        subprocess.check_output([sys.executable, "-c", cmd], stderr=subprocess.STDOUT)

    assert not err.value.stderr, "nothing on the stderr"
    assert err.value.output.decode("utf-8").strip() == expected_output, "Error should be printed in expected form"
