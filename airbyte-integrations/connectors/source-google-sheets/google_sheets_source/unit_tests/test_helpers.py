import unittest
from unittest.mock import patch, MagicMock, Mock
from apiclient import discovery

from ..helpers import Helpers
from ..models.generated import Values, RowData, CellData, Spreadsheet, Sheet, GridData
from airbyte_protocol import AirbyteCatalog, AirbyteStream, AirbyteMessage, AirbyteRecordMessage


class TestHelpers(unittest.TestCase):
    def test_headers_to_airbyte_stream(self):
        sheet_name = "sheet1"
        header_values = ["h1", "h2", "h3"]

        expected_stream = AirbyteStream(name=sheet_name, json_schema={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            # For simplicity, the type of every cell is a string
            "properties": {header: {"type": "string"} for header in header_values},
        })

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

        expected_stream = AirbyteStream(name=sheet_name, json_schema={
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            # For simplicity, the type of every cell is a string
            "properties": {"h1": {"type": "string"}},
        })
        actual_stream = Helpers.headers_to_airbyte_stream(sheet_name, header_values)

        self.assertEqual(expected_stream, actual_stream)

    def test_is_row_empty_with_empty_row(self):
        values = Values(__root__=[" ", "", "     "])

        self.assertTrue(Helpers.is_row_empty(values))

    def test_is_row_empty_with_full_row(self):
        values = Values(__root__=[" ", "", "     ", "somevaluehere"])

        self.assertFalse(Helpers.is_row_empty(values))

    def test_row_contains_relevant_data(self):
        values = Values(__root__=["c1", "c2", "c3"])
        relevant_indices = [2]
        self.assertTrue(Helpers.row_contains_relevant_data(values, relevant_indices))

    def test_row_contains_relevant_data_is_false(self):
        values = Values(__root__=["", "", "c3"])
        relevant_indices = [0, 1]
        self.assertFalse(Helpers.row_contains_relevant_data(values, relevant_indices))

    def test_parse_sheet_and_column_names_from_catalog(self):
        sheet1 = 'soccer_team'
        sheet1_columns = frozenset(['arsenal', 'chelsea', 'manutd', 'liverpool'])
        sheet1_schema = {"properties": {c: {'type': 'string'} for c in sheet1_columns}}

        sheet2 = 'basketball_teams'
        sheet2_columns = frozenset(['gsw', 'lakers'])
        sheet2_schema = {"properties": {c: {'type': 'string'} for c in sheet2_columns}}

        catalog = AirbyteCatalog(streams=[
            AirbyteStream(name=sheet1, json_schema=sheet1_schema),
            AirbyteStream(name=sheet2, json_schema=sheet2_schema)
        ])

        actual = Helpers.parse_sheet_and_column_names_from_catalog(catalog)

        expected = {sheet1: sheet1_columns, sheet2: sheet2_columns}
        self.assertEqual(actual, expected)

    def test_row_data_to_record_message(self):
        sheet = "my_sheet"
        cell_values = Values(__root__=['v1', 'v2', 'v3', 'v4'])
        column_index_to_name = {0: 'c1', 3: 'c4'}

        actual = Helpers.row_data_to_record_message(sheet, cell_values, column_index_to_name)

        expected = AirbyteRecordMessage(stream=sheet, data={'c1': 'v1', 'c4': 'v4'}, emitted_at=1)
        self.assertEqual(expected.stream, actual.stream)
        self.assertEqual(expected.data, actual.data)

    def test_get_formatted_row_values(self):
        expected = [str(i) for i in range(10)]
        row_data = RowData(values=[CellData(formattedValue=x) for x in expected])

        actual = Helpers.get_formatted_row_values(row_data)

        self.assertEqual(expected, actual)

    def test_get_first_row(self):
        spreadsheet_id = '123'
        sheet = "s1"
        expected_first_row = ['1', '2', '3', '4']
        fake_response = Spreadsheet(
            spreadsheetId=spreadsheet_id,
            sheets=[Sheet(data=[GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in expected_first_row])])])]
        )

        client = Mock()
        client.get.return_value.execute.return_value = fake_response

        actual = Helpers.get_first_row(client, spreadsheet_id, sheet)
        self.assertEqual(expected_first_row, actual)
        client.get.assert_called_with(spreadsheetId=spreadsheet_id, includeGridData=True, ranges=f"{sheet}!1:1")

    def get_available_sheets_to_column_index_to_name(self):
        spreadsheet_id = '123'
        sheet = "s1"
        expected_first_row = ['1', '2', '3', '4']
        fake_response = Spreadsheet(
            spreadsheetId=spreadsheet_id,
            sheets=[Sheet(data=[GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in expected_first_row])])])]
        )

        client = Mock()
        client.get.return_value.execute.return_value = fake_response

        actual = Helpers.get_available_sheets_to_column_index_to_name(client, spreadsheet_id, {sheet: frozenset(expected_first_row)})
        expected = {sheet: {0: '1', 1: '2', 2: '3', 3: '4'}}

        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
