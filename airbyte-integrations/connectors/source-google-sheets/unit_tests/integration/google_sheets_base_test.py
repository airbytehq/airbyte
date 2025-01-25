# Copyright (c) 2025 Airbyte, Inc., all rights reserved.


import json
from abc import ABC
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple, Union
from unittest import TestCase

from source_google_sheets.batch_size_manager import BatchSizeManager

from airbyte_cdk.models import (
    ConfiguredAirbyteCatalog,
)
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template

from .mock_credentials import AUTH_BODY, oauth_credentials, service_account_credentials
from .protocol_helpers import check_helper, discover_helper, read_helper
from .request_builder import AuthBuilder, RequestBuilder


_SPREADSHEET_ID = "a_spreadsheet_id"

_STREAM_NAME = "a_stream_name"

_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": oauth_credentials, "batch_size": 200}

_SERVICE_CONFIG = {"spreadsheet_id": _SPREADSHEET_ID, "credentials": service_account_credentials}


class GoogleSheetsBaseTest(TestCase, ABC):
    def setUp(self) -> None:
        self._config = deepcopy(_CONFIG)
        self._service_config = deepcopy(_SERVICE_CONFIG)
        BatchSizeManager.reset()

    @staticmethod
    def _check(config: Dict[str, Any], expecting_exception: bool = True) -> EntrypointOutput:
        return check_helper(config, stream_name=_STREAM_NAME, expecting_exception=expecting_exception)

    @staticmethod
    def _discover(config: Dict[str, Any], expecting_exception: bool = True) -> EntrypointOutput:
        return discover_helper(config, stream_name=_STREAM_NAME, expecting_exception=expecting_exception)

    @staticmethod
    def _read(config: Dict[str, Any], catalog: ConfiguredAirbyteCatalog, expecting_exception: bool = False) -> EntrypointOutput:
        return read_helper(config, catalog, expecting_exception=expecting_exception)

    @staticmethod
    def authorize(http_mocker: HttpMocker):
        # Authorization request with user credentials to "https://oauth2.googleapis.com" to obtain a token
        http_mocker.post(
            AuthBuilder.get_token_endpoint().with_body(AUTH_BODY).build(),
            HttpResponse(json.dumps(find_template("auth_response", __file__)), 200),
        )

    @staticmethod
    def get_spreadsheet_info_and_sheets(
        http_mocker: HttpMocker,
        streams_response_file: Optional[str] = None,
        meta_response_code: Optional[int] = 200,
        spreadsheet_id: Optional[str] = _SPREADSHEET_ID,
    ):
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
        GoogleSheetsBaseTest.authorize(http_mocker)
        if streams_response_file:
            http_mocker.get(
                RequestBuilder().with_spreadsheet_id(spreadsheet_id).with_include_grid_data(False).with_alt("json").build(),
                HttpResponse(json.dumps(find_template(streams_response_file, __file__)), meta_response_code),
            )

    @staticmethod
    def get_sheet_first_row(
        http_mocker: HttpMocker,
        headers_response_file: str,
        headers_response_code: int = 200,
        stream_name: Optional[str] = _STREAM_NAME,
        data_initial_range_response_file: Optional[str] = None,
        data_initial_response_code: Optional[int] = 200,
        spreadsheet_id: Optional[str] = _SPREADSHEET_ID,
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
            .with_spreadsheet_id(spreadsheet_id)
            .with_include_grid_data(True)
            .with_ranges(f"{stream_name}!1:1")
            .with_alt("json")
            .build(),
            HttpResponse(json.dumps(find_template(headers_response_file, __file__)), headers_response_code),
        )

    @staticmethod
    def get_stream_data(
        http_mocker: HttpMocker,
        data_response_file: Optional[str] = None,
        response_code: Optional[int] = 200,
        stream_name: Optional[str] = _STREAM_NAME,
        request_range: Tuple = (2, 202),
        spreadsheet_id: Optional[str] = _SPREADSHEET_ID,
        responses: Optional[Union[HttpResponse, List[HttpResponse]]] = None,
    ):
        """ "
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
            RequestBuilder.get_account_endpoint()
            .with_spreadsheet_id(spreadsheet_id)
            .with_ranges(batch_request_ranges)
            .with_major_dimension("ROWS")
            .with_alt("json")
            .build(),
            HttpResponse(json.dumps(find_template(data_response_file, __file__)), response_code) if data_response_file else responses,
        )
