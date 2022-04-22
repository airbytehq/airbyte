#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import sys
from io import StringIO

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, Status
from destination_google_sheets.destination import DestinationGoogleSheets
from unit_tests.test_helpers import TEST_CONFIG
from unit_tests.test_buffer import read_input_messages
from unit_tests.test_writer import TEST_CATALOG, TEST_SPREADSHEET, TEST_STREAM

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
TEST_DESTINATION = DestinationGoogleSheets()
# path to test records txt file
TEST_RECORDS_PATH: str = "unit_tests/test_data/test_destination_messages.txt"

# ----- BEGIN TESTS -----


def test_check():
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    actual = TEST_DESTINATION.check(logger=AirbyteLogger, config=TEST_CONFIG)
    assert actual == expected


def test_write():

    expected = [
        '{"type": "LOG", "log": {"level": "INFO", "message": "Writing data for stream: stream_1"}}',
        "No duplicated records found for stream: stream_1",
    ]
    # clean worksheet after previous test
    TEST_SPREADSHEET.clean_worksheet(TEST_STREAM)
    
    # perform test
    with CaptureStdOut() as output:
        list(
            TEST_DESTINATION.write(
                config=TEST_CONFIG, configured_catalog=TEST_CATALOG, input_messages=read_input_messages(TEST_RECORDS_PATH)
            )
        )
    assert output == expected

    # clean wks after the test
    test_wks = TEST_SPREADSHEET.open_worksheet(TEST_STREAM)
    TEST_SPREADSHEET.spreadsheet.del_worksheet(test_wks)
