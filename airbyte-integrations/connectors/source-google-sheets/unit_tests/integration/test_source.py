# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
import re
from copy import deepcopy
from typing import Any, Dict, List, Tuple
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
from .sheet_builder import SheetBuilder
from .spreadsheet_builder import SpreadsheetBuilder

_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"

_CONFIG = {
  "spreadsheet_id": _SPREADSHEET_ID,
  "credentials": service_account_credentials
}

MOCK_GOOGLE_OBJECTS = False

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
        if MOCK_GOOGLE_OBJECTS:
            self._authentication_patch, self._authentication_mock = self._patch("google.oauth2.service_account.Credentials")
            self._discovery_build_patch, self._discovery_build_mock = self._patch("googleapiclient.discovery.build")

            self._sheets_client = Mock()
        def discovery_build(*args, **kwargs) -> Any:
            match args[0]:
                case "sheets":
                    sheet_discovery_build = Mock()
                    sheet_discovery_build.spreadsheets.return_value = self._sheets_client
                    return sheet_discovery_build
                case "drive":
                    return Mock()
                case _:
                    raise ValueError("Unknown service name")
        if MOCK_GOOGLE_OBJECTS:
            self._discovery_build_mock.side_effect = discovery_build

        self._config = deepcopy(_CONFIG)
        self._source = SourceGoogleSheets()

    def _patch(self, class_name: str) -> Tuple[Any, Mock]:
        patcher = patch(class_name)
        return patcher, patcher.start()

    def tearDown(self) -> None:
        if MOCK_GOOGLE_OBJECTS:
            self._authentication_patch.stop()
            self._discovery_build_patch.stop()

    def _mock_spreadsheet(self, spreadsheet) -> None:
        def _get_response_based_on_args(*args, **kwargs):
            get_mock = Mock()
            return_value = deepcopy(spreadsheet)
            if "ranges" in kwargs:
                sheet_has_data = "data" in return_value["sheets"][0]
                if sheet_has_data:
                    # this is for schema discovery so only return the first row
                    if not return_value["sheets"][0]["data"]:
                        return_value["sheets"][0]["data"][0]["rowData"] = [{"columnMetadata": [], "rowMetatada": []}]  # there should be data in "rowMetadata" and "columnMetadata" here but it is not useful for the tests
                    return_value["sheets"][0]["data"][0]["rowData"] = return_value["sheets"][0]["data"][0]["rowData"][:1]

            get_mock.execute.return_value = return_value
            return get_mock

        if MOCK_GOOGLE_OBJECTS:
            self._sheets_client.get.side_effect = _get_response_based_on_args

        def _batch_get_response(*args, **kwargs):
            # self.client.values().batchGet(ranges=range, **kwargs).execute()
            range_search = re.search(r".*!([0-9]*):([0-9]*)", kwargs["ranges"])
            range_lower_index = int(range_search.group(1)) - 1
            range_upper_index = int(range_search.group(2)) - 1
            batch_get_mock = Mock()
            for sheet in spreadsheet["sheets"]:
                if sheet["properties"]["title"] in kwargs["ranges"]:
                    batch_get_mock.execute.return_value = {
                        "spreadsheetId": spreadsheet["spreadsheetId"],
                        "valueRanges": [{"values": [list(map(lambda row: row["formattedValue"], _range["values"])) for _range in sheet["data"][0]["rowData"][range_lower_index:range_upper_index]]}]
                    }
                    break

            return batch_get_mock

        if MOCK_GOOGLE_OBJECTS:
            self._sheets_client.values.return_value.batchGet.side_effect = _batch_get_response

    @staticmethod
    def _get_discovery_ranges_response(spreadsheet):
        # this is for schema discovery so only return the first row
        return_value = deepcopy(spreadsheet)
        sheet_has_data = "data" in return_value["sheets"][0]
        if sheet_has_data:
            if not return_value["sheets"][0]["data"]:
                return_value["sheets"][0]["data"][0]["rowData"] = [{"columnMetadata": [],
                                                                    "rowMetatada": []}]  # there should be data in "rowMetadata" and "columnMetadata" here but it is not useful for the tests
            return_value["sheets"][0]["data"][0]["rowData"] = return_value["sheets"][0]["data"][0]["rowData"][:1]

        return return_value

    @staticmethod
    def _batch_get_response(spreadsheet, ranges=""):
        range_search = re.search(r".*!([0-9]*):([0-9]*)", ranges)
        range_lower_index = int(range_search.group(1)) - 1
        range_upper_index = int(range_search.group(2)) - 1
        return_value = deepcopy(spreadsheet)
        for sheet in spreadsheet["sheets"]:
            if sheet["properties"]["title"] in ranges:
                return_value = {
                    "spreadsheetId": spreadsheet["spreadsheetId"],
                    "valueRanges": [{"values": [list(map(lambda row: row["formattedValue"], _range["values"])) for _range in
                                                sheet["data"][0]["rowData"][range_lower_index:range_upper_index]]}]
                }
                break

        return return_value

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_spreadsheet_when_check_then_status_is_succeeded(self) -> None:
        http_mocker = CustomHttpMocker()
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(find_template("check_response", __file__)), 200)
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
        current_spreadsheet = SpreadsheetBuilder(_SPREADSHEET_ID).with_sheet(
            SheetBuilder(_STREAM_NAME).with_sheet_type("GRID").with_data([["header1", "header2"]])).build()

        # spreadsheet_metadata request
        http_mocker = CustomHttpMocker()
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(current_spreadsheet), 200)
        )

        # discovery response
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(f"{current_spreadsheet['sheets'][0]['properties']['title']}!1:1").with_alt("json").build(),
            HttpResponse(json.dumps(self._get_discovery_ranges_response(current_spreadsheet)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):

            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 1
            assert len(discovered_catalog.streams[0].json_schema["properties"]) == 2

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self) -> None:
        # todo: are we reproducing correct response data for this? maybe is worth to set and empty sheet and catch response
        current_spreadsheet = SpreadsheetBuilder(_SPREADSHEET_ID).with_sheet(SheetBuilder.empty(_STREAM_NAME).with_sheet_type("GRID")).build()
        http_mocker = CustomHttpMocker()
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(current_spreadsheet), 200)
        )

        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(f"{current_spreadsheet['sheets'][0]['properties']['title']}!1:1").with_alt("json").build(),
            HttpResponse(json.dumps(self._get_discovery_ranges_response(current_spreadsheet)), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 0

    @pytest.mark.usefixtures("mock_google_credentials")
    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self) -> None:
        current_spreadsheet = SpreadsheetBuilder(_SPREADSHEET_ID).with_sheet(SheetBuilder(_STREAM_NAME).with_sheet_type("potato").with_data([["header1", "header2"]])).build()
        http_mocker = CustomHttpMocker()
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(current_spreadsheet), 200)
        )

        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            discovered_catalog = self._source.discover(Mock(), self._config)
            assert len(discovered_catalog.streams) == 0


    @pytest.mark.usefixtures("mock_google_credentials")
    def test_when_read_then_return_records(self) -> None:
        current_spreadsheet = SpreadsheetBuilder.from_list_of_records(_SPREADSHEET_ID, _STREAM_NAME, [{"header_1": "value_11", "header_2": "value_12"}, {"header_1": "value_21", "header_2": "value_22"}]).build()
        http_mocker = CustomHttpMocker()
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(False).with_alt("json").build(),
            HttpResponse(json.dumps(current_spreadsheet), 200)
        )

        # discovery response
        http_mocker.get(
            RequestBuilder().with_spreadsheet_id(_SPREADSHEET_ID).with_include_grid_data(True).with_ranges(
                f"{current_spreadsheet['sheets'][0]['properties']['title']}!1:1").with_alt("json").build(),

            HttpResponse(json.dumps(self._get_discovery_ranges_response(current_spreadsheet)), 200)
        )

        # batch response
        batch_request_ranges = f"{current_spreadsheet['sheets'][0]['properties']['title']}!2:202"
        http_mocker.get(
            RequestBuilder.get_account_endpoint().with_spreadsheet_id(_SPREADSHEET_ID).with_ranges(batch_request_ranges).with_major_dimension("ROWS").with_alt("json").build(),
            HttpResponse(json.dumps(self._batch_get_response(current_spreadsheet, batch_request_ranges)), 200)
        )
        with patch("httplib2.Http.request", side_effect=http_mocker.mock_request):
            output = read(self._source, self._config, CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build())
            assert len(output.records) == 2
