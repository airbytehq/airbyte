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
from google.auth.credentials import AnonymousCredentials
from source_google_sheets import SourceGoogleSheets

from .custom_http_mocker import CustomHttpMocker
from .google_credentials import service_account_credentials
from .request_builder import RequestBuilder


_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"

_CONFIG = {
  "spreadsheet_id": _SPREADSHEET_ID,
  "credentials": service_account_credentials
}

@pytest.fixture
def mock_google_credentials():
    with patch("google.oauth2.service_account.Credentials.from_service_account_info", return_value=AnonymousCredentials()):
        with patch("google.oauth2.credentials.Credentials.from_authorized_user_info", return_value=AnonymousCredentials()):
            yield

@pytest.fixture
def mock_google_credentials_with_error():
    # todo: mock "https://oauth2.googleapis.com/token" instead
    with patch(
        "google.oauth2.service_account.Credentials.from_service_account_info",
        side_effect=ValueError("Mocked ValueError for service account credentials"),
    ):
        with patch(
            "google.oauth2.credentials.Credentials.from_authorized_user_info",
            side_effect=ValueError("Mocked ValueError for user credentials"),
        ):
            yield

class GoogleSheetSourceTest(TestCase):
    def setUp(self) -> None:
        self._config = deepcopy(_CONFIG)
        self._source = SourceGoogleSheets()

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_spreadsheet_when_check_then_status_is_succeeded(self) -> None:
        http_mocker = CustomHttpMocker()
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

    @pytest.mark.usefixtures("mock_google_credentials_with_error")
    def test_given_authentication_error_when_check_then_status_is_failed(self) -> None:
        connection_status = self._source.check(Mock(), self._config)
        assert connection_status.status == Status.FAILED

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_grid_sheet_type_with_at_least_one_row_when_discover_then_return_stream(self) -> None:
        # spreadsheet_metadata request
        http_mocker = CustomHttpMocker()
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

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self) -> None:
        http_mocker = CustomHttpMocker()
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

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self) -> None:
        http_mocker = CustomHttpMocker()
        # meta data request
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("non_grid_sheet_meta", __file__)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 0

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_when_read_then_return_records(self) -> None:
        http_mocker = CustomHttpMocker()
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
