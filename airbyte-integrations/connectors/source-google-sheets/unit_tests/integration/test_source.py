# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import json
from copy import deepcopy
from typing import Any, Dict, Optional, Tuple
from requests.status_codes import codes as status_codes
from unittest import TestCase
from unittest.mock import ANY, patch

import pytest
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteErrorTraceMessage,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
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
from source_google_sheets.utils import exception_description_by_status_code

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

GET_SPREADSHEET_INFO = "get_spreadsheet_info"
GET_SHEETS_FIRST_ROW = "get_sheet_first_row"
GET_STREAM_DATA = "get_stream_data"

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
    def get_stream_data(http_mocker: HttpMocker, data_response_file: str, response_code: int=200, stream_name:Optional[str]=_STREAM_NAME, request_range: Tuple=(2,202) ):
        """"
        Mock requests to 'https://sheets.googleapis.com/v4/spreadsheets/<spreadsheet>/values:batchGet?ranges=<sheet>!2:202&majorDimension=ROWS&alt=json'
        to obtain value ranges (data) for stream from the spreadsheet + sheet provided.
        For this we use range e.g. [2:202(2 + range in config which default is 200)].
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
        start_range = str(request_range[0])
        end_range = str(request_range[1])
        batch_request_ranges = f"{stream_name}!{start_range}:{end_range}"
        http_mocker.get(
            RequestBuilder.get_account_endpoint().with_spreadsheet_id(_SPREADSHEET_ID).with_ranges(batch_request_ranges).with_major_dimension("ROWS").with_alt("json").build(),
            HttpResponse(json.dumps(find_template(data_response_file, __file__)), response_code)
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
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_link", status_codes.NOT_FOUND)
        error_message = exception_description_by_status_code(status_codes.NOT_FOUND, _SPREADSHEET_ID)
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

    def test_check_invalid_creds_json_file(self) -> None:
        invalid_creds_json_file = {}
        output = self._check(invalid_creds_json_file, expecting_exception=True)
        msg = AirbyteConnectionStatus(status=Status.FAILED, message="Config validation error: 'spreadsheet_id' is a required property")
        expected_message = AirbyteMessage(type=Type.CONNECTION_STATUS, connectionStatus=msg)
        assert output._messages[-1] == expected_message

    @HttpMocker()
    def test_check_access_expired(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_permissions", status_codes.FORBIDDEN)
        expected_message = exception_description_by_status_code(status_codes.FORBIDDEN, _SPREADSHEET_ID) + ". The caller does not have right permissions."

        output = self._check(self._config, expecting_exception=True)
        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=expected_message,
                internal_message=ANY,
                failure_type=FailureType.config_error,
                stack_trace=ANY,
            ),
        )
        expected_airbyte_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_airbyte_message

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
    def test_discover_empty_column_return_expected_schema(self, http_mocker: HttpMocker) -> None:
        """
        The response from headers (first row) has columns "name | age | | address | address2"  so everything after empty cell will be
        discarded, in this case address and address2 shouldn't be part of the schema.
        """
        expected_schemas_properties = {
            _STREAM_NAME: {'name': {'type':  ['null', 'string']}, 'age': {'type':  ['null', 'string']}},
        }
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "discover_with_empty_column_spreadsheet_info_and_sheets", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"discover_with_empty_column_get_sheet_first_row", 200)


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
    def test_discover_with_duplicated_return_expected_schema(self, http_mocker: HttpMocker):
        """
        The response from headers (first row) has columns "header_1 | header_2 | header_2 | address | address2"  so header_2 will
        be ignored from schema.
        """
        expected_schema_properties = {'header_1': {'type': ['null', 'string']}, 'address': {'type': ['null', 'string']}, 'address2': {'type': ['null', 'string']}
        }
        test_file_base_name = "discover_duplicated_headers"
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")

        expected_schema = {'$schema': 'http://json-schema.org/draft-07/schema#',
                           'properties': expected_schema_properties,
                           'type': 'object'}
        expected_stream = AirbyteStream(name=_STREAM_NAME, json_schema=expected_schema,
                                        supported_sync_modes=[SyncMode.full_refresh], is_resumable=False)

        expected_catalog = AirbyteCatalog(streams=[expected_stream])
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)
        expected_log_message = AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message="Duplicate headers found in sheet. Ignoring them: ['header_2']"))

        output = self._discover(self._config, expecting_exception=False)

        assert output.catalog == expected_message
        assert output.logs[-1] == expected_log_message

    @HttpMocker()
    def test_discover_with_names_conversion(self, http_mocker: HttpMocker) -> None:
        # will convert '1 тест' to '_1_test and 'header2' to 'header_2'
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "only_headers_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "names_conversion_range", 200)
        expected_schema  = {'$schema': 'http://json-schema.org/draft-07/schema#', 'properties': {'_1_test': {'type': ['null', 'string']}, 'header_2': {'type': ['null', 'string']}}, 'type': 'object'}
        expected_catalog = AirbyteCatalog(streams=[AirbyteStream(name="a_stream_name", json_schema=expected_schema, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False)])
        expected_message = AirbyteMessage(type=Type.CATALOG, catalog=expected_catalog)

        self._config["names_conversion"] = True
        output = self._discover(self._config, expecting_exception=False)
        assert output.catalog == expected_message

    @HttpMocker()
    def test_discover_could_not_run_discover(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "internal_server_error", status_codes.INTERNAL_SERVER_ERROR)

        with patch("time.sleep"):
            output = self._discover(self._config, expecting_exception=True)
            expected_message = exception_description_by_status_code(status_codes.INTERNAL_SERVER_ERROR, _SPREADSHEET_ID)

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
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_link", status_codes.NOT_FOUND)
        output = self._discover(self._config, expecting_exception=True)
        error_message = exception_description_by_status_code(status_codes.NOT_FOUND, _SPREADSHEET_ID)
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
    def test_discover_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "invalid_permissions", status_codes.FORBIDDEN)
        output = self._discover(self._config, expecting_exception=True)

        expected_message = exception_description_by_status_code(status_codes.FORBIDDEN, _SPREADSHEET_ID) + ". The caller does not have right permissions."

        trace_message = AirbyteTraceMessage(
            type=TraceType.ERROR,
            emitted_at=ANY,
            error=AirbyteErrorTraceMessage(
                message=expected_message,
                internal_message=ANY,
                failure_type=FailureType.config_error,
                stack_trace=ANY,
            ),
        )
        expected_airbyte_message = AirbyteMessage(type=Type.TRACE, trace=trace_message)
        assert output.errors[-1] == expected_airbyte_message

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
        first_property = "header_1"
        second_property = "header_2"
        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {first_property: { "type": ["null", "string"] }, second_property: { "type": ["null", "string"] }}})).build()

        output =  self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: 'value_11', second_property: 'value_12'}
                )
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: 'value_21', second_property: 'value_22'}
                )
            )
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_empty_column_then_return_records(self, http_mocker: HttpMocker) -> None:
        """
        The response from headers (first row) has columns "header_1 | header_2 | | address | address2"  so everything after empty cell will be
        discarded, in this case address and address2 shouldn't be part of the schema in records.
        """
        test_file_base_name = "read_with_empty_column"
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"{test_file_base_name}_{GET_STREAM_DATA}")
        first_property = "header_1"
        second_property = "header_2"
        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema(
            {"properties": {first_property: {"type": ["null", "string"]}, second_property: {"type": ["null", "string"]}}})).build()

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: 'value_11', second_property: 'value_12'}
                )
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: 'value_21', second_property: 'value_22'}
                )
            )
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_with_duplicated_headers_then_return_records(self, http_mocker: HttpMocker):
        """"
        header_2 will be ignored from records as column is duplicated.

        header_1	header_2	header_2	address	        address2
        value_11	value_12	value_13	main	        main st
        value_21	value_22	value_23	washington 3	colonial

        It will correctly match row values and field/column names in read records.
        """
        test_file_base_name = "read_duplicated_headers"
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"{test_file_base_name}_{GET_STREAM_DATA}")
        first_property = "header_1"
        second_property = "address"
        third_property = "address2"
        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema(
            {"properties": {first_property: {"type": ["null", "string"]},
                            second_property: {"type": ["null", "string"]},
                            third_property: {"type": ["null", "string"]},
                            }})

        ).build()

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: 'value_11', second_property: 'main', third_property: 'main st'}
                )
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_property: 'value_21', second_property: 'washington 3', third_property: 'colonial'}
                )
            )
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

    @HttpMocker()
    def test_when_empty_rows_then_return_records(self, http_mocker: HttpMocker):
        """"
        There are a few empty rows in the response that we shuld ignore

        e.g.
        id	name	            normalized_name
        7	Children	        children
        12	Mechanical Santa	mechanical santa
        13	Tattoo Man	        tattoo man
        16	DOCTOR ZITSOFSKY	doctor zitsofsky


        20	Students	        students

        There are two empty rows between id 16 and 20 that we will not be present in read records
        """
        test_file_base_name = "read_empty_rows"
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"{test_file_base_name}_{GET_STREAM_DATA}")
        expected_properties = ["id", "name", "normalized_name"]
        catalog_properties = {}
        for property in expected_properties:
            catalog_properties[property] = {"type": ["null", "string"]}
        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema(
            {"properties": catalog_properties})

        ).build()

        records_in_response = find_template(f"{test_file_base_name}_{GET_STREAM_DATA}", __file__)
        empty_row_count = 0
        expected_rows_found = 23
        expected_empty_rows = 7
        expected_records = []

        for row in records_in_response["valueRanges"][0]["values"]:
            if row:
                expected_records += [
                    AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(
                                emitted_at=ANY,
                                stream=_STREAM_NAME,
                                data={expected_property:row_value for expected_property,row_value in zip(expected_properties, row)}
                            )
                        )
                ]
            else:
                empty_row_count += 1
        assert empty_row_count == expected_empty_rows
        assert len(expected_records) == expected_rows_found
        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) == expected_rows_found
        assert output.records == expected_records

    @HttpMocker()
    def test_when_read_by_batches_make_expected_requests(self, http_mocker: HttpMocker):
        test_file_base_name = "read_by_batches"
        batch_size = 10
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, f"{test_file_base_name}_{GET_SPREADSHEET_INFO}")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, f"{test_file_base_name}_{GET_SHEETS_FIRST_ROW}")
        start_range = 2
        for range_file_postfix in ("first_batch", "second_batch", "third_batch", "fourth_batch", "fifth_batch"):
            end_range = start_range + batch_size
            request_range = (start_range, end_range)
            GoogleSheetSourceTest.get_stream_data(http_mocker, data_response_file=f"{test_file_base_name}_{GET_STREAM_DATA}_{range_file_postfix}", request_range=request_range)
            start_range += batch_size + 1
        catalog_properties = {}
        for expected_property in ["id", "name", "normalized_name"]:
            catalog_properties[expected_property] = {"type": ["null", "string"]}
        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema(
            {"properties": catalog_properties})
        ).build()
        self._config["batch_size"] = batch_size
        output = self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        assert len(output.records) > 0

    @HttpMocker()
    def test_when_read_then_return_records_with_name_conversion(self, http_mocker: HttpMocker) -> None:
        # will convert '1 тест' to '_1_test and 'header2' to 'header_2'
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta")
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "names_conversion_range")
        GoogleSheetSourceTest.get_stream_data(http_mocker, "read_records_range_with_dimensions")

        first_expected_converted_property = "_1_test"
        second_expected_converted_property = "header_2"
        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {first_expected_converted_property: { "type": ["null", "string"] }, second_expected_converted_property: { "type": ["null", "string"] }}})).build()

        self._config["names_conversion"] = True
        output =  self._read(self._config, catalog=configured_catalog, expecting_exception=False)
        expected_records = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_expected_converted_property: 'value_11', second_expected_converted_property: 'value_12'}
                )
            ),
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    emitted_at=ANY,
                    stream=_STREAM_NAME,
                    data={first_expected_converted_property: 'value_21', second_expected_converted_property: 'value_22'}
                )
            )
        ]
        assert len(output.records) == 2
        assert output.records == expected_records

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

        assert len(output.state_messages) == 3
        state_messages_streams = []
        for state_message in output.state_messages:
            state_messages_streams.append(state_message.state.stream.stream_descriptor.name)

        assert _STREAM_NAME in state_messages_streams
        assert _B_STREAM_NAME in state_messages_streams
        assert _C_STREAM_NAME in state_messages_streams

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
        GoogleSheetSourceTest.get_stream_data(http_mocker, "rate_limit_error", status_codes.TOO_MANY_REQUESTS)

        configured_catalog =CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        with patch("time.sleep"):
            output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)

        expected_message = f"Exception while syncing stream {_STREAM_NAME}: " + exception_description_by_status_code(status_codes.TOO_MANY_REQUESTS, _STREAM_NAME)

        assert output.errors[0].trace.error.internal_message == expected_message

    @HttpMocker()
    def test_read_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_spreadsheet_info_and_sheets(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_sheet_first_row(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "invalid_permissions", status_codes.FORBIDDEN)

        configured_catalog = CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()

        output = self._read(self._config, catalog=configured_catalog, expecting_exception=True)
        expected_message = exception_description_by_status_code(status_codes.FORBIDDEN, _SPREADSHEET_ID) + ". The caller does not have right permissions."
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
    def test_for_increase_batch_size_when_rate_limit(self):
        pass
