#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Mapping

from airbyte_cdk.models import ConfiguredAirbyteCatalog
from destination_google_sheets.client import GoogleSheetsClient
from destination_google_sheets.helpers import ConnectionTest, get_spreadsheet_id, get_streams_from_catalog
from destination_google_sheets.spreadsheet import GoogleSheets
from pygsheets.client import Client as pygsheets_client

# ----- PREPARE ENV -----


def get_config(config_path: str = "secrets/config_oauth.json") -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open(config_path, "r") as f:
        return json.loads(f.read())


# using real config from secrets/config_oauth.json
TEST_CONFIG: dict = get_config()
# client instance
TEST_CLIENT: pygsheets_client = GoogleSheetsClient(TEST_CONFIG).authorize()
# get test spreadsheet_id
TEST_SPREADSHEET_ID: str = get_spreadsheet_id(TEST_CONFIG.get("spreadsheet_id"))
# define test Spreadsheet class
TEST_SPREADSHEET: GoogleSheets = GoogleSheets(TEST_CLIENT, TEST_SPREADSHEET_ID)
# define test stream
TEST_STREAM: str = "test_stream"
# path to configured_catalog json file
TEST_CATALOG_PATH: str = "integration_tests/configured_catalog.json"
# reading prepared catalog with streams
TEST_CATALOG: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog.parse_file(TEST_CATALOG_PATH)


# ----- BEGIN TESTS -----


def test_connection_test_write():
    check_result = ConnectionTest(TEST_SPREADSHEET).perform_connection_test()
    assert check_result is True


def test_get_spreadsheet_id(config: dict = TEST_CONFIG):
    expected = "1Zi1addRSXvXNf3-fxMhEGlshsgTl6tg76fvzaGjuy50"
    spreadsheet_id = get_spreadsheet_id(config.get("spreadsheet_id"))
    assert spreadsheet_id == expected


def test_get_streams_from_catalog():
    limit_count_streams = 2
    actual = get_streams_from_catalog(TEST_CATALOG, limit_count_streams)
    assert len(actual) == limit_count_streams
