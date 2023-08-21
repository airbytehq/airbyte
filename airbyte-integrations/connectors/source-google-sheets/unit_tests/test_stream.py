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
from google.auth import exceptions as google_exceptions
from source_google_sheets import SourceGoogleSheets
from source_google_sheets.client import GoogleSheetsClient
from source_google_sheets.helpers import SCOPES, Helpers
from source_google_sheets.models import CellData, GridData, RowData, Sheet, SheetProperties, Spreadsheet


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
    expected_message = ("The requested Google Sheets spreadsheet with id invalid_spreadsheet_id does not exist."
                        " Please ensure the Spreadsheet Link you have set is valid and Spreadsheet exists. If the issue persists, contact support. Requested entity was not found.")
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
    expected_message = ("The authenticated Google Sheets user does not have permissions to view the "
                        "spreadsheet with id invalid_spreadsheet_id. Please ensure the authenticated user has access"
                        " to the Spreadsheet and reauthenticate. If the issue persists, contact support. "
                        "The caller does not have right permissions.")
    assert e.value.args[0] == expected_message


def test_check_invalid_creds_json_file(invalid_config):
    source = SourceGoogleSheets()
    res = source.check(logger=None, config={""})
    assert 'Please use valid credentials json file' in res.message


def test_check_access_expired(mocker, invalid_config):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 403
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=google_exceptions.GoogleAuthError(resp=resp, content=b''))
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    expected_message = 'Access to the spreadsheet expired or was revoked. Re-authenticate to restore access.'
    assert e.value.args[0] == expected_message


def test_check_status_succeeded(mocker, invalid_config):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    expected_sheets = ["1", "2", "3", "4"]
    mocker.patch.object(GoogleSheetsClient, "get", return_value=Spreadsheet(
            spreadsheetId='spreadsheet_id', sheets=[Sheet(properties=SheetProperties(title=t)) for t in expected_sheets]
        ))

    res = source.check(logger=None, config=invalid_config)
    assert str(res.status) == "Status.SUCCEEDED"


def test_discover_with_non_grid_sheets(mocker, invalid_config):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    expected_sheets = ["1", "2", "3", "4"]
    mocker.patch.object(GoogleSheetsClient, "get", return_value=Spreadsheet(
        spreadsheetId='spreadsheet_id', sheets=[Sheet(properties=SheetProperties(title=t)) for t in expected_sheets]
    ))
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert res.streams == []


def test_discover(mocker, invalid_config):
    sheet1_first_row = ["1", "2", "3", "4"]
    data = [
        GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in sheet1_first_row])
                          ])]
    sheet = Sheet(properties=SheetProperties(title='sheet1', gridProperties='true', sheetType="GRID"), data=data)

    spreadsheet = Spreadsheet(spreadsheetId='spreadsheet_id', sheets=[sheet])
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert len(res.streams) == 1


def test_discover_incorrect_spreadsheet_name(mocker, invalid_config):
    sheet1_first_row = ["1", "2", "3", "4"]
    data = [
        GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in sheet1_first_row])
                          ])]
    sheet = Sheet(properties=SheetProperties(title='sheet1 test test', gridProperties='true', sheetType="GRID"), data=data)

    spreadsheet = Spreadsheet(spreadsheetId='spreadsheet_id', sheets=[sheet])
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert len(res.streams) == 1


def test_discover_could_not_run_discover(mocker, invalid_config):
    source = SourceGoogleSheets()
    resp = requests.Response()
    resp.status = 500
    resp.reason = "Interval Server error"
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=errors.HttpError(resp=resp, content=b''))

    with pytest.raises(Exception) as e:
        source.discover(logger=mocker.MagicMock(), config=invalid_config)
    expected_message = ("Could not discover the schema of your spreadsheet. There was an issue with the Google Sheets API."
                        " This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support. Interval Server error.")
    assert e.value.args[0] == expected_message


def test_get_credentials(invalid_config):
    expected_config = {
        'auth_type': 'Client', 'client_id': 'fake_client_id',
        'client_secret': 'fake_client_secret', 'refresh_token': 'fake_refresh_token'
    }
    assert expected_config == SourceGoogleSheets.get_credentials(invalid_config)


def test_get_credentials_old_style():
    old_style_config = {
        "credentials_json": "some old style data"
    }
    expected_config = {'auth_type': 'Service', 'service_account_info': 'some old style data'}
    assert expected_config == SourceGoogleSheets.get_credentials(old_style_config)


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
    assert "Request a higher quota limit" in caplog.text
