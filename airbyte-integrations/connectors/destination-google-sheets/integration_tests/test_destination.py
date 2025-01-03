#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import sys
from io import StringIO

import pytest
from destination_google_sheets.destination import DestinationGoogleSheets
from integration_tests.test_buffer import read_input_messages
from integration_tests.test_helpers import TEST_CONFIG
from integration_tests.test_writer import TEST_CATALOG, TEST_SPREADSHEET, TEST_STREAM

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status


# ----- PREPARE ENV -----


class CaptureStdOut(list):
    """
    Captures the stdout messages into the variable list, that could be validated later.
    """

    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout


# define instance
TEST_DESTINATION: DestinationGoogleSheets = DestinationGoogleSheets()
# path to test records txt file
TEST_RECORDS_PATH: str = "integration_tests/test_data/test_destination_messages.txt"

# ----- BEGIN TESTS -----


def test_check():
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    actual = TEST_DESTINATION.check(logger=AirbyteLogger, config=TEST_CONFIG)
    assert actual == expected


@pytest.mark.parametrize(
    "expected, raised",
    [
        ('{"type": "LOG", "log": {"level": "INFO", "message": "Auth session is expired. Refreshing..."}}', False),
        ('{"type": "LOG", "log": {"level": "INFO", "message": "Successfully refreshed auth session"}}', False),
        ('{"type": "LOG", "log": {"level": "INFO", "message": "Writing data for stream: stream_1"}}', True),
        ('{"type": "LOG", "log": {"level": "INFO", "message": "No duplicated records found for stream: stream_1"}}', True),
    ],
    ids=[
        "token needs refresh",
        "token refreshed",
        "writing stream",
        "no dups found for stream",
    ],
)
def test_write(expected, raised):
    # clean worksheet after previous test
    TEST_SPREADSHEET.clean_worksheet(TEST_STREAM)

    # perform test
    with CaptureStdOut() as output:
        list(
            TEST_DESTINATION.write(
                config=TEST_CONFIG, configured_catalog=TEST_CATALOG, input_messages=read_input_messages(TEST_RECORDS_PATH)
            )
        )

    assert True if not raised else any(msg == expected for msg in output)

    # clean wks after the test
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    TEST_SPREADSHEET.spreadsheet.del_worksheet(test_wks)
