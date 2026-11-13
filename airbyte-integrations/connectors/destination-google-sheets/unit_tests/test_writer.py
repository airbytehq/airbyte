#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_google_sheets.writer import GoogleSheetsWriter
from googleapiclient.errors import HttpError

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils import AirbyteTracedException


class MockResponse:
    status = 400
    reason = "Bad Request"


class MockWorksheet:
    def append_table(self, values, start, dimension):
        raise HttpError(
            MockResponse(),
            b'{"error": {"message": "This action would increase the number of cells in the workbook above the limit of 10000000 cells."}}',
            uri="https://sheets.googleapis.com/v4/spreadsheets/test/values/test%21A2%3AZ383398:append",
        )


class MockSpreadsheet:
    def open_worksheet(self, stream_name):
        return MockWorksheet()


@pytest.mark.parametrize(
    "row, col, expected",
    [
        (0, 0, "A1"),
        (0, 25, "Z1"),
        (0, 26, "AA1"),
        (99, 18277, "ZZZ100"),
    ],
)
def test_a1_notation(row, col, expected):
    writer = GoogleSheetsWriter(None)
    assert writer._a1_notation(row, col) == expected


def test_write_from_queue_classifies_workbook_cell_limit_as_config_error():
    writer = GoogleSheetsWriter(MockSpreadsheet())
    writer.stream_info = {"calls": {"headers": ["id"], "is_set": True}}
    writer.records_buffer = {"calls": [["1"]]}

    with pytest.raises(AirbyteTracedException) as exc_info:
        writer.write_from_queue("calls")

    assert exc_info.value.message == "Google Sheets workbook exceeds the 10,000,000-cell limit."
    assert exc_info.value.failure_type == FailureType.config_error
    assert "above the limit of 10000000 cells" in exc_info.value.internal_message
