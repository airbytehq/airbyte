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

import json
from typing import Dict, Generator

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from apiclient import errors
from base_python import AirbyteLogger, Source
from requests.status_codes import codes as status_codes

from .client import GoogleSheetsClient
from .helpers import Helpers
from .models.spreadsheet import Spreadsheet
from .models.spreadsheet_values import SpreadsheetValues

ROW_BATCH_SIZE = 200


class GoogleSheetsSource(Source):
    """
    Spreadsheets API Reference: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets
    """

    def __init__(self):
        super().__init__()

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        # Check involves verifying that the specified spreadsheet is reachable with our credentials.
        client = GoogleSheetsClient(json.loads(config["credentials_json"]))
        spreadsheet_id = config["spreadsheet_id"]
        try:
            # Attempt to get first row of sheet
            client.get(spreadsheetId=spreadsheet_id, includeGridData=False, ranges="1:1")
        except errors.HttpError as err:
            reason = str(err)
            # Give a clearer message if it's a common error like 404.
            if err.resp.status == status_codes.NOT_FOUND:
                reason = "Requested spreadsheet was not found."
            logger.error(f"Formatted error: {reason}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=str(reason))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        client = GoogleSheetsClient(json.loads(config["credentials_json"]))
        spreadsheet_id = config["spreadsheet_id"]
        try:
            logger.info(f"Running discovery on sheet {spreadsheet_id}")
            spreadsheet_metadata = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=False))
            sheet_names = [sheet.properties.title for sheet in spreadsheet_metadata.sheets]
            streams = []
            for sheet_name in sheet_names:
                header_row_data = Helpers.get_first_row(client, spreadsheet_id, sheet_name)
                stream = Helpers.headers_to_airbyte_stream(sheet_name, header_row_data)
                streams.append(stream)
            return AirbyteCatalog(streams=streams)

        except errors.HttpError as err:
            reason = str(err)
            if err.resp.status == status_codes.NOT_FOUND:
                reason = "Requested spreadsheet was not found."
            raise Exception(f"Could not run discovery: {reason}")

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        client = GoogleSheetsClient(json.loads(config["credentials_json"]))

        sheet_to_column_name = Helpers.parse_sheet_and_column_names_from_catalog(catalog)
        spreadsheet_id = config["spreadsheet_id"]

        logger.info(f"Starting syncing spreadsheet {spreadsheet_id}")
        # For each sheet in the spreadsheet, get a batch of rows, and as long as there hasn't been
        # a blank row, emit the row batch
        sheet_to_column_index_to_name = Helpers.get_available_sheets_to_column_index_to_name(client, spreadsheet_id, sheet_to_column_name)
        for sheet in sheet_to_column_index_to_name.keys():
            logger.info(f"Syncing sheet {sheet}")
            column_index_to_name = sheet_to_column_index_to_name[sheet]
            row_cursor = 2  # we start syncing past the header row
            encountered_blank_row = False
            while not encountered_blank_row:
                range = f"{sheet}!{row_cursor}:{row_cursor + ROW_BATCH_SIZE}"
                logger.info(f"Fetching range {range}")
                row_batch = SpreadsheetValues.parse_obj(
                    client.get_values(spreadsheetId=spreadsheet_id, ranges=range, majorDimension="ROWS")
                )
                row_cursor += ROW_BATCH_SIZE + 1
                # there should always be one range since we requested only one
                value_ranges = row_batch.valueRanges[0]

                if not value_ranges.values:
                    break

                row_values = value_ranges.values
                if len(row_values) == 0:
                    break

                for row in row_values:
                    if Helpers.is_row_empty(row):
                        encountered_blank_row = True
                        break
                    elif Helpers.row_contains_relevant_data(row, column_index_to_name.keys()):
                        yield AirbyteMessage(type=Type.RECORD, record=Helpers.row_data_to_record_message(sheet, row, column_index_to_name))
        logger.info(f"Finished syncing spreadsheet {spreadsheet_id}")
