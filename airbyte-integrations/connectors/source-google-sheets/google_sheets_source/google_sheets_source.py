#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import socket
from typing import Any, Generator, List, MutableMapping, Union

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources.source import Source
from apiclient import errors
from requests.status_codes import codes as status_codes

from .client import GoogleSheetsClient
from .helpers import Helpers
from .models.spreadsheet import Spreadsheet
from .models.spreadsheet_values import SpreadsheetValues

# set default batch read size
ROW_BATCH_SIZE = 200
# override default socket timeout to be 10 mins instead of 60 sec.
# on behalf of https://github.com/airbytehq/oncall/issues/242
DEFAULT_SOCKET_TIMEOUT: int = 600
socket.setdefaulttimeout(DEFAULT_SOCKET_TIMEOUT)


class GoogleSheetsSource(Source):
    """
    Spreadsheets API Reference: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets
    """

    def __init__(self):
        super().__init__()

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        # Check involves verifying that the specified spreadsheet is reachable with our credentials.
        try:
            client = GoogleSheetsClient(self.get_credentials(config))
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Please use valid credentials json file. Error: {e}")

        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])

        try:
            # Attempt to get first row of sheet
            client.get(spreadsheetId=spreadsheet_id, includeGridData=False, ranges="1:1")
        except errors.HttpError as err:
            reason = str(err)
            # Give a clearer message if it's a common error like 404.
            if err.resp.status == status_codes.NOT_FOUND:
                reason = "Requested spreadsheet was not found."
            logger.error(f"Formatted error: {reason}")
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"Unable to connect with the provided credentials to spreadsheet. Error: {reason}"
            )

        # Check for duplicate headers
        spreadsheet_metadata = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=False))

        grid_sheets = Helpers.get_grid_sheets(spreadsheet_metadata)

        duplicate_headers_in_sheet = {}
        for sheet_name in grid_sheets:
            try:
                header_row_data = Helpers.get_first_row(client, spreadsheet_id, sheet_name)
                _, duplicate_headers = Helpers.get_valid_headers_and_duplicates(header_row_data)
                if duplicate_headers:
                    duplicate_headers_in_sheet[sheet_name] = duplicate_headers
            except Exception as err:
                if str(err).startswith("Expected data for exactly one row for sheet"):
                    logger.warn(f"Skip empty sheet: {sheet_name}")
                else:
                    logger.error(str(err))
                    return AirbyteConnectionStatus(
                        status=Status.FAILED, message=f"Unable to read the schema of sheet {sheet_name}. Error: {str(err)}"
                    )
        if duplicate_headers_in_sheet:
            duplicate_headers_error_message = ", ".join(
                [
                    f"[sheet:{sheet_name}, headers:{duplicate_sheet_headers}]"
                    for sheet_name, duplicate_sheet_headers in duplicate_headers_in_sheet.items()
                ]
            )
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message="The following duplicate headers were found in the following sheets. Please fix them to continue: "
                + duplicate_headers_error_message,
            )

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        client = GoogleSheetsClient(self.get_credentials(config))
        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])
        try:
            logger.info(f"Running discovery on sheet {spreadsheet_id}")
            spreadsheet_metadata = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=False))
            grid_sheets = Helpers.get_grid_sheets(spreadsheet_metadata)
            streams = []
            for sheet_name in grid_sheets:
                try:
                    header_row_data = Helpers.get_first_row(client, spreadsheet_id, sheet_name)
                    stream = Helpers.headers_to_airbyte_stream(logger, sheet_name, header_row_data)
                    streams.append(stream)
                except Exception as err:
                    if str(err).startswith("Expected data for exactly one row for sheet"):
                        logger.warn(f"Skip empty sheet: {sheet_name}")
                    else:
                        logger.error(str(err))
            return AirbyteCatalog(streams=streams)

        except errors.HttpError as err:
            reason = str(err)
            if err.resp.status == status_codes.NOT_FOUND:
                reason = "Requested spreadsheet was not found."
            raise Exception(f"Could not run discovery: {reason}")

    def read(
        self,
        logger: AirbyteLogger,
        config: json,
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Generator[AirbyteMessage, None, None]:
        client = GoogleSheetsClient(self.get_credentials(config))

        sheet_to_column_name = Helpers.parse_sheet_and_column_names_from_catalog(catalog)
        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])

        row_batch_size = config.get("row_batch_size", ROW_BATCH_SIZE)
        logger.info(f"Starting syncing spreadsheet {spreadsheet_id}")
        # For each sheet in the spreadsheet, get a batch of rows, and as long as there hasn't been
        # a blank row, emit the row batch
        sheet_to_column_index_to_name = Helpers.get_available_sheets_to_column_index_to_name(client, spreadsheet_id, sheet_to_column_name)
        sheet_row_counts = Helpers.get_sheet_row_count(client, spreadsheet_id)
        logger.info(f"Row counts: {sheet_row_counts}")
        for sheet in sheet_to_column_index_to_name.keys():
            logger.info(f"Syncing sheet {sheet}")
            column_index_to_name = sheet_to_column_index_to_name[sheet]
            row_cursor = 2  # we start syncing past the header row
            # For the loop, it is necessary that the initial row exists when we send a request to the API,
            # if the last row of the interval goes outside the sheet - this is normal, we will return
            # only the real data of the sheet and in the next iteration we will loop out.
            while row_cursor <= sheet_row_counts[sheet]:
                range = f"{sheet}!{row_cursor}:{row_cursor + row_batch_size}"
                logger.info(f"Fetching range {range}")
                row_batch = SpreadsheetValues.parse_obj(
                    client.get_values(spreadsheetId=spreadsheet_id, ranges=range, majorDimension="ROWS")
                )

                row_cursor += row_batch_size + 1
                # there should always be one range since we requested only one
                value_ranges = row_batch.valueRanges[0]

                if not value_ranges.values:
                    break

                row_values = value_ranges.values
                if len(row_values) == 0:
                    break

                for row in row_values:
                    if not Helpers.is_row_empty(row) and Helpers.row_contains_relevant_data(row, column_index_to_name.keys()):
                        yield AirbyteMessage(type=Type.RECORD, record=Helpers.row_data_to_record_message(sheet, row, column_index_to_name))
        logger.info(f"Finished syncing spreadsheet {spreadsheet_id}")

    @staticmethod
    def get_credentials(config):
        # backward compatible with old style config
        if config.get("credentials_json"):
            credentials = {"auth_type": "Service", "service_account_info": config.get("credentials_json")}
            return credentials

        return config.get("credentials")
