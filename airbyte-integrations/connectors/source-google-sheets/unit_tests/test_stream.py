#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests
from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob, AirbyteStreamStatus, ConfiguredAirbyteCatalog
from airbyte_cdk.utils import AirbyteTracedException
from apiclient import errors
from source_google_sheets import SourceGoogleSheets
from source_google_sheets.client import GoogleSheetsClient
from source_google_sheets.helpers import SCOPES, Helpers
from source_google_sheets.models import CellData, GridData, RowData, Sheet, SheetProperties, Spreadsheet


def set_http_error_for_google_sheets_client(mocker, resp):
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", side_effect=errors.HttpError(resp=resp, content=b""))


def set_resp_http_error(status_code, error_message=None):
    resp = requests.Response()
    resp.status = status_code
    if error_message:
        resp.reason = error_message
    return resp


def set_sheets_type_grid(sheet_first_row):
    data = [GridData(rowData=[RowData(values=[CellData(formattedValue=v) for v in sheet_first_row])])]
    sheet = Sheet(properties=SheetProperties(title="sheet1", gridProperties="true", sheetType="GRID"), data=data)
    return sheet


def test_invalid_credentials_error_message(invalid_config):
    source = SourceGoogleSheets()
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    assert e.value.args[0] == "Access to the spreadsheet expired or was revoked. Re-authenticate to restore access."


def test_invalid_link_error_message(mocker, invalid_config):
    source = SourceGoogleSheets()
    set_http_error_for_google_sheets_client(mocker, set_resp_http_error(404))
    with pytest.raises(AirbyteTracedException) as e:
        source.check(logger=None, config=invalid_config)
    expected_message = "Config error: The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync."
    assert e.value.args[0] == expected_message


def test_discover_404_error(mocker, invalid_config):
    source = SourceGoogleSheets()
    set_http_error_for_google_sheets_client(mocker, set_resp_http_error(404, "Requested entity was not found"))

    with pytest.raises(AirbyteTracedException) as e:
        source.discover(logger=mocker.MagicMock(), config=invalid_config)
    expected_message = (
        "The requested Google Sheets spreadsheet with id invalid_spreadsheet_id does not exist."
        " Please ensure the Spreadsheet Link you have set is valid and the spreadsheet exists. If the issue persists, contact support. Requested entity was not found."
    )
    assert e.value.args[0] == expected_message


def test_discover_403_error(mocker, invalid_config):
    source = SourceGoogleSheets()
    set_http_error_for_google_sheets_client(mocker, set_resp_http_error(403, "The caller does not have right permissions"))

    with pytest.raises(AirbyteTracedException) as e:
        source.discover(logger=mocker.MagicMock(), config=invalid_config)
    expected_message = (
        "The authenticated Google Sheets user does not have permissions to view the "
        "spreadsheet with id invalid_spreadsheet_id. Please ensure the authenticated user has access"
        " to the Spreadsheet and reauthenticate. If the issue persists, contact support. "
        "The caller does not have right permissions."
    )
    assert e.value.args[0] == expected_message


def test_check_invalid_creds_json_file(invalid_config):
    source = SourceGoogleSheets()
    res = source.check(logger=None, config={""})
    assert "Please use valid credentials json file" in res.message


def test_check_access_expired(mocker, invalid_config):
    source = SourceGoogleSheets()
    set_http_error_for_google_sheets_client(mocker, set_resp_http_error(403))
    expected_message = "Access to the spreadsheet expired or was revoked. Re-authenticate to restore access."
    with pytest.raises(AirbyteTracedException):
        res = source.check(logger=None, config=invalid_config)
        assert res.message == expected_message


def test_check_expected_to_read_data_from_1_sheet(mocker, invalid_config, caplog):
    spreadsheet = Spreadsheet(spreadsheetId="spreadsheet_id", sheets=[set_sheets_type_grid(["1", "2"]), set_sheets_type_grid(["3", "4"])])
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.check(logger=logging.getLogger("airbyte"), config=invalid_config)
    assert str(res.status) == "Status.FAILED"
    assert "Unexpected return result: Sheet sheet1 was expected to contain data on exactly 1 sheet." in caplog.text


def test_check_duplicated_headers(invalid_config, mocker, caplog):
    spreadsheet = Spreadsheet(spreadsheetId="spreadsheet_id", sheets=[set_sheets_type_grid(["1", "1", "3", "4"])])
    source = SourceGoogleSheets()
    expected_message = (
        "The following duplicate headers were found in the following sheets. Please fix them to continue: [sheet:sheet1, headers:['1']]"
    )
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.check(logger=logging.getLogger("airbyte"), config=invalid_config)
    assert str(res.status) == "Status.FAILED"
    assert expected_message in res.message


