#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import re
from datetime import datetime, timedelta

import pytest
from ci_credentials.logger import Logger


LOG_RE = re.compile(r"^\[(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{6})\] -" r"\s+(\w+)\s+- \[.*tests/test_logger.py:(\d+)\] # (.+)")
LOGGER = Logger()
TEST_MESSAGE = "sbhY=)9'v-}LT=)jjF66(XrZh=]>7Xp\"?/zCz,=eu8K47u8"


def check_output(msg: str, expected_line_number: int, expected_log_level: str):
    m = LOG_RE.match(msg)
    assert m is not None, f"incorrect message format, pattern: {LOG_RE.pattern}, message: {msg}"
    date_time, log_level, line_number, msg = m.groups()

    assert int(line_number) == expected_line_number
    assert log_level == expected_log_level
    assert log_level == expected_log_level
    dt = datetime.strptime(date_time, "%d/%m/%Y %H:%M:%S.%f")
    now = datetime.now()
    delta = timedelta(seconds=1)
    assert now - delta < dt < now


@pytest.mark.parametrize(
    "log_func,expected_log_level,expected_code",
    ((LOGGER.debug, "DEBUG", 0), (LOGGER.warning, "WARNING", 0), (LOGGER.info, "INFO", 0), (LOGGER.error, "ERROR", 1)),
)
def test_log_message(capfd, log_func, expected_log_level, expected_code):
    assert log_func(TEST_MESSAGE) == expected_code
    _, err = capfd.readouterr()
    check_output(err, 36, expected_log_level)


def test_critical_message(capfd):
    with pytest.raises(SystemExit) as (err):
        LOGGER.critical(TEST_MESSAGE)
    _, err = capfd.readouterr()
    check_output(err, 43, "CRITICAL")
