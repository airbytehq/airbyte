# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import json
from copy import deepcopy
from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import ANY, patch

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStream,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    FailureType,
    Level,
    Status,
    StreamDescriptor,
    SyncMode,
    TraceType,
    Type,
)
from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob, AirbyteStreamStatus
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from source_google_sheets import SourceGoogleSheets

from .entrypoint_wrapper_helper import check
from .request_builder import AuthBuilder, RequestBuilder
from .test_credentials import AUTH_BODY, oauth_credentials, service_account_credentials, service_account_info

_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"
_B_STREAM_NAME = "b_stream_name"
_C_STREAM_NAME = "c_stream_name"


_CONFIG = {
    "spreadsheet_id": _SPREADSHEET_ID,
    "credentials": oauth_credentials,
    "batch_size": 200
}

_SERVICE_CONFIG = {
    "spreadsheet_id": _SPREADSHEET_ID,
    "credentials": service_account_credentials
}


def _catalog(sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()

def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[Dict[str, Any]]) -> SourceGoogleSheets:
    return SourceGoogleSheets(catalog=catalog, config=config, state=state)

def _check(config: Dict[str, Any], expecting_exception: bool = False)-> EntrypointOutput:
    sync_mode = SyncMode.full_refresh
    catalog = _catalog(sync_mode)
    source = _source(catalog=catalog, config=config, state={})
    return check(source, config, expecting_exception)

def _discover(config: Dict[str, Any], expecting_exception: bool = False)-> EntrypointOutput:
    sync_mode = SyncMode.full_refresh
    catalog = _catalog(sync_mode)
    source = _source(catalog=catalog, config=config, state={})
    return discover(source, config, expecting_exception)

