"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import unittest
from unittest.mock import Mock, patch

from airbyte_protocol import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream
from google_sheets_source.client import GoogleSheetsClient
from google_sheets_source.helpers import Helpers
from google_sheets_source.models import CellData, GridData, RowData, Sheet, SheetProperties, Spreadsheet


class TestHelpers(unittest.TestCase):
    def test_headers_to_airbyte_stream(self):
        sheet_name = "sheet1"
        header_values = ["h1", "h2", "h3"]

        expected_stream = AirbyteStream(
            name=sheet_name,
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                # For simplicity, the type of every cell is a string
                "properties": {header: {"type": "string"} for header in header_values},
            },
        )

        actual_stream = Helpers.headers_to_airbyte_stream(sheet_name, header_values)
        self.assertEqual(expected_stream, actual_stream)

    def test_duplicate_headers_to_ab_stream_fails(self):
        sheet_name = "sheet1"
        header_values = ["h1", "h1", "h3"]
        with self.assertRaises(BaseException):
            Helpers.headers_to_airbyte_stream(sheet_name, header_values)

    def test_headers_to_airbyte_stream_blank_values_terminate_row(self):
        sheet_name = "sheet1"
        header_values = ["h1", "", "h3"]

        expected_stream = AirbyteStream(
            name=sheet_name,
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                # For simplicity, the type of every cell is a string
                "properties": {"h1": {"type": "string"}},
            },
        )
        actual_stream = Helpers.headers_to_airbyte_stream(sheet_name, header_values)

        self.assertEqual(expected_stream, actual_stream)

    def test_is_row_empty_with_empty_row(self):
        values = [" ", "", "     "]

        self.assertTrue(Helpers.is_row_empty(values))

    def test_is_row_empty_with_full_row(self):
        values = [" ", "", "     ", "somevaluehere"]

        self.assertFalse(Helpers.is_row_empty(values))

    def test_row_contains_relevant_data(self):
        values = ["c1", "c2", "c3"]
        relevant_indices = [2]
        self.assertTrue(Helpers.row_contains_relevant_data(values, relevant_indices))

    def test_row_contains_relevant_data_is_false(self):
        values = ["", "", "c3"]
        relevant_indices = [0, 1]
        self.assertFalse(Helpers.row_contains_relevant_data(values, relevant_indices))

    def test_parse_sheet_and_column_names_from_catalog(self):
        sheet1 = "soccer_team"
        sheet1_columns = frozenset(["arsenal", "chelsea", "manutd", "liverpool"])
        sheet1_schema = {"properties": {c: {"type": "string"} for c in sheet1_columns}}

        sheet2 = "basketball_teams"
        sheet2_columns = frozenset(["gsw", "lakers"])
        sheet2_schema = {"properties": {c: {"type": "string"} for c in sheet2_columns}}

        catalog = ConfiguredAirbyteCatalog(
            streams=[
                ConfiguredAirbyteStream(stream=AirbyteStream(name=sheet1, json_schema=sheet1_schema)),
                ConfiguredAirbyteStream(stream=AirbyteStream(name=sheet2, json_schema=sheet2_schema)),
            ]
        )

        actual = Helpers.parse_sheet_and_column_names_from_catalog(catalog)

        expected = {sheet1: sheet1_columns, sheet2: sheet2_columns}
        self.assertEqual(actual, expected)

    def test_row_data_to_record_message(self):
        sheet = "my_sheet"
        cell_values = ["v1", "v2", "v3", "v4"]
        column_index_to_name = {0: "c1", 3: "c4"}

        actual = Helpers.row_data_to_record_message(sheet, cell_values, column_index_to_name)

        expected = AirbyteRecordMessage(stream=sheet, data={"c1": "v1", "c4": "v4"}, emitted_at=1)
        self.assertEqual(expected.stream, actual.stream)
        self.assertEqual(expected.data, actual.data)

    def test_get_formatted_row_values(self):
        expected = [str(i) for i in range(10)]
        row_data = RowData(values=[CellData(formattedValue=x) for x in expected])

        actual = Helpers.get_formatted_row_values(row_data)

        self.assertEqual(expected, actual)

    def test_get_first_row(self):
        spreadsheet_id = "123"
        sheet = "s1"
        expected_first_row = ["1", "2", "3", "4"]
        fake_response = Spreadsheet(
            spreadsheetId=spreadsheet_id,
            sheets=[Sheet(data=[GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in expected_first_row])])])],
        )

        client = Mock()
        client.get.return_value.execute.return_value = fake_response
        with patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes: None):
            sheet_client = GoogleSheetsClient({"fake": "credentials"}, ["auth_scopes"])
            sheet_client.client = client
        actual = Helpers.get_first_row(sheet_client, spreadsheet_id, sheet)
        self.assertEqual(expected_first_row, actual)
        client.get.assert_called_with(spreadsheetId=spreadsheet_id, includeGridData=True, ranges=f"{sheet}!1:1")

    def test_get_sheets_in_spreadsheet(self):
        spreadsheet_id = "id1"
        expected_sheets = ["s1", "s2"]
        client = Mock()
        client.get.return_value.execute.return_value = Spreadsheet(
            spreadsheetId=spreadsheet_id, sheets=[Sheet(properties=SheetProperties(title=t)) for t in expected_sheets]
        )
        with patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes: None):
            sheet_client = GoogleSheetsClient({"fake": "credentials"}, ["auth_scopes"])
            sheet_client.client = client
        actual_sheets = Helpers.get_sheets_in_spreadsheet(sheet_client, spreadsheet_id)

        self.assertEqual(expected_sheets, actual_sheets)
        client.get.assert_called_with(spreadsheetId=spreadsheet_id, includeGridData=False)

    def test_get_available_sheets_to_column_index_to_name(self):
        # To mock different return values depending on input args, we use side effects with this method
        spreadsheet_id = "123"
        sheet1 = "s1"
        sheet1_first_row = ["1", "2", "3", "4"]

        # Since pytest and unittest don't give a clean way to mock responses for exact input arguments,
        # we use .side_effect to achieve this. This dict structure is spreadsheet_id -> includeGridData -> ranges
        def mock_client_call(spreadsheetId, includeGridData, ranges=None):
            if spreadsheetId != spreadsheet_id:
                return None
            # the spreadsheet only contains sheet1
            elif not includeGridData and ranges is None:
                mocked_return = Spreadsheet(spreadsheetId=spreadsheet_id, sheets=[Sheet(properties=SheetProperties(title=sheet1))])
            elif includeGridData and ranges == f"{sheet1}!1:1":
                mocked_return = Spreadsheet(
                    spreadsheetId=spreadsheet_id,
                    sheets=[Sheet(data=[GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in sheet1_first_row])])])],
                )

            m = Mock()
            m.execute.return_value = mocked_return
            return m

        client = Mock()
        client.get.side_effect = mock_client_call
        with patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes: None):
            sheet_client = GoogleSheetsClient({"fake": "credentials"}, ["auth_scopes"])
            sheet_client.client = client
        actual = Helpers.get_available_sheets_to_column_index_to_name(
            sheet_client, spreadsheet_id, {sheet1: frozenset(sheet1_first_row), "doesnotexist": frozenset(["1", "2"])}
        )
        expected = {sheet1: {0: "1", 1: "2", 2: "3", 3: "4"}}

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
