# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from copy import deepcopy
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest
from airbyte_cdk.models import Status
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.utils import AirbyteTracedException
from source_google_sheets import SourceGoogleSheets

from .custom_http_mocker import CustomHttpMocker
from .request_builder import AuthBuilder, RequestBuilder
from .test_credentials import oauth_credentials, service_account_credentials, service_account_info

_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"

_CONFIG = {
  "spreadsheet_id": _SPREADSHEET_ID,
  "credentials": oauth_credentials
}

_SERVICE_CONFIG = {
  "spreadsheet_id": _SPREADSHEET_ID,
  "credentials": service_account_credentials
}


class GoogleSheetSourceTest(TestCase):
    def setUp(self) -> None:
        self._config = deepcopy(_CONFIG)
        self._service_config = deepcopy(_SERVICE_CONFIG)
        self._source = SourceGoogleSheets()

    def test_given_spreadsheet_when_check_then_status_is_succeeded(self) -> None:
        http_mocker = CustomHttpMocker()
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200)
        )

        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("check_succeeded_meta", __file__)), 200)
        )

        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(f"{_STREAM_NAME}!1:1").with_alt("json").build(),
            HttpResponse(json.dumps(find_template("check_succeeded_range", __file__)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
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

    def test_given_authentication_error_when_invalid_client(self) -> None:
        http_mocker = CustomHttpMocker()
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(),
            HttpResponse(json.dumps(find_template("auth_invalid_client", __file__)), 200)
        )
        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request), pytest.raises(AirbyteTracedException) as exc_info:
            self._source.check(Mock(), self._config)

        assert str(exc_info.value) == (
            "Access to the spreadsheet expired or was revoked. Re-authenticate to restore access."
        )


    def test_given_grid_sheet_type_with_at_least_one_row_when_discover_then_return_stream(self) -> None:
        # spreadsheet_metadata request
        http_mocker = CustomHttpMocker()
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200)
        )
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("only_headers_meta", __file__)), 200)
        )

        # range 1:1 (headers)
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(f"{_STREAM_NAME}!1:1").with_alt("json").build(),
            HttpResponse(json.dumps(find_template("only_headers_range", __file__)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):

            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 1
            assert len(discovered_catalog.streams[0].json_schema["properties"]) == 2

    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self) -> None:
        http_mocker = CustomHttpMocker()
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200)
        )
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("no_rows_meta", __file__)), 200)
        )

        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(f"{_STREAM_NAME}!1:1").with_alt("json").build(),
            HttpResponse(json.dumps(find_template("no_rows_range", __file__)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 0

    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self) -> None:
        http_mocker = CustomHttpMocker()
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200)
        )
        # meta data request
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("non_grid_sheet_meta", __file__)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 0

    def test_when_read_then_return_records(self) -> None:
        http_mocker = CustomHttpMocker()
        http_mocker.post(
            AuthBuilder.get_token_endpoint().build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200)
        )
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("read_records_meta", __file__)), 200)
        )

        # discovery response
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(
                f"{_STREAM_NAME}!1:1").with_alt("json").build(),

            HttpResponse(json.dumps(find_template("read_records_range", __file__)), 200)
        )

        # batch response
        batch_request_ranges = f"{_STREAM_NAME}!2:202"
        http_mocker.get(
            RequestBuilder.get_account_endpoint().with_spreadsheet_id(_SPREADSHEET_ID).with_ranges(batch_request_ranges).with_major_dimension("ROWS").with_alt("json").build(),
            HttpResponse(json.dumps(find_template("read_records_range_with_dimensions", __file__)), 200)
        )
        configured_catalog =CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build()
        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            output = read(self._source, self._config, configured_catalog)
            assert len(output.records) == 2
