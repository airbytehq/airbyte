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

from collections import defaultdict
from datetime import datetime
from typing import Dict, FrozenSet, Iterable, List

from airbyte_protocol import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog
from google.oauth2 import service_account
from googleapiclient import discovery

from .models.spreadsheet import RowData, Spreadsheet

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]


class Helpers(object):
    @staticmethod
    def get_authenticated_sheets_client(credentials: Dict[str, str], scopes: List[str] = SCOPES) -> discovery.Resource:
        creds = Helpers.get_authenticated_google_credentials(credentials, scopes)
        return discovery.build("sheets", "v4", credentials=creds).spreadsheets()

    @staticmethod
    def get_authenticated_drive_client(credentials: Dict[str, str], scopes: List[str] = SCOPES) -> discovery.Resource:
        creds = Helpers.get_authenticated_google_credentials(credentials, scopes)
        return discovery.build("drive", "v3", credentials=creds)

    @staticmethod
    def get_authenticated_google_credentials(credentials: Dict[str, str], scopes: List[str] = SCOPES):
        return service_account.Credentials.from_service_account_info(credentials, scopes=scopes)

    @staticmethod
    def headers_to_airbyte_stream(sheet_name: str, header_row_values: List[str]) -> AirbyteStream:
        """
        Parses sheet headers from the provided row. This method assumes that data is contiguous
        i.e: every cell contains a value and the first cell which does not contain a value denotes the end
        of the headers. For example, if the first row contains "One | Two | | Three" then this method
        will parse the headers as ["One", "Two"]. This assumption is made for simplicity and can be modified later.
        """
        fields = []
        for cell_value in header_row_values:
            if cell_value:
                if cell_value in fields:
                    raise Exception(f"Duplicate header {cell_value} found in {sheet_name}. Please ensure all headers are unique")
                else:
                    fields.append(cell_value)
            else:
                break

        sheet_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            # For simplicity, the type of every cell is a string
            "properties": {field: {"type": "string"} for field in fields},
        }

        return AirbyteStream(name=sheet_name, json_schema=sheet_json_schema)

    @staticmethod
    def get_formatted_row_values(row_data: RowData) -> List[str]:
        """
        Gets the formatted values of all cell data in this row. A formatted value is the final value a user sees in a spreadsheet. It can be a raw
        string input by the user, or the result of a sheets function call.
        """
        return [value.formattedValue for value in row_data.values]

    @staticmethod
    def get_first_row(client, spreadsheet_id: str, sheet_name: str) -> List[str]:
        spreadsheet = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=True, ranges=f"{sheet_name}!1:1"))

        # There is only one sheet since we are specifying the sheet in the requested ranges.
        returned_sheets = spreadsheet.sheets
        if len(returned_sheets) != 1:
            raise Exception(f"Unexpected return result: Sheet {sheet_name} was expected to contain data on exactly 1 sheet. ")

        range_data = returned_sheets[0].data
        if len(range_data) != 1:
            raise Exception(f"Expected data for exactly one range for sheet {sheet_name}")

        all_row_data = range_data[0].rowData
        if not all_row_data or len(all_row_data) != 1:
            raise Exception(f"Expected data for exactly one row for sheet {sheet_name}")

        first_row_data = all_row_data[0]

        return Helpers.get_formatted_row_values(first_row_data)

    @staticmethod
    def parse_sheet_and_column_names_from_catalog(catalog: ConfiguredAirbyteCatalog) -> Dict[str, FrozenSet[str]]:
        sheet_to_column_name = {}
        for configured_stream in catalog.streams:
            stream = configured_stream.stream
            sheet_name = stream.name
            sheet_to_column_name[sheet_name] = frozenset(stream.json_schema["properties"].keys())

        return sheet_to_column_name

    @staticmethod
    def row_data_to_record_message(sheet_name: str, cell_values: List[str], column_index_to_name: Dict[int, str]) -> AirbyteRecordMessage:
        data = {}
        for relevant_index in sorted(column_index_to_name.keys()):
            if relevant_index >= len(cell_values):
                break

            cell_value = cell_values[relevant_index]
            if cell_value.strip() != "":
                data[column_index_to_name[relevant_index]] = cell_value

        return AirbyteRecordMessage(stream=sheet_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000)

    @staticmethod
    def get_available_sheets_to_column_index_to_name(
        client, spreadsheet_id: str, requested_sheets_and_columns: Dict[str, FrozenSet[str]]
    ) -> Dict[str, Dict[int, str]]:
        available_sheets = Helpers.get_sheets_in_spreadsheet(client, spreadsheet_id)

        available_sheets_to_column_index_to_name = defaultdict(dict)
        for sheet, columns in requested_sheets_and_columns.items():
            if sheet in available_sheets:
                first_row = Helpers.get_first_row(client, spreadsheet_id, sheet)
                # Find the column index of each header value
                idx = 0
                for cell_value in first_row:
                    if cell_value in columns:
                        available_sheets_to_column_index_to_name[sheet][idx] = cell_value
                    idx += 1
        return available_sheets_to_column_index_to_name

    @staticmethod
    def get_sheets_in_spreadsheet(client, spreadsheet_id: str) -> List[str]:
        spreadsheet_metadata = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=False))
        return [sheet.properties.title for sheet in spreadsheet_metadata.sheets]

    @staticmethod
    def get_sheet_row_count(client, spreadsheet_id: str) -> Dict[str, int]:
        spreadsheet_metadata = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=False))
        return {sheet.properties.title: sheet.properties.gridProperties["rowCount"] for sheet in spreadsheet_metadata.sheets}

    @staticmethod
    def is_row_empty(cell_values: List[str]) -> bool:
        for cell in cell_values:
            if cell.strip() != "":
                return False
        return True

    @staticmethod
    def row_contains_relevant_data(cell_values: List[str], relevant_indices: Iterable[int]) -> bool:
        for idx in relevant_indices:
            if len(cell_values) > idx and cell_values[idx].strip() != "":
                return True
        return False
