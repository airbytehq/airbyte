import httplib2
import os
import json

from airbyte_protocol import Source
from airbyte_protocol import AirbyteSpec
from airbyte_protocol import AirbyteCheckResponse
from airbyte_protocol import AirbyteCatalog
from airbyte_protocol import AirbyteStream
from airbyte_protocol import AirbyteMessage
from typing import Generator
from apiclient import discovery, errors
from google.oauth2 import service_account

WORKSPACE_ROOT = "/airbyte/google_sheets_source"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']


# TODO add a JSONSchema type which denotes the API's return values
'''
  Spreadsheets API Reference: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/sheet
'''
class GoogleSheetsSource(Source):
    def __init__(self):
        pass

    def _get_authenticated_sheets_service(self, config) -> discovery.Resource:
        creds_json = json.loads(config['credentials_json'])
        credentials = service_account.Credentials.from_service_account_info(creds_json, scopes=SCOPES)
        return discovery.build('sheets', 'v4', credentials=credentials)

    def spec(self) -> AirbyteSpec:
        with open(f"{WORKSPACE_ROOT}/spec.json") as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    def check(self, logger, config_container) -> AirbyteCheckResponse:
        # Check involves verifying that the specified spreadsheet is reachable with our credentials.
        config = config_container.rendered_config
        service = self._get_authenticated_sheets_service(config)
        spreadsheet_id = config['spreadsheet_id']
        try:
            # Attempt to get first row of sheet
            service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False, range='1:1').execute()
        except errors.HttpError as err:
            reason = str(err)
            # Give a clearer message if it's a common error like 404.
            if err.resp.status == 404:
                reason = "Requested spreadsheet was not found."

            print(f"Formatted error: {reason}")
            return AirbyteCheckResponse(False, {"reason": str(reason)})

        return AirbyteCheckResponse(True, {})

    # Parses the cell values in the provided row. This method assumes that the input row is "full"
    # i.e: every cell contains a value and the first cell which does not contain a value denotes the end
    # of the headers. For example, if the first row contains "One | Two | | Three" then this method
    # will parse the headers as ["one", "two"]. This assumption is made for simplicity and can be modified later.
    def _parse_headers_to_stream(self, sheet_name, row) -> AirbyteStream:
        fields = []
        string_schema = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "string"}
        for value in row['values']:
            formatted_value = value.get('formattedValue')
            if formatted_value:
                # For simplicity, everything is considered to be a string
                fields.append(formatted_value)
            else:
                break

        schema = {field: string_schema for field in fields}
        return AirbyteStream(name=sheet_name, schema=schema)

    def discover(self, logger, config_container) -> AirbyteCatalog:
        config = config_container.rendered_config
        service = self._get_authenticated_sheets_service(config)
        spreadsheet_id = config['spreadsheet_id']
        try:
            spreadsheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=False).execute()
            sheets = [sheet['properties']['title'] for sheet in spreadsheet_metadata['sheets']]
            streams = []
            for sheet in sheets:
                first_row = service.spreadsheets().get(spreadsheetId=spreadsheet_id, includeGridData=True, ranges=f'{sheet}!1:1').execute()
                # There is only one sheet since we are specifying the sheet in the requested ranges.
                sheet_object = first_row['sheets']
                if len(sheet_object) != 1:
                    raise Exception(f"Unexpected return result: Sheet {sheet} was expected to contain data on exactly 1 sheet. ")
                range_data = sheet_object[0]['data']

                if len(range_data) != 1:
                    raise Exception(f"Expected data for exactly one range for sheet {sheet}")

                all_row_data = range_data[0]['rowData']

                if len(all_row_data) != 1:
                    raise Exception(f"Expected data for exactly one row for sheet {sheet}")

                row_data = all_row_data[0]

                stream = self._parse_headers_to_stream(sheet, row_data)
                streams.append(stream)

            return AirbyteCatalog(streams=streams)
        except errors.HttpError as err:
            reason = str(err)
            # Give a clearer message if it's a common error like 404.
            if err.resp.status == 404:
                reason = "Requested spreadsheet was not found."
            raise Exception(f"Could not run discovery: {reason}")

    def read(self, logger, config_container, catalog_path, state=None) -> Generator[AirbyteMessage, None, None]:
        # masked_airbyte_catalog = self.read_config(catalog_path)
        # discovered_singer_catalog = SingerHelper.get_catalogs(logger, f"tap-stripe --config {config_container.rendered_config_path} --discover").singer_catalog
        # selected_singer_catalog = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, discovered_singer_catalog)
        #
        # config_option = f"--config {config_container.rendered_config_path}"
        # catalog_option = f"--catalog {selected_singer_catalog}"
        # state_option = f"--state {state}" if state else ""
        raise Exception("Not Implemented")
        # return SingerHelper.read(logger, f"tap-stripe {config_option} {catalog_option} {state_option}")
