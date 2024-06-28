#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Dict, FrozenSet, Iterable, List, Tuple

from airbyte_cdk.models.airbyte_protocol import AirbyteRecordMessage, AirbyteStream, ConfiguredAirbyteCatalog, SyncMode
from google.oauth2 import credentials as client_account
from google.oauth2 import service_account
from googleapiclient import discovery

from .models.spreadsheet import RowData, Spreadsheet
from .utils import safe_name_conversion

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly", "https://www.googleapis.com/auth/drive.readonly"]

logger = logging.getLogger("airbyte")


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
        auth_type = credentials.pop("auth_type")
        if auth_type == "Service":
            return service_account.Credentials.from_service_account_info(json.loads(credentials["service_account_info"]), scopes=scopes)
        elif auth_type == "Client":
            return client_account.Credentials.from_authorized_user_info(info=credentials)

    @staticmethod
    def headers_to_airbyte_stream(logger: logging.Logger, sheet_name: str, header_row_values: List[str]) -> AirbyteStream:
        """
        Parses sheet headers from the provided row. This method assumes that data is contiguous
        i.e: every cell contains a value and the first cell which does not contain a value denotes the end
        of the headers. For example, if the first row contains "One | Two | | Three" then this method
        will parse the headers as ["One", "Two"]. This assumption is made for simplicity and can be modified later.
        """
        fields, duplicate_fields = Helpers.get_valid_headers_and_duplicates(header_row_values)
        if duplicate_fields:
            logger.warn(f"Duplicate headers found in {sheet_name}. Ignoring them: {duplicate_fields}")

        sheet_json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            # For simplicity, the type of every cell is a string
            "properties": {field: {"type": "string"} for field in fields},
        }

        return AirbyteStream(name=sheet_name, json_schema=sheet_json_schema, supported_sync_modes=[SyncMode.full_refresh])

    @staticmethod
    def get_valid_headers_and_duplicates(header_row_values: List[str]) -> (List[str], List[str]):
        fields = []
        duplicate_fields = set()
        for cell_value in header_row_values:
            if cell_value:
                if cell_value in fields:
                    duplicate_fields.add(cell_value)
                else:
                    fields.append(cell_value)
            else:
                break

        # Removing all duplicate fields
        if duplicate_fields:
            fields = [field for field in fields if field not in duplicate_fields]

        return fields, list(duplicate_fields)

    @staticmethod
    def get_formatted_row_values(row_data: RowData) -> List[str]:
        """
        Gets the formatted values of all cell data in this row. A formatted value is the final value a user sees in a spreadsheet.
        It can be a raw string input by the user, or the result of a sheets function call.
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
        if not all_row_data:
            # the sheet is empty
            logger.warning(f"The sheet {sheet_name} (ID {spreadsheet_id}) is empty!")
            return []

        if len(all_row_data) != 1:
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
        client, spreadsheet_id: str, requested_sheets_and_columns: Dict[str, FrozenSet[str]], names_conversion: bool = False
    ) -> Dict[str, Dict[int, str]]:
        available_sheets = Helpers.get_sheets_in_spreadsheet(client, spreadsheet_id)
        logger.info(f"Available sheets: {available_sheets}")
        available_sheets_to_column_index_to_name = defaultdict(dict)
        for sheet, columns in requested_sheets_and_columns.items():
            if sheet in available_sheets:
                first_row = Helpers.get_first_row(client, spreadsheet_id, sheet)
                if names_conversion:
                    first_row = [safe_name_conversion(h) for h in first_row]
                    # When performing names conversion, they won't match what is listed in catalog for the majority of cases,
                    # so they should be cast here in order to have them in records
                    columns = {safe_name_conversion(c) for c in columns}
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
        # filter out sheets without gridProperties (like in diagram sheets)
        data_sheets = [sheet for sheet in spreadsheet_metadata.sheets if hasattr(sheet.properties, "gridProperties")]
        return {sheet.properties.title: sheet.properties.gridProperties["rowCount"] for sheet in data_sheets}

    @staticmethod
    def get_grid_sheets(spreadsheet_metadata) -> List[str]:
        """Return grid only diagram, filter out sheets with image/diagram only

        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheets#sheetproperties
        """
        grid_sheets = []
        non_grid_sheets = []
        for sheet in spreadsheet_metadata.sheets:
            sheet_title = sheet.properties.title
            if (
                hasattr(sheet.properties, "gridProperties")
                and hasattr(sheet.properties, "sheetType")
                and sheet.properties.sheetType == "GRID"
            ):
                grid_sheets.append(sheet_title)
            else:
                non_grid_sheets.append(sheet_title)

        if non_grid_sheets:
            # logging.getLogger(...).log() expects an integer level. The level for WARN is 30
            # Reference: https://docs.python.org/3.10/library/logging.html#levels
            logging.getLogger("airbyte").log(30, "Skip non-grid sheets: " + ", ".join(non_grid_sheets))

        return grid_sheets

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

    @staticmethod
    def get_spreadsheet_id(id_or_url: str) -> str:
        if re.match(r"(https://)", id_or_url):
            # This is a URL
            m = re.search(r"(/)([-\w]{20,})([/]?)", id_or_url)
            if m is not None and m.group(2):
                return m.group(2)
        else:
            return id_or_url

    @staticmethod
    def check_sheet_is_valid(client, spreadsheet_id: str, sheet_name: str) -> Tuple[bool, str]:
        try:
            Helpers.get_first_row(client, spreadsheet_id, sheet_name)
            return True, ""
        except Exception as e:
            return False, str(e)
