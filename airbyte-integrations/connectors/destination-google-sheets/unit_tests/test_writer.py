#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_google_sheets.writer import GoogleSheetsWriter
from googleapiclient.errors import HttpError

from airbyte_cdk.models import FailureType
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


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


class _GoogleApiResponse:
    status = 400
    reason = "Bad Request"

    def __getitem__(self, key):
        return str(getattr(self, key))


class _FailingWorksheetWithCellLimit:
    def append_table(self, values, start, dimension):
        content = (
            b'{"error":{"message":"This action would increase the number of cells in the workbook above the limit of 10000000 cells."}}'
        )
        raise HttpError(_GoogleApiResponse(), content)


class _FailingWorksheetWithOtherError:
    def append_table(self, values, start, dimension):
        content = b'{"error":{"message":"Invalid value at data.values."}}'
        raise HttpError(_GoogleApiResponse(), content)


class _FailingSpreadsheetWithCellLimit:
    def set_headers(self, stream_name, headers):
        return None

    def open_worksheet(self, stream_name):
        return _FailingWorksheetWithCellLimit()


class _FailingSpreadsheetWithOtherError:
    def set_headers(self, stream_name, headers):
        return None

    def open_worksheet(self, stream_name):
        return _FailingWorksheetWithOtherError()


def test_write_from_queue_raises_config_error_for_google_sheets_cell_limit():
    writer = GoogleSheetsWriter(_FailingSpreadsheetWithCellLimit())
    stream_name = "stream_1"
    writer.stream_info[stream_name] = {"headers": ["id"], "is_set": False}
    writer.records_buffer[stream_name] = [["1"]]

    with pytest.raises(AirbyteTracedException) as exc_info:
        writer.write_from_queue(stream_name)

    assert exc_info.value.failure_type == FailureType.config_error
    assert exc_info.value.message == "Google Sheets spreadsheet exceeds the 10,000,000-cell limit."
    assert "limit of 10000000 cells" in exc_info.value.internal_message


def test_write_from_queue_preserves_other_google_api_errors():
    writer = GoogleSheetsWriter(_FailingSpreadsheetWithOtherError())
    stream_name = "stream_1"
    writer.stream_info[stream_name] = {"headers": ["id"], "is_set": False}
    writer.records_buffer[stream_name] = [["1"]]

    with pytest.raises(HttpError) as exc_info:
        writer.write_from_queue(stream_name)

    assert "Invalid value at data.values" in str(exc_info.value)
