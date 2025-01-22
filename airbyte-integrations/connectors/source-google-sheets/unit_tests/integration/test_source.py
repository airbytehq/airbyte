# Copyright (c) 2024 Airbyte, Inc., all rights reserved.


import json
from copy import deepcopy
from typing import Optional
from unittest import TestCase
from unittest.mock import (
    Mock,
    patch,  # patch("time.sleep")
)

import pytest
from source_google_sheets import SourceGoogleSheets

from airbyte_cdk.models import Status
from airbyte_cdk.models.airbyte_protocol import AirbyteStateBlob, AirbyteStreamStatus
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.utils import AirbyteTracedException

from .custom_http_mocker import CustomHttpMocker as HttpMocker
from .request_builder import AuthBuilder, RequestBuilder
from .test_credentials import oauth_credentials, service_account_credentials, service_account_info


_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"
_B_STREAM_NAME = "b_stream_name"
_C_STREAM_NAME = "c_stream_name"


_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": oauth_credentials}

_SERVICE_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": service_account_credentials}


class GoogleSheetSourceTest(TestCase):
    def setUp(self) -> None:
        self._config = deepcopy(_CONFIG)
        self._service_config = deepcopy(_SERVICE_CONFIG)
        self._source = SourceGoogleSheets()

    @staticmethod
    def authorize(http_mocker: HttpMocker):
        # Authorization request with user credentials to "https://oauth2.googleapis.com" to obtain a token
        http_mocker.post(AuthBuilder.get_token_endpoint().build(), HttpResponse(json.dumps(find_template("auth_response", __file__)), 200))

    @staticmethod
    def get_streams(http_mocker: HttpMocker, streams_response_file: Optional[str] = None, meta_response_code: Optional[int] = 200):
        """ "
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
                HttpResponse(json.dumps(find_template(streams_response_file, __file__)), meta_response_code),
            )

    @staticmethod
    def get_schema(
        http_mocker: HttpMocker,
        headers_response_file: str,
        headers_response_code: int = 200,
        stream_name: Optional[str] = _STREAM_NAME,
        data_initial_range_response_file: Optional[str] = None,
        data_initial_response_code: Optional[int] = 200,
    ):
        """ "
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
            RequestBuilder()
            .with_spreadsheet_id(_SPREADSHEET_ID)
            .with_include_grid_data(True)
            .with_ranges(f"{stream_name}!1:1")
            .with_alt("json")
            .build(),
            HttpResponse(json.dumps(find_template(headers_response_file, __file__)), headers_response_code),
        )

    @staticmethod
    def get_stream_data(
        http_mocker: HttpMocker, range_data_response_file: str, range_response_code: int = 200, stream_name: Optional[str] = _STREAM_NAME
    ):
        """ "
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
            RequestBuilder.get_account_endpoint()
            .with_spreadsheet_id(_SPREADSHEET_ID)
            .with_ranges(batch_request_ranges)
            .with_major_dimension("ROWS")
            .with_alt("json")
            .build(),
            HttpResponse(json.dumps(find_template(range_data_response_file, __file__)), range_response_code),
        )

    @HttpMocker()
    def test_given_spreadsheet_when_check_then_status_is_succeeded(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "check_succeeded_meta")
        GoogleSheetSourceTest.get_schema(http_mocker, "check_succeeded_range")
        connection_status = self._source.check(Mock(), self._config)
        assert connection_status.status == Status.SUCCEEDED

    def test_given_authentication_error_when_check_then_status_is_failed(self) -> None:
        del self._config["credentials"]["client_secret"]
        connection_status = self._source.check(Mock(), self._config)
        assert connection_status.status == Status.FAILED

    def test_given_service_authentication_error_when_check_then_status_is_failed(self) -> None:
        wrong_service_account_info = deepcopy(service_account_info)
        del wrong_service_account_info["client_email"]
        wrong_service_account_info_encoded = json.dumps(service_account_info).encode("utf-8")
        wrong_service_account_credentials = {
            "auth_type": "Service",
            "service_account_info": wrong_service_account_info_encoded,
        }
        connection_status = self._source.check(Mock(), wrong_service_account_credentials)
        assert connection_status.status == Status.FAILED

    @HttpMocker()
    def test_invalid_credentials_error_message_when_check(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(), HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 200)
        )
        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check(Mock(), self._config)

        assert str(exc_info.value) == ("Access to the spreadsheet expired or was revoked. Re-authenticate to restore access.")

    @HttpMocker()
    def test_invalid_link_error_message_when_check(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "invalid_link", 404)

        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check(Mock(), self._config)
        assert str(exc_info.value) == (
            "Config error: The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync."
        )

    def test_check_invalid_creds_json_file(self) -> None:
        connection_status = self._source.check(Mock(), "")
        assert "Please use valid credentials json file" in connection_status.message
        assert connection_status.status == Status.FAILED

    @HttpMocker()
    def test_check_access_expired(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "invalid_permissions", 403)
        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check(Mock(), self._config)
        assert str(exc_info.value) == ("Config error: ")

    @HttpMocker()
    def test_check_expected_to_read_data_from_1_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "check_succeeded_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "check_wrong_range", 200)

        connection_status = self._source.check(Mock(), self._config)
        assert connection_status.status == Status.FAILED
        assert (
            connection_status.message
            == f"Unable to read the schema of sheet a_stream_name. Error: Unexpected return result: Sheet {_STREAM_NAME} was expected to contain data on exactly 1 sheet. "
        )

    @HttpMocker()
    def test_check_duplicated_headers(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "check_succeeded_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "check_duplicate_headers", 200)

        connection_status = self._source.check(Mock(), self._config)
        assert connection_status.status == Status.FAILED
        assert (
            connection_status.message
            == f"The following duplicate headers were found in the following sheets. Please fix them to continue: [sheet:{_STREAM_NAME}, headers:['header1']]"
        )

    @HttpMocker()
    def test_given_grid_sheet_type_with_at_least_one_row_when_discover_then_return_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "only_headers_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "only_headers_range", 200)

        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 1
        assert len(discovered_catalog.streams[0].json_schema["properties"]) == 2

    @HttpMocker()
    def test_discover_return_expected_schema(self, http_mocker: HttpMocker) -> None:
        # When we move to manifest only is possible that DynamicSchemaLoader will identify fields like age as integers
        # and addresses "oneOf": [{"type": ["null", "string"]}, {"type": ["null", "integer"]}] as it has mixed data
        expected_schemas_properties = {
            _STREAM_NAME: {"age": {"type": "string"}, "name": {"type": "string"}},
            _B_STREAM_NAME: {"email": {"type": "string"}, "name": {"type": "string"}},
            _C_STREAM_NAME: {"address": {"type": "string"}},
        }
        GoogleSheetSourceTest.get_streams(http_mocker, "multiple_streams_schemas_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetSourceTest.get_schema(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 3
        for current_stream in discovered_catalog.streams:
            assert current_stream.json_schema["properties"] == expected_schemas_properties[current_stream.name]

    @HttpMocker()
    def test_discover_with_names_conversion(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "only_headers_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "names_conversion_range", 200)

        self._config["names_conversion"] = True

        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 1
        assert len(discovered_catalog.streams[0].json_schema["properties"]) == 2
        assert "_1_test" in discovered_catalog.streams[0].json_schema["properties"].keys()

    @HttpMocker()
    def test_discover_could_not_run_discover(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "internal_server_error", 500)

        with pytest.raises(Exception) as exc_info, patch("time.sleep"), patch("backoff._sync._maybe_call", side_effect=lambda value: 3):
            self._source.discover(Mock(), self._config)
        expected_message = (
            "Could not discover the schema of your spreadsheet. There was an issue with the Google Sheets API."
            " This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support. Interval Server error."
        )
        assert str(exc_info.value) == expected_message

    @HttpMocker()
    def test_discover_invalid_credentials_error_message(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(), HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 200)
        )

        with pytest.raises(Exception) as exc_info:
            self._source.discover(Mock(), self._config)
        expected_message = "Access to the spreadsheet expired or was revoked. Re-authenticate to restore access."
        assert str(exc_info.value) == expected_message

    @HttpMocker()
    def test_discover_404_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "invalid_link", 404)

        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.discover(Mock(), self._config)
        expected_message = (
            f"The requested Google Sheets spreadsheet with id {_SPREADSHEET_ID} does not exist."
            " Please ensure the Spreadsheet Link you have set is valid and the spreadsheet exists. If the issue persists, contact support. Requested entity was not found.."
        )
        assert str(exc_info.value) == expected_message

    @HttpMocker()
    def test_discover_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "invalid_permissions", 403)

        with pytest.raises(AirbyteTracedException) as exc_info:
            self._source.discover(Mock(), self._config)
        expected_message = (
            "The authenticated Google Sheets user does not have permissions to view the "
            f"spreadsheet with id {_SPREADSHEET_ID}. Please ensure the authenticated user has access"
            " to the Spreadsheet and reauthenticate. If the issue persists, contact support. "
            "The caller does not have right permissions."
        )
        assert str(exc_info.value) == expected_message

    @HttpMocker()
    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "no_rows_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "no_rows_range", 200)

        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 0

    @HttpMocker()
    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "non_grid_sheet_meta", 200)
        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 0

    @HttpMocker()
    def test_when_read_then_return_records(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta")
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range")
        GoogleSheetSourceTest.get_stream_data(http_mocker, "read_records_range_with_dimensions")

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = read(self._source, self._config, configured_catalog)
        assert len(output.records) == 2

    @HttpMocker()
    def test_when_read_multiple_streams_return_records(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "multiple_streams_schemas_meta", 200)

        GoogleSheetSourceTest.get_schema(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range", 200, _B_STREAM_NAME)
        GoogleSheetSourceTest.get_schema(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range", 200, _C_STREAM_NAME)

        GoogleSheetSourceTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_STREAM_NAME}_range_2")
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_B_STREAM_NAME}_range_2", stream_name=_B_STREAM_NAME)
        GoogleSheetSourceTest.get_stream_data(http_mocker, f"multiple_streams_schemas_{_C_STREAM_NAME}_range_2", stream_name=_C_STREAM_NAME)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"age": {"type": "string"}, "name": {"type": "string"}}})
            )
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_B_STREAM_NAME)
                .with_json_schema({"properties": {"email": {"type": "string"}, "name": {"type": "string"}}})
            )
            .with_stream(
                ConfiguredAirbyteStreamBuilder().with_name(_C_STREAM_NAME).with_json_schema({"properties": {"address": {"type": "string"}}})
            )
            .build()
        )

        output = read(self._source, self._config, configured_catalog)
        assert len(output.records) == 9

        assert output.state_messages[0].state.stream.stream_descriptor.name == _STREAM_NAME
        assert output.state_messages[1].state.stream.stream_descriptor.name == _B_STREAM_NAME
        assert output.state_messages[2].state.stream.stream_descriptor.name == _C_STREAM_NAME

        airbyte_stream_statuses = [AirbyteStreamStatus.COMPLETE, AirbyteStreamStatus.RUNNING, AirbyteStreamStatus.STARTED]
        for output_id in range(3):
            assert output.state_messages[output_id].state.stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)
            expected_status = airbyte_stream_statuses.pop()
            assert output.trace_messages[output_id].trace.stream_status.status == expected_status
            assert output.trace_messages[output_id + 3].trace.stream_status.status == expected_status
            assert output.trace_messages[output_id + 6].trace.stream_status.status == expected_status

    @HttpMocker()
    def test_when_read_then_status_and_state_messages_emitted(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta_2", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range_2", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "read_records_range_with_dimensions_2")

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = read(self._source, self._config, configured_catalog)
        assert len(output.records) == 5
        assert output.state_messages[0].state.stream.stream_state == AirbyteStateBlob(__ab_no_cursor_state_message=True)
        assert output.state_messages[0].state.stream.stream_descriptor.name == _STREAM_NAME

        assert output.trace_messages[0].trace.stream_status.status == AirbyteStreamStatus.STARTED
        assert output.trace_messages[1].trace.stream_status.status == AirbyteStreamStatus.RUNNING
        assert output.trace_messages[2].trace.stream_status.status == AirbyteStreamStatus.COMPLETE

    @HttpMocker()
    def test_read_429_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "rate_limit_error", 429)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        with patch("time.sleep"), patch("backoff._sync._maybe_call", side_effect=lambda value: 1):
            output = read(self._source, self._config, configured_catalog)

        expected_message = "Stopped syncing process due to rate limits. Rate limit has been reached. Please try later or request a higher quota for your account."
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_403_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "invalid_permissions", 403)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = read(self._source, self._config, configured_catalog)

        expected_message = f"Stopped syncing process. The authenticated Google Sheets user does not have permissions to view the spreadsheet with id {_SPREADSHEET_ID}. Please ensure the authenticated user has access to the Spreadsheet and reauthenticate. If the issue persists, contact support"
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_500_error(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range", 200)
        GoogleSheetSourceTest.get_stream_data(http_mocker, "internal_server_error", 500)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        with patch("time.sleep"), patch("backoff._sync._maybe_call", side_effect=lambda value: 1):
            output = read(self._source, self._config, configured_catalog)

        expected_message = "Stopped syncing process. There was an issue with the Google Sheets API. This is usually a temporary issue from Google's side. Please try again. If this issue persists, contact support"
        assert output.errors[0].trace.error.message == expected_message

    @HttpMocker()
    def test_read_empty_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range_empty", 200)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = read(self._source, self._config, configured_catalog)
        expected_message = f"Unexpected return result: Sheet {_STREAM_NAME} was expected to contain data on exactly 1 sheet. "
        assert output.errors[0].trace.error.internal_message == expected_message

    @HttpMocker()
    def test_read_expected_data_on_1_sheet(self, http_mocker: HttpMocker) -> None:
        GoogleSheetSourceTest.get_streams(http_mocker, "read_records_meta", 200)
        GoogleSheetSourceTest.get_schema(http_mocker, "read_records_range_with_unexpected_extra_sheet", 200)

        configured_catalog = (
            CatalogBuilder()
            .with_stream(
                ConfiguredAirbyteStreamBuilder()
                .with_name(_STREAM_NAME)
                .with_json_schema({"properties": {"header_1": {"type": ["null", "string"]}, "header_2": {"type": ["null", "string"]}}})
            )
            .build()
        )

        output = read(self._source, self._config, configured_catalog)
        expected_message = f"Unexpected return result: Sheet {_STREAM_NAME} was expected to contain data on exactly 1 sheet. "
        assert output.errors[0].trace.error.internal_message == expected_message
