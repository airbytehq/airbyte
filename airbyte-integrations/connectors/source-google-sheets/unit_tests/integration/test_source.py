import json
import re
from copy import deepcopy
import pytest
from typing import Tuple, Any, Dict, List
from unittest import TestCase
from unittest.mock import Mock, patch

from airbyte_cdk.models import Status
from airbyte_cdk.test.catalog_builder import CatalogBuilder, ConfiguredAirbyteStreamBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from .google_credentials import service_account_info
from google.auth.credentials import AnonymousCredentials
from source_google_sheets import SourceGoogleSheets

from airbyte_cdk.test.mock_http.response_builder import (
    find_template,
)

_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"

_CONFIG = {
  "spreadsheet_id": _SPREADSHEET_ID,
  "credentials": {
    "auth_type": "Service",
    "service_account_info": service_account_info,
  }
}

class SheetBuilder:

    @classmethod
    def empty(cls, title: str) -> "SheetBuilder":
        builder = SheetBuilder(title)
        return builder

    def __init__(self, title: str) -> None:
        self._sheet = {
            "properties": {
                "title": title,
                "gridProperties": {
                    "rowCount": 0
                },
                "sheetType": "GRID",
            }
        }

    def with_records(self, records: List[Dict[str, str]]) -> "SheetBuilder":
        fields = list(records[0].keys())
        fields.sort()

        rows = []
        rows.append(fields)
        for record in records:
            if record.keys() != set(fields):
                raise ValueError("Records do not have all the same columns")
            rows.append([record[key] for key in sorted(record.keys())])

        self.with_data(rows)
        return self

    def with_data(self, rows: List[List[str]]) -> "SheetBuilder":
        self._sheet["data"] = [{"rowData": [self._create_row(row) for row in rows]}]
        self._sheet["properties"]["gridProperties"]["rowCount"] = len(rows)
        return self

    def _create_row(self, values: List[str]) -> Dict[str, List[Dict[str, str]]]:
        return {"values": [{"formattedValue": value} for value in values]}

    def with_properties(self, properties: Dict[str, str]) -> "SheetBuilder":
        self._sheet["properties"] = properties
        return self

    def with_sheet_type(self, sheet_type: str) -> "SheetBuilder":
        self._sheet["properties"]["sheetType"] = sheet_type
        return self

    def build(self) -> Any:
        return self._sheet


class SpreadsheetBuilder:
    @classmethod
    def from_list_of_records(cls, spreadsheet_id: str, sheet_title: str, records: List[Dict[str, str]]) -> "SpreadsheetBuilder":
        builder = SpreadsheetBuilder(spreadsheet_id)
        builder.with_sheet(SheetBuilder(sheet_title).with_records(records))
        return builder

    def __init__(self, spreadsheet_id: str) -> None:
        self._spreadsheet = {
            "spreadsheetId": spreadsheet_id,
            "sheets": [],
        }

    def with_sheet(self, sheet: SheetBuilder) -> "SpreadsheetBuilder":
        self._spreadsheet["sheets"].append(sheet.build())
        return self

    def build(self) -> Any:
        return self._spreadsheet

@pytest.fixture
def mock_google_credentials():
    with patch("google.oauth2.service_account.Credentials.from_service_account_info", return_value=AnonymousCredentials()):
        with patch("google.oauth2.credentials.Credentials.from_authorized_user_info", return_value=AnonymousCredentials()):
            yield
from httplib2 import Response

def mock_request(uri, method="GET", body=None, headers=None, **kwargs):
    """
    Mock behavior of httplib2.Http.request based on the URI.
    """
    base_sheets_response = find_template("base_sheets_response", __file__)
    # 'https://sheets.googleapis.com/v4/spreadsheets/12MI0w4JwM8f1uwC0qhDJedh2zwKSK4pNJcMl2quQykg?includeGridData=false&alt=json'
    if uri == f"https://sheets.googleapis.com/v4/spreadsheets/{_SPREADSHEET_ID}?includeGridData=false&alt=json":
        return (
            Response({"status": "200"}),  # Response headers
            json.dumps(base_sheets_response).encode("utf-8"),  # Response content
        )
    elif uri == "https://oauth2.googleapis.com/token":
        return (
            {"status": "200"},  # Response headers
            b'{"access_token":"ya29.c.--access-token","expires_in":3599,"token_type":"Bearer"}',  # Response content
        )
    elif uri == "https://example.com/api/resource3":
        return (
            {"status": "500"},  # Response headers
            b'{"error": "internal server error"}',  # Response content
        )
    else:
        return (
            {"status": "400"},
            b'{"error": "bad request"}',
        )

