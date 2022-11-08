#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from itertools import permutations
from unittest.mock import ANY, Mock

import pytest
from smartsheet.exceptions import ApiError
from source_smartsheets.sheet import SmartSheetAPIWrapper


def test_fetch_sheet(config, get_sheet_mocker):
    spreadsheet_id = config["spreadsheet_id"]
    sheet = SmartSheetAPIWrapper(config)
    mock, resp = get_sheet_mocker(sheet)

    sheet._fetch_sheet()
    mock.assert_called_once_with(spreadsheet_id, rows_modified_since=None, page_size=1)
    assert sheet.data == resp

    sheet._fetch_sheet(from_dt="2022-03-04T00:00:00Z")
    mock.assert_called_with(spreadsheet_id, rows_modified_since="2022-03-04T00:00:00Z")
    assert sheet.data == resp


def test_properties(config, get_sheet_mocker):
    sheet = SmartSheetAPIWrapper(config)
    _, resp = get_sheet_mocker(sheet)
    assert sheet.data == resp
    assert sheet.name == "aws_s3_sample"
    assert sheet.row_count == 4
    assert sheet.primary_key == "id"


@pytest.mark.parametrize(
    ("column_type", "expected_schema"),
    (
        ("TEXT_NUMBER", {"type": "string"}),
        ("DATE", {"type": "string", "format": "date"}),
        ("DATETIME", {"type": "string", "format": "date-time"}),
        ("DURATION", {"type": "string"}),
    ),
)
def test_column_types(config, column_type, expected_schema):
    sheet = SmartSheetAPIWrapper(config)
    assert sheet._column_to_property(column_type) == expected_schema


def test_json_schema(config, get_sheet_mocker):
    sheet = SmartSheetAPIWrapper(config)
    _ = get_sheet_mocker(sheet)
    json_schema = sheet.json_schema
    assert json_schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert json_schema["type"] == "object"
    assert "properties" in json_schema
    assert "modifiedAt" in json_schema["properties"]


def _make_api_error(code, message, name):
    result_mock = Mock(code=code, message=message)
    result_mock.name = name
    return ApiError(error=Mock(result=result_mock))


@pytest.mark.parametrize(
    ("side_effect", "expected_error"),
    (
        (Exception("Internal Server Error"), "Internal Server Error"),
        (
            _make_api_error(code=1006, message="Resource not found", name="Not Found"),
            "Not Found: 404 - Resource not found | Check your spreadsheet ID.",
        ),
        (
            _make_api_error(code=4003, message="Too many requests", name="Limit reached"),
            "Limit reached: 4003 - Too many requests | Check your spreadsheet ID.",
        ),
    ),
)
def test_check_connection_fail(mocker, config, side_effect, expected_error):
    sheet = SmartSheetAPIWrapper(config)
    with mocker.patch.object(sheet, "_get_sheet", side_effect=side_effect):
        status, error = sheet.check_connection(logger=logging.getLogger())
    assert error == expected_error
    assert status is False


def test_check_connection_success(mocker, config):
    sheet = SmartSheetAPIWrapper(config)
    with mocker.patch.object(sheet, "_get_sheet"):
        status, error = sheet.check_connection(logger=logging.getLogger())
    assert error is None
    assert status is True


_columns = [
    Mock(id="1101932201830276", title="id", type="TEXT_NUMBER"),
    Mock(id="5605531829200772", title="first_name", type="TEXT_NUMBER"),
    Mock(id="3353732015515524", title="last_name", type="TEXT_NUMBER"),
]


_cells = [
    Mock(column_id="1101932201830276", value="11"),
    Mock(column_id="5605531829200772", value="Leonardo"),
    Mock(column_id="3353732015515524", value="Dicaprio"),
]


@pytest.mark.parametrize(("row", "columns"), (*((perm, _columns) for perm in permutations(_cells)), ([], _columns), ([], [])))
def test_different_cell_order_produces_same_result(get_sheet_mocker, config, row, columns):
    sheet = SmartSheetAPIWrapper(config)
    sheet_mock = Mock(rows=[Mock(cells=row)] if row else [], columns=columns)
    get_sheet_mocker(sheet, data=Mock(return_value=sheet_mock))

    records = sheet.read_records(from_dt="2020-01-01T00:00:00Z")
    expected_records = [] if not row else [{"id": "11", "first_name": "Leonardo", "last_name": "Dicaprio", "modifiedAt": ANY}]
    assert list(records) == expected_records
