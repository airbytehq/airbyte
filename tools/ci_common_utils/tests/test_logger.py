import re
from datetime import datetime, timedelta

import pytest

from ..ci_common_utils import Logger

# [20/10/2018 23:31:20.076283] - WARNING - [tests/test_logger.py:23] Entity1 test
log_re = re.compile(
    r'^\[(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}\.\d{6})\] -\s+(\w+)\s+- \[.*tests/test_logger.py:(\d+)\] # (.+)'
)

logger = Logger()

TEST_MESSAGE = """sbhY=)9'v-}LT=)jjF66(XrZh=]>7Xp"?/zCz,=eu8K47u8"""


def check_output(msg: str, expected_line_number: int, expected_log_level: str):
    m = log_re.match(msg)

    assert m is not None, f"incorrect log format, expected: {log_re.pattern}"
    date_time, log_level, line_number, msg = m.groups()

    assert msg == TEST_MESSAGE
    assert log_level == expected_log_level

    dt = datetime.strptime(date_time, "%d/%m/%Y %H:%M:%S.%f")
    now = datetime.now()
    assert (now - timedelta(seconds=1)) < dt < now

    assert int(line_number) == expected_line_number


@pytest.mark.parametrize(
    "log_func,expected_log_level,expected_code", (
            (logger.debug, "DEBUG", 0),
            (logger.warning, "WARNING", 0),
            (logger.info, "INFO", 0),
            (logger.error, "ERROR", 1),
    )
)
def test_log_message(capfd, log_func, expected_log_level, expected_code):
    assert log_func(TEST_MESSAGE) == expected_code
    _, err = capfd.readouterr()
    check_output(err, 43, expected_log_level)


def test_critical_message(capfd):
    with pytest.raises(SystemExit) as err:
        logger.critical(TEST_MESSAGE)
    _, err = capfd.readouterr()
    check_output(err, 50, "CRITICAL")