def _read(
    config: Dict[str, Any],
    catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:

    source = _source(catalog=catalog, config=config, state={})
    return read(source, config, catalog, state, expecting_exception)

class GoogleSheetSourceTest(TestCase):
    def setUp(self) -> None:
        self._config = deepcopy(_CONFIG)
        self._service_config = deepcopy(_SERVICE_CONFIG)

    @staticmethod
    def _check(config: Dict[str, Any], expecting_exception: bool = True) -> EntrypointOutput:
        return _check(config, expecting_exception=expecting_exception)

    @staticmethod
    def _discover(config: Dict[str, Any], expecting_exception: bool = True) -> EntrypointOutput:
        return _discover(config, expecting_exception=expecting_exception)

    @staticmethod
    def _read(config: Dict[str, Any], catalog: ConfiguredAirbyteCatalog, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, catalog, expecting_exception=expecting_exception)

    @staticmethod
    def authorize(http_mocker: HttpMocker):
        # Authorization request with user credentials to "https://oauth2.googleapis.com" to obtain a token
        http_mocker.post(
            AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200)
        )

    @staticmethod
    def get_spreadsheet_info_and_sheets(http_mocker: HttpMocker, streams_response_file: Optional[str]=None, meta_response_code: Optional[int]=200):
        """"
        Mock request to https://sheets.googleapis.com/v4/spreadsheets/<spreed_sheet_id>?includeGridData=false&alt=json in order
        to obtain sheets (streams) from the spreed_sheet_id provided.
        e.g. from response file
          "sheets": [
            {
              "properties": {
                "sheetId": 0,
                "title": "<sheet_id>",
                "index": 0,
                "sheetType": "GRID",
                "gridProperties": {
                  "rowCount": 1,
                  "columnCount": 1
                }
              }
            }
          ],
        """
        GoogleSheetSourceTest.authorize(http_mocker)
        if streams_response_file:
            http_mocker.get(
                RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
                HttpResponse(json.dumps(find_template(streams_response_file, __file__)), meta_response_code)
            )

    @staticmethod
    def get_sheet_first_row(http_mocker: HttpMocker, headers_response_file: str, headers_response_code: int=200, stream_name: Optional[str]=_STREAM_NAME, data_initial_range_response_file: Optional[str]=None, data_initial_response_code: Optional[int]=200):
        """"
        Mock request to 'https://sheets.googleapis.com/v4/spreadsheets/<spreadsheet>?includeGridData=true&ranges=<sheet>!1:1&alt=json'
        to obtain headers data (keys) used for stream schema from the spreadsheet + sheet provided.
        For this we use range of first row in query.
        e.g. from response file
        "sheets": [
            {
              "properties": {
                "sheetId": 0,
                "title": <sheet_id>,
                "index": 0,
                "sheetType": "GRID",
                "gridProperties": {
                  "rowCount": 4,
                  "columnCount": 2
                }
              },
              "data": [
                {
                  "rowData": [
                    {
                      "values": [
                        {
                          "userEnteredValue": {
                            "stringValue": "name"
                          },
                          "effectiveValue": {
                            "stringValue": "name"
                          },
                          "formattedValue": "name"
                        },
                        {
                          "userEnteredValue": {
                            "stringValue": "age"
                          },
                          "effectiveValue": {
                            "stringValue": "age"
                          },
                          "formattedValue": "age"
                        }
                      ]}],}]}]
        """
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(f"{stream_name}!1:1").with_alt("json").build(),
            HttpResponse(json.dumps(find_template(headers_response_file, __file__)), headers_response_code)
        )

    @staticmethod
    def get_stream_data(http_mocker: HttpMocker, range_data_response_file: str, range_response_code: int=200, stream_name:Optional[str]=_STREAM_NAME):
        """"
        Mock requests to 'https://sheets.googleapis.com/v4/spreadsheets/<spreadsheet>/values:batchGet?ranges=<sheet>!2:202&majorDimension=ROWS&alt=json'
        to obtain value ranges (data) for stream from the spreadsheet + sheet provided.
        For this we use range [2:202(2 + range in config which default is 200)].
        We start at 2 as we consider row 1 to contain headers. If we had more data the routine would continue to next ranges.
        e.g. from response file
        {
          "spreadsheetId": "<spreadsheet_id>",
          "valueRanges": [
            {
              "range": "<sheet_id>!A2:B4",
              "majorDimension": "ROWS",
              "values": [
                ["name1", "22"],
                ["name2", "24"],
                ["name3", "25"]
              ]
            }
          ]
        }
        """
        batch_request_ranges = f"{stream_name}!2:202"
        http_mocker.get(
            RequestBuilder.get_account_endpoint().with_spreadsheet_id(_SPREADSHEET_ID).with_ranges(batch_request_ranges).with_major_dimension("ROWS").with_alt("json").build(),
            HttpResponse(json.dumps(find_template(range_data_response_file, __file__)), range_response_code)
        )

    @HttpMocker()
    def test_given_spreadsheet_when_check_then_status_is_succeeded(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "check_succeeded_range")

        output = self._check(self._config, expecting_exception=False)
        expected_message = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Check succeeded"))
        assert output.logs[-1] == expected_message

    def test_given_authentication_error_when_check_then_status_is_failed(self) -> None:
        del self._config["credentials"]["client_secret"]

        output = self._check(self._config, expecting_exception=False)
        msg = AirbyteConnectionStatus(status=Status.FAILED, message="Config validation error: 'Service' was expected")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @pytest.mark.skip("Need service credentials to test this behavior")
    def test_given_service_authentication_error_when_check_then_status_is_failed(self) -> None:
        # todo, test this with service credentials
        wrong_service_account_info = deepcopy(service_account_info)
        del wrong_service_account_info["client_email"]
        wrong_service_account_info_encoded = json.dumps(service_account_info)#.encode("utf-8")
        wrong_service_account_credentials = {
            "auth_type": "Service",
            "service_account_info": wrong_service_account_info_encoded,
        }
        wrong_config = {
          "spreadsheet_id": _SPREADSHEET_ID,
          "credentials": wrong_service_account_credentials
        }
        # connection_status = self._source.check(Mock(), wrong_service_account_credentials)
        output = self._check(wrong_config, expecting_exception=True)

        msg = AirbyteConnectionStatus(status=Status.FAILED, message="")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @HttpMocker()
    def test_invalid_credentials_error_message_when_check(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(),
            HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 401)
        )
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message="Something went wrong in the connector. See the logs for more details.",
                internal_message='401 Client Error: None for url: https://www.googleapis.com/oauth2/v4/token',
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_invalid_link_error_message_when_check(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_link", 404)
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message="The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync.",
                internal_message=ANY,
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    def test_check_invalid_creds_json_file(self) -> None:
        invalid_creds_json_file = {}
        output = self._check(invalid_creds_json_file, expecting_exception=True)
        msg = AirbyteConnectionStatus(status=Status.FAILED, message="Config validation error: 'spreadsheet_id' is a required property")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @HttpMocker()
    def test_check_access_expired(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_permissions", 403)
        error_message = (
            "The authenticated Google Sheets user does not have permissions to view the "
            f"spreadsheet with id {_SPREADSHEET_ID}. Please ensure the authenticated user has access"
            " to the Spreadsheet and reauthenticate. If the issue persists, contact support. "
            "The caller does not have right permissions."
        )
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=error_message,
                internal_message=ANY,
                failure_type=FailureType.config_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_check_expected_to_read_data_from_1_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "check_wrong_range", 200)
        error_message =  f'Unable to read the schema of sheet. Error: Unexpected return result: Sheet was expected to contain data on exactly 1 sheet.'
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=error_message,
                internal_message=ANY,
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_check_duplicated_headers(self, http_mocker: HttpMocker) -> None:
        # With headers, we refer to properties that will be used for schema
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "check_succeeded_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "check_duplicate_headers", 200)

        error_message =  f"The following duplicate headers were found in the sheet. Please fix them to continue: ['header1']"
        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=error_message,
                internal_message=ANY,
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_given_grid_sheet_type_with_at_least_one_row_when_discover_then_return_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "only_headers_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "only_headers_range", 200)

        expected_schema  = {'$schema': 'http://json-schema.org/draft-07/schema#', 'properties': {'header1': {'type': ['null', 'string']}, 'header2': {'type': ['null', 'string']}}, 'type': 'object'}
        expected_catalog = AirbyteCatalog(streams=[AirbyteStream(name="a_stream_name", json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False)])
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message

    @HttpMocker()
    def test_discover_return_expected_schema(self, http_mocker: HttpMocker) -> None:
        expected_schemas_properties = {
            _STREAM_NAME: {'age': {'type':  ['null', 'string']}, 'name': {'type':  ['null', 'string']}},
            _B_STREAM_NAME: {'email': {'type':  ['null', 'string']}, 'name': {'type':  ['null', 'string']}},
            _C_STREAM_NAME: {'address': {'type':  ['null', 'string']}}
        }
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "multiple_streams_schemas_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        expected_streams = []
        for expected_stream_name, expected_stream_properties in expected_schemas_properties.items():
            expected_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                               'properties': expected_stream_properties,
                               'type': 'object'}
            expected_stream = AirbyteStream(name=expected_stream_name, json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False)
            expected_streams.append(expected_stream)
        expected_catalog = AirbyteCatalog(streams=expected_streams)
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message

    @HttpMocker()
    def test_discover_with_names_conversion(self, http_mocker: HttpMocker) -> None:
        # will convert '1 тест' to '_1_test
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "only_headers_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "names_conversion_range", 200)
        expected_schema  = {'$schema': 'http://json-schema.org/draft-07/schema#', 'properties': {'_1_test': {'type': ['null', 'string']}, 'header_2': {'type': ['null', 'string']}}, 'type': 'object'}
        expected_catalog = AirbyteCatalog(streams=[AirbyteStream(name="a_stream_name", json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False)])
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        self._config["names_conversion"] = True
        output = self._discover(self._config, expecting_exception=False)
        assert output
        assert output.catalog == expected_message

    @HttpMocker()
    def test_discover_could_not_run_discover(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "internal_server_error", 500)

        with patch("time.sleep"):
            output = self._discover(self._config, expecting_exception=True)
            expected_message = (
                "Could not discover the schema of your spreadsheet. There was an issue with the Google Sheets API."
                " This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support. Interval Server error."
            )

            trace_message = AirbyteTraceMessage(
                type=TraceType.ERROR,
                emitted_at=ANY,
                error=AirbyteErrorTraceMessage(
                    message='Something went wrong in the connector. See the logs for more details.',
                    internal_message=expected_message,
                    failure_type=FailureType.system_error,
                    stack_trace=ANY,
                ),
            )
            expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
            assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_discover_invalid_credentials_error_message(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(),
            HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 401)
        )

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message="Something went wrong in the connector. See the logs for more details.",
                internal_message='401 Client Error: None for url: https://www.googleapis.com/oauth2/v4/token',
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        output = self._discover(self._config, expecting_exception=True)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_discover_404_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_link", 404)
        output = self._discover(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message="The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync.",
                internal_message=ANY,
                failure_type=FailureType.system_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_discover_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_permissions", 403)
        output = self._discover(self._config, expecting_exception=True)
        error_message = (
            "The authenticated Google Sheets user does not have permissions to view the "
            f"spreadsheet with id {_SPREADSHEET_ID}. Please ensure the authenticated user has access"
            " to the Spreadsheet and reauthenticate. If the issue persists, contact support. "
            "The caller does not have right permissions."
        )

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=error_message,
                internal_message=ANY,
                failure_type=FailureType.config_error,
                stack_trace=ANY,
            ),
        )
        expected_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_message

    @HttpMocker()
    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "no_rows_meta", 200)
        output = self._discover(self._config, expecting_exception=False)
        assert len(output.catalog.catalog.streams) == 0

    @HttpMocker()
    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "non_grid_sheet_meta", 200)
        output = self._discover(self._config, expecting_exception=False)
        assert len(output.catalog.catalog.streams) == 0

    @HttpMocker()
    def test_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range")
        GoogleSheetSourceTest.get_stream_data(http_mocker, "read_records_range_with_dimensions")

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        output =  self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 2

    @HttpMocker()
    @pytest.mark.skip("Pending to do")
    def test_when_read_then_return_records_with_name_conversion(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "names_conversion_range")
        GoogleSheetSourceTest.get_stream_data(http_mocker, "read_records_range_with_dimensions")

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"_1_test": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        self._config["names_conversion"] = True
        output =  self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 2

    @HttpMocker()
    def test_when_read_multiple_streams_return_records(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "multiple_streams_schemas_meta", 200)

        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        GoogleSheetSourceTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range_2")
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range_2", stream_name=_B_STREAM_NAME)
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range_2", stream_name=_C_STREAM_NAME)

        configured_catalog = (CatalogBuilder().with_stream(
            ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).
                with_json_schema({"properties": {'age': {'type': 'string'}, 'name': {'type': 'string'}}
                                  })
        ).with_stream(
            ConfiguredAirbyteStreamBuilder().with_name(_B_STREAM_NAME).
                with_json_schema({"properties": {'email': {'type': 'string'}, 'name': {'type': 'string'}}
                                  })
        ).with_stream(
            ConfiguredAirbyteStreamBuilder().with_name(_C_STREAM_NAME).
                with_json_schema({"properties": {'address': {'type': 'string'}}
                                  })
        )
        .build())

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 9

        assert output.state_messages[0].state.stream.stream_descriptor.name == _STREAM_NAME
        assert output.state_messages[1].state.stream.stream_descriptor.name == _B_STREAM_NAME
        assert output.state_messages[2].state.stream.stream_descriptor.name == _C_STREAM_NAME

        expected_messages = []
        for current_stream in [_STREAM_NAME, _B_STREAM_NAME, _C_STREAM_NAME]:
            for current_status in [AirbyteStreamStatus.COMPLETE, AirbyteStreamStatus.RUNNING, AirbyteStreamStatus.STARTED]:
                stream_descriptor = StreamDescriptor(
                    name=current_stream,
                    namespace=None
                )
                stream_status = AirbyteStreamStatusTraceMessage(
                    status= current_status,
                    stream_descriptor=stream_descriptor
                )
                airbyte_trace_message = AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=ANY,
                    stream_status= stream_status
                )
                airbyte_message = AirbyteMessage(type=Type.TRACE, trace=airbyte_trace_message)
                expected_messages.append(airbyte_message)
        assert len(output.trace_messages) == len(expected_messages)
        for message in expected_messages:
            assert message in output.trace_messages

    @HttpMocker()
    def test_when_read_then_status_and_state_messages_emitted(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta_2", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range_2", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "read_records_range_with_dimensions_2")

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == 5
        assert output.state_messages[0].state.stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)
        assert output.state_messages[0].state.stream.stream_descriptor.name == _STREAM_NAME

        assert output.trace_messages[0].trace.stream_status.status == AirbyteStreamStatus.STARTED
        assert output.trace_messages[1].trace.stream_status.status == AirbyteStreamStatus.RUNNING
        assert output.trace_messages[2].trace.stream_status.status == AirbyteStreamStatus.COMPLETE


    @HttpMocker()
    def test_read_429_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "rate_limit_error", 429)

        configured_catalog =CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        with patch("time.sleep"):
            output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)

        expected_message = (
            "Exception while syncing stream a_stream_name: Stopped syncing process due to rate limits. Rate limit has been reached. Please try later or request a higher quota for your account."
        )
        assert output.errors[0].trace.error.internal_message == expected_message

    @HttpMocker()
    def test_read_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "invalid_permissions", 403)

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        # output = read(self._source, self._config, configured_catalog)
        output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)

        expected_message = (
            f"The authenticated Google Sheets user does not have permissions to view the spreadsheet with id {_SPREADSHEET_ID}. Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. If the issue persists, contact support. The caller does not have right permissions."
        )
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_500_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "internal_server_error", 500)

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        with patch("time.sleep"):
            output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)

        expected_message = (
            "Exception while syncing stream a_stream_name: There was an issue with the Google Sheets API. This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support"
        )
        assert output.errors[0].trace.error.internal_message == expected_message

    @HttpMocker()
    def test_read_empty_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range_empty", 200)

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)
        expected_message = (
            f"Unable to read the schema of sheet. Error: Unexpected return result: Sheet was expected to contain data on exactly 1 sheet."
        )
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_expected_data_on_1_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range_with_unexpected_extra_sheet", 200)

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)
        expected_message = (
            f"Unable to read the schema of sheet. Error: Unexpected return result: Sheet was expected to contain data on exactly 1 sheet."
        )
        assert output.errors[0].trace.error.message == expected_message

    @pytest.mark.skip("Pending to do")
    def test_name_conversion_for_schema_match(self):
        pass

    @pytest.mark.skip("Pending to do")
    def test_for_columns_empty_does_right_match(self):
        pass

    @pytest.mark.skip("Pending to do")
    def test_for_increase_batch_size_when_rate_limit(self):
        pass