def test_check_status_succeeded(mocker, invalid_config):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(
        GoogleSheetsClient,
        "get",
        return_value=Spreadsheet(
            spreadsheetId="spreadsheet_id", sheets=[Sheet(properties=SheetProperties(title=t)) for t in ["1", "2", "3", "4"]]
        ),
    )

    res = source.check(logger=None, config=invalid_config)
    assert str(res.status) == "Status.SUCCEEDED"


def test_discover_with_non_grid_sheets(mocker, invalid_config):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(
        GoogleSheetsClient,
        "get",
        return_value=Spreadsheet(
            spreadsheetId="spreadsheet_id", sheets=[Sheet(properties=SheetProperties(title=t)) for t in ["1", "2", "3", "4"]]
        ),
    )
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert res.streams == []


def test_discover(mocker, invalid_config):
    source = SourceGoogleSheets()
    spreadsheet = Spreadsheet(spreadsheetId="spreadsheet_id", sheets=[set_sheets_type_grid(["1", "2", "3", "4"])])
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert len(res.streams) == 1


def test_discover_with_names_conversion(mocker, invalid_config):
    invalid_config["names_conversion"] = True
    spreadsheet = Spreadsheet(spreadsheetId="spreadsheet_id", sheets=[set_sheets_type_grid(["1 тест", "2", "3", "4"])])
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert len(res.streams) == 1
    assert "_1_test" in res.streams[0].json_schema["properties"].keys()


def test_discover_incorrect_spreadsheet_name(mocker, invalid_config):
    spreadsheet = Spreadsheet(spreadsheetId="spreadsheet_id", sheets=[set_sheets_type_grid(["1", "2", "3", "4"])])
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet)
    res = source.discover(logger=mocker.MagicMock(), config=invalid_config)
    assert len(res.streams) == 1


def test_discover_could_not_run_discover(mocker, invalid_config):
    source = SourceGoogleSheets()
    set_http_error_for_google_sheets_client(mocker, set_resp_http_error(500, "Interval Server error"))

    with pytest.raises(Exception) as e:
        source.discover(logger=mocker.MagicMock(), config=invalid_config)
    expected_message = (
        "Could not discover the schema of your spreadsheet. There was an issue with the Google Sheets API."
        " This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support. Interval Server error."
    )
    assert e.value.args[0] == expected_message


def test_get_credentials(invalid_config):
    expected_config = {
        "auth_type": "Client",
        "client_id": "fake_client_id",
        "client_secret": "fake_client_secret",
        "refresh_token": "fake_refresh_token",
    }
    assert expected_config == SourceGoogleSheets.get_credentials(invalid_config)


def test_get_credentials_old_style():
    old_style_config = {"credentials_json": "some old style data"}
    expected_config = {"auth_type": "Service", "service_account_info": "some old style data"}
    assert expected_config == SourceGoogleSheets.get_credentials(old_style_config)


def test_read_429_error(mocker, invalid_config, catalog, caplog):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=mocker.Mock)
    mocker.patch.object(
        Helpers,
        "get_sheets_in_spreadsheet",
        side_effect=errors.HttpError(resp=set_resp_http_error(429, "Request a higher quota limit"), content=b""),
    )

    sheet1 = "soccer_team"
    sheet1_columns = frozenset(["arsenal", "chelsea", "manutd", "liverpool"])
    sheet1_schema = {"properties": {c: {"type": "string"} for c in sheet1_columns}}
    catalog = ConfiguredAirbyteCatalog(streams=catalog((sheet1, sheet1_schema),))
    records = list(source.read(logger=logging.getLogger("airbyte"), config=invalid_config, catalog=catalog))
    assert [] == records
    assert (
        "Stopped syncing process due to rate limits. Rate limit has been reached. Please try later or request a higher quota for your account"
        in caplog.text
    )


def test_read_403_error(mocker, invalid_config, catalog, caplog):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    mocker.patch.object(GoogleSheetsClient, "get", return_value=mocker.Mock)
    mocker.patch.object(
        Helpers, "get_sheets_in_spreadsheet", side_effect=errors.HttpError(resp=set_resp_http_error(403, "Permission denied"), content=b"")
    )

    sheet1 = "soccer_team"
    sheet1_columns = frozenset(["arsenal", "chelsea", "manutd", "liverpool"])
    sheet1_schema = {"properties": {c: {"type": "string"} for c in sheet1_columns}}
    catalog = ConfiguredAirbyteCatalog(streams=catalog((sheet1, sheet1_schema),))
    with pytest.raises(AirbyteTracedException) as e:
        next(source.read(logger=logging.getLogger("airbyte"), config=invalid_config, catalog=catalog))
    assert (
        str(e.value)
        == "The authenticated Google Sheets user does not have permissions to view the spreadsheet with id invalid_spreadsheet_id. Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. If the issue persists, contact support"
    )


