#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    SyncMode,
)
from airbyte_cdk.utils import AirbyteTracedException
from apiclient import errors
from source_google_sheets import SourceGoogleSheets
from source_google_sheets.client import GoogleSheetsClient
from source_google_sheets.helpers import SCOPES, Helpers


def test_invalid_credentials_error_message(invalid_config):
    source = SourceGoogleSheets()
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    assert e.value.args[0] == 'Access to the spreadsheet expired or was revoked. Re-authenticate to restore access.'


def test_invalid_link_error_message(mocker, invalid_config):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 404
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=errors.HttpError(resp=resp, content=b''))
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    expected_message = 'Config error: The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync.'
    assert e.value.args[0] == expected_message


def test_discover_404_error(mocker, invalid_config):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 404
    resp.reason = "Requested entity was not found"
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=errors.HttpError(resp=resp, content=b''))

    with pytest.raises(AirbyteTracedException) as e:
        source.discover(logger=mocker.MagicMock(), config=invalid_config)
    expected_message = ("Requested spreadsheet with id invalid_spreadsheet_id was not found. Requested entity was not found. "
                        "See docs for more details here: https://cloud.google.com/service-infrastructure/docs/service-control/reference/rpc/google.api/servicecontrol.v1#code")
    assert e.value.args[0] == expected_message


def test_discover_403_error(mocker, invalid_config):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 403
    resp.reason = "The caller does not have right permissions"
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=errors.HttpError(resp=resp, content=b''))

    with pytest.raises(AirbyteTracedException) as e:
        source.discover(logger=mocker.MagicMock(), config=invalid_config)
    expected_message = ("Forbidden when requesting spreadsheet with id invalid_spreadsheet_id. The caller does not have right permissions. "
                        "See docs for more details here: https://cloud.google.com/service-infrastructure/docs/service-control/reference/rpc/google.api/servicecontrol.v1#code")
    assert e.value.args[0] == expected_message


def test_read_429_error(mocker, invalid_config, caplog):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 429
    resp.reason = "Request a higher quota limit"
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=mocker.Mock)
    mocker.patch.object(Helpers, "get_sheets_in_spreadsheet", side_effect=errors.HttpError(resp=resp, content=b''))

    sheet1 = "soccer_team"
    sheet1_columns = frozenset(["arsenal", "chelsea", "manutd", "liverpool"])
    sheet1_schema = {"properties": {c: {"type": "string"} for c in sheet1_columns}}
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=sheet1, json_schema=sheet1_schema, supported_sync_modes=["full_refresh"]),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.overwrite,
            ),
        ]
    )
    records = list(source.read(logger=logging.getLogger("airbyte"), config=invalid_config, catalog=catalog))
    assert [] == records
    assert "Stopped syncing process due to rate limits. Request a higher quota limit" in caplog.text
