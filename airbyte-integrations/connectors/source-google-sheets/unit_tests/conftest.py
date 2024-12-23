#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_google_sheets.models import CellData, GridData, RowData, Sheet, SheetProperties, Spreadsheet, SpreadsheetValues, ValueRange

from airbyte_cdk.models.airbyte_protocol import AirbyteStream, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode


@pytest.fixture
def invalid_config():
    return {
        "spreadsheet_id": "invalid_spreadsheet_id",
        "credentials": {
            "auth_type": "Client",
            "client_id": "fake_client_id",
            "client_secret": "fake_client_secret",
            "refresh_token": "fake_refresh_token",
        },
    }


@pytest.fixture
def spreadsheet():
    def maker(spreadsheet_id, sheet_name):
        return Spreadsheet(
            spreadsheetId=spreadsheet_id,
            sheets=[
                Sheet(
                    data=[GridData(rowData=[RowData(values=[CellData(formattedValue="ID")])])],
                    properties=SheetProperties(title=sheet_name, gridProperties={"rowCount": 2}),
                ),
            ],
        )

    return maker


@pytest.fixture
def spreadsheet_values():
    def maker(spreadsheet_id):
        return SpreadsheetValues(spreadsheetId=spreadsheet_id, valueRanges=[ValueRange(values=[["1"]])])

    return maker


@pytest.fixture
def catalog():
    def maker(*name_schema_pairs):
        for name, schema in name_schema_pairs:
            yield ConfiguredAirbyteStream(
                stream=AirbyteStream(name=name, json_schema=schema, supported_sync_modes=["full_refresh"]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            )

    return maker