def test_read_expected_data_on_1_sheet(invalid_config, mocker, catalog, caplog):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    sheet1 = "soccer_team"
    sheet2 = "soccer_team2"
    mocker.patch.object(
        GoogleSheetsClient,
        "get",
        return_value=Spreadsheet(
            spreadsheetId="spreadsheet_id", sheets=[Sheet(properties=SheetProperties(title=t)) for t in [sheet1, sheet2]]
        ),
    )

    sheet1_columns = frozenset(["arsenal", "chelsea", "manutd", "liverpool"])
    sheet1_schema = {"properties": {c: {"type": "string"} for c in sheet1_columns}}
    catalog = ConfiguredAirbyteCatalog(streams=catalog((sheet1, sheet1_schema), (sheet2, sheet1_schema)))

    with pytest.raises(Exception) as e:
        next(source.read(logger=logging.getLogger("airbyte"), config=invalid_config, catalog=catalog))
    assert "Unexpected return result: Sheet soccer_team was expected to contain data on exactly 1 sheet." in str(e.value)


def test_read_empty_sheet(invalid_config, mocker, catalog, caplog):
    source = SourceGoogleSheets()
    mocker.patch.object(GoogleSheetsClient, "__init__", lambda s, credentials, scopes=SCOPES: None)
    sheet1 = "soccer_team"
    sheet2 = "soccer_team2"
    sheets = [
                 Sheet(properties=SheetProperties(title=t), data=[{"test1": "12", "test2": "123"},])
                 for t in [sheet1]
    ]
    mocker.patch.object(
        GoogleSheetsClient,
        "get",
        return_value=Spreadsheet(spreadsheetId=invalid_config["spreadsheet_id"], sheets=sheets),
    )

    sheet1_columns = frozenset(["arsenal", "chelsea"])
    sheet1_schema = {"properties": {c: {"type": "string"} for c in sheet1_columns}}
    catalog = ConfiguredAirbyteCatalog(streams=catalog((sheet1, sheet1_schema), (sheet2, sheet1_schema)))
    records = list(source.read(logger=logging.getLogger("airbyte"), catalog=catalog, config=invalid_config))
    assert records == []
    assert "The sheet soccer_team (ID invalid_spreadsheet_id) is empty!" in caplog.text


def test_when_read_then_status_messages_emitted(mocker, spreadsheet, spreadsheet_values, catalog, invalid_config):
    source = SourceGoogleSheets()
    spreadsheet_id = "invalid_spreadsheet_id"
    sheet_name = "sheet_1"
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet(spreadsheet_id, sheet_name))
    mocker.patch.object(GoogleSheetsClient, "get_values", return_value=spreadsheet_values(spreadsheet_id))

    sheet_schema = {"properties": {"ID": {"type": "string"}}}
    catalog = ConfiguredAirbyteCatalog(streams=catalog((sheet_name, sheet_schema),))
    records = list(source.read(logger=logging.getLogger("airbyte"), config=invalid_config, catalog=catalog))

    # stream started, stream running, 1 record, stream state, stream completed
    assert len(records) == 5
    assert records[0].trace.stream_status.status == AirbyteStreamStatus.STARTED
    assert records[1].trace.stream_status.status == AirbyteStreamStatus.RUNNING
    assert records[4].trace.stream_status.status == AirbyteStreamStatus.COMPLETE


def test_when_read_then_state_message_emitted(mocker, spreadsheet, spreadsheet_values, catalog, invalid_config):
    source = SourceGoogleSheets()
    spreadsheet_id = "invalid_spreadsheet_id"
    sheet_name = "sheet_1"
    mocker.patch.object(GoogleSheetsClient, "get", return_value=spreadsheet(spreadsheet_id, sheet_name))
    mocker.patch.object(GoogleSheetsClient, "get_values", return_value=spreadsheet_values(spreadsheet_id))

    sheet_schema = {"properties": {"ID": {"type": "string"}}}
    catalog = ConfiguredAirbyteCatalog(streams=catalog((sheet_name, sheet_schema),))
    records = list(source.read(logger=logging.getLogger("airbyte"), config=invalid_config, catalog=catalog))

    # stream started, stream running, 1 record, stream state, stream completed
    assert len(records) == 5
    assert records[3].state.stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)
    assert records[3].state.stream.stream_descriptor.name == "sheet_1"