class GoogleSheetSourceTest(TestCase):
    def setUp(self) -> None:
        # self._authentication_patch, self._authentication_mock = self._patch("google.oauth2.service_account.Credentials")
        # self._discovery_build_patch, self._discovery_build_mock = self._patch("googleapiclient.discovery.build")

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

        # self._discovery_build_mock.side_effect = discovery_build
        self._config = deepcopy(_CONFIG)

        self._source = SourceGoogleSheets()

    def _patch(self, class_name: str) -> Tuple[Any, Mock]:
        patcher = patch(class_name)
        return patcher, patcher.start()

    def tearDown(self) -> None:
        # self._authentication_patch.stop()
        # self._discovery_build_patch.stop()
        pass
    def _mock_spreadsheet(self, spreadsheet) -> None:
        def _get_response_based_on_args(*args, **kwargs):
            get_mock = Mock()
            return_value = deepcopy(spreadsheet)
            if "ranges" in kwargs:
                # this is for schema discovery so only return the first row
                if not return_value["sheets"][0]["data"]:
                    return_value["sheets"][0]["data"][0]["rowData"] = [{"columnMetadata": [], "rowMetatada": []}]  # there should be data in "rowMetadata" and "columnMetadata" here but it is not useful for the tests
                return_value["sheets"][0]["data"][0]["rowData"] = return_value["sheets"][0]["data"][0]["rowData"][:1]

            get_mock.execute.return_value = return_value
            return get_mock

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

        self._sheets_client.values.return_value.batchGet.side_effect = _batch_get_response

    # @patch("httplib2.Http.request", side_effect=mock_request)
    @pytest.mark.usefixtures("mock_google_credentials")
    # def test_given_spreadsheet_when_check_then_status_is_succeeded(self, mock_http_request) -> None:
    def test_given_spreadsheet_when_check_then_status_is_succeeded(self) -> None:
        def custom_mock_request(uri, method="GET", body=None, headers=None, **kwargs):
            return mock_request(uri, method, body, headers, **kwargs)

        # Use patch as a context manager
        with patch("httplib2.Http.request", side_effect=custom_mock_request):
            self._mock_spreadsheet(
                {
                    "spreadsheetId": _SPREADSHEET_ID,
                    "sheets": [
                    ],
                }
            )
            connection_status = self._source.check(Mock(), self._config)
            assert connection_status.status == Status.SUCCEEDED

    def test_given_authentication_error_when_check_then_status_is_failed(self) -> None:
        # self._authentication_mock.from_service_account_info.side_effect = ValueError
        connection_status = self._source.check(Mock(), self._config)
        assert connection_status.status == Status.FAILED

    def test_given_grid_sheet_type_with_at_least_one_row_when_discover_then_return_stream(self) -> None:
        self._mock_spreadsheet(SpreadsheetBuilder(_SPREADSHEET_ID).with_sheet(SheetBuilder(_STREAM_NAME).with_sheet_type("GRID").with_data([["header1", "header2"]])).build())

        discovered_catalog = self._source.discover(Mock(), self._config)

        assert len(discovered_catalog.streams) == 1
        assert len(discovered_catalog.streams[0].json_schema["properties"]) == 2

    def test_given_grid_sheet_type_without_rows_when_discover_then_ignore_stream(self) -> None:
        self._mock_spreadsheet(SpreadsheetBuilder(_SPREADSHEET_ID).with_sheet(SheetBuilder.empty(_STREAM_NAME).with_sheet_type("GRID")).build())
        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 0

    def test_given_not_grid_sheet_type_when_discover_then_ignore_stream(self) -> None:
        self._mock_spreadsheet(SpreadsheetBuilder(_SPREADSHEET_ID).with_sheet(SheetBuilder(_STREAM_NAME).with_sheet_type("potato").with_data([["header1", "header2"]])).build())
        discovered_catalog = self._source.discover(Mock(), self._config)
        assert len(discovered_catalog.streams) == 0

    def test_when_read_then_return_records(self) -> None:
        self._mock_spreadsheet(SpreadsheetBuilder.from_list_of_records(_SPREADSHEET_ID, _STREAM_NAME, [{"header_1": "value_11", "header_2": "value_12"}, {"header_1": "value_21", "header_2": "value_22"}]).build())
        output = read(self._source, self._config, CatalogBuilder().with_stream(ConfiguredAirbyteStreamBuilder().with_name(_STREAM_NAME).with_json_schema({"properties": {"header_1": { "type": ["null", "string"] }, "header_2": { "type": ["null", "string"] }}})).build())
        assert len(output.records) == 2
