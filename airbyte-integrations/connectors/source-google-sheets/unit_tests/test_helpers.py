#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import unittest
from unittest.mock import Mock, patch

from source_google_sheets.client import GoogleSheetsClient
from source_google_sheets.helpers import Helpers
from source_google_sheets.models import CellData, GridData, RowData, Sheet, SheetProperties, Spreadsheet

from airbyte_cdk.models.airbyte_protocol import (
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)


logger = logging.getLogger("airbyte")


def google_sheet_client(row_data, spreadsheet_id, client):
    fake_response = Spreadsheet(
        spreadsheetId=spreadsheet_id,
        sheets=[Sheet(data=[GridData(rowData=row_data)])],
    )
    client.get.return_value.execute.return_value = fake_response
    with patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes: None):
        sheet_client = GoogleSheetsClient({"fake": "credentials"}, ["auth_scopes"])
        sheet_client.client = client
    return sheet_client


def google_sheet_invalid_client(spreadsheet_id, client):
    fake_response = Spreadsheet(
        spreadsheetId=spreadsheet_id,
        sheets=[Sheet(data=[])],
    )
    client.get.return_value.execute.return_value = fake_response
    with patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes: None):
        sheet_client = GoogleSheetsClient({"fake": "credentials"}, ["auth_scopes"])
        sheet_client.client = client
    return sheet_client


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
            supported_sync_modes=[SyncMode.full_refresh],
        )

        actual_stream = Helpers.headers_to_airbyte_stream(logger, sheet_name, header_values)
        self.assertEqual(expected_stream, actual_stream)

    def test_duplicate_headers_retrieved(self):
        header_values = ["h1", "h1", "h3"]

        expected_valid_header_values = ["h3"]
        expected_duplicate_header_values = ["h1"]

        actual_header_values, actual_duplicate_header_values = Helpers.get_valid_headers_and_duplicates(header_values)

        self.assertEqual(expected_duplicate_header_values, actual_duplicate_header_values)
        self.assertEqual(expected_valid_header_values, actual_header_values)

    def test_duplicate_headers_to_ab_stream_ignores_duplicates(self):
        sheet_name = "sheet1"
        header_values = ["h1", "h1", "h3"]

        # h1 is ignored because it is duplicate
        expected_stream_header_values = ["h3"]
        expected_stream = AirbyteStream(
            name=sheet_name,
            json_schema={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                # For simplicity, the type of every cell is a string
                "properties": {header: {"type": "string"} for header in expected_stream_header_values},
            },
            supported_sync_modes=[SyncMode.full_refresh],
        )

        actual_stream = Helpers.headers_to_airbyte_stream(logger, sheet_name, header_values)
        self.assertEqual(expected_stream, actual_stream)

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
            supported_sync_modes=[SyncMode.full_refresh],
        )
        actual_stream = Helpers.headers_to_airbyte_stream(logger, sheet_name, header_values)

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
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name=sheet1, json_schema=sheet1_schema, supported_sync_modes=["full_refresh"]),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                ),
                ConfiguredAirbyteStream(
                    stream=AirbyteStream(name=sheet2, json_schema=sheet2_schema, supported_sync_modes=["full_refresh"]),
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.overwrite,
                ),
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
        row_data = [RowData(values=[CellData(formattedValue=v) for v in expected_first_row])]
        client = Mock()
        sheet_client = google_sheet_client(row_data, spreadsheet_id, client)
        actual = Helpers.get_first_row(sheet_client, spreadsheet_id, sheet)
        self.assertEqual(expected_first_row, actual)
        client.get.assert_called_with(spreadsheetId=spreadsheet_id, includeGridData=True, ranges=f"{sheet}!1:1")

    def test_get_first_row_empty_sheet(self):
        spreadsheet_id = "123"
        sheet = "s1"
        row_data = []
        client = Mock()
        sheet_client = google_sheet_client(row_data, spreadsheet_id, client)
        self.assertEqual(Helpers.get_first_row(sheet_client, spreadsheet_id, sheet), [])
        client.get.assert_called_with(spreadsheetId=spreadsheet_id, includeGridData=True, ranges=f"{sheet}!1:1")

    def test_check_sheet_is_valid(self):
        spreadsheet_id = "123"
        sheet = "s1"
        expected_first_row = ["1", "2", "3", "4"]
        row_data = [RowData(values=[CellData(formattedValue=v) for v in expected_first_row])]
        client = Mock()
        sheet_client = google_sheet_client(row_data, spreadsheet_id, client)
        is_valid, reason = Helpers.check_sheet_is_valid(sheet_client, spreadsheet_id, sheet)
        self.assertTrue(is_valid)
        self.assertEqual(reason, "")

    def test_check_sheet_is_valid_empty(self):
        spreadsheet_id = "123"
        sheet = "s1"
        client = Mock()
        sheet_client = google_sheet_invalid_client(spreadsheet_id, client)
        is_valid, reason = Helpers.check_sheet_is_valid(sheet_client, spreadsheet_id, sheet)
        self.assertFalse(is_valid)
        self.assertEqual(reason, "Expected data for exactly one range for sheet s1")

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

        expected = {sheet1: {0: "1", 1: "2", 2: "3", 3: "4"}}

        # names_conversion = False
        actual = Helpers.get_available_sheets_to_column_index_to_name(
            client=sheet_client,
            spreadsheet_id=spreadsheet_id,
            requested_sheets_and_columns={sheet1: frozenset(sheet1_first_row), "doesnotexist": frozenset(["1", "2"])},
        )
        self.assertEqual(expected, actual)

        # names_conversion = False, with null header cell
        sheet1_first_row = ["1", "2", "3", "4", None]
        expected = {sheet1: {0: "1", 1: "2", 2: "3", 3: "4", 4: None}}
        actual = Helpers.get_available_sheets_to_column_index_to_name(
            client=sheet_client,
            spreadsheet_id=spreadsheet_id,
            requested_sheets_and_columns={sheet1: frozenset(sheet1_first_row), "doesnotexist": frozenset(["1", "2"])},
        )
        self.assertEqual(expected, actual)

        # names_conversion = True, with null header cell
        sheet1_first_row = ["AB", "Some Header", "Header", "4", "1MyName", None]
        expected = {sheet1: {0: "ab", 1: "some_header", 2: "header", 3: "_4", 4: "_1_my_name", 5: None}}
        actual = Helpers.get_available_sheets_to_column_index_to_name(
            client=sheet_client,
            spreadsheet_id=spreadsheet_id,
            requested_sheets_and_columns={sheet1: frozenset(sheet1_first_row), "doesnotexist": frozenset(["1", "2"])},
            names_conversion=True,
        )

        self.assertEqual(expected, actual)

    def test_get_spreadsheet_id(self):
        test_url = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGegwY_GdV1B_cPP9re66xI8uJK25dtY9Q/edit#gid=1820065035"
        result = Helpers.get_spreadsheet_id(test_url)
        self.assertEqual("18vWlVH8BfjGegwY_GdV1B_cPP9re66xI8uJK25dtY9Q", result)

        test_url = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGa-gwYGdV1BjcPP9re66xI8uJK25dtY9Q/edit"
        result = Helpers.get_spreadsheet_id(test_url)
        self.assertEqual("18vWlVH8BfjGa-gwYGdV1BjcPP9re66xI8uJK25dtY9Q", result)

        test_url = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q/"
        result = Helpers.get_spreadsheet_id(test_url)
        self.assertEqual("18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q", result)

        test_url = "https://docs.google.com/spreadsheets/d/18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q/#"
        result = Helpers.get_spreadsheet_id(test_url)
        self.assertEqual("18vWlVH8BfjGegwY_GdV1BjcPP9re_6xI8uJ-25dtY9Q", result)

        test_url = "18vWlVH8BfjGegwY_GdV1BjcPP9re66xI8uJK25dtY9Q"
        result = Helpers.get_spreadsheet_id(test_url)
        self.assertEqual("18vWlVH8BfjGegwY_GdV1BjcPP9re66xI8uJK25dtY9Q", result)


if __name__ == "__main__":
    unittest.main()
