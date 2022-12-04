#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_google_sheets.client import GoogleSheetsClient
from integration_tests.test_helpers import TEST_CONFIG
from pygsheets.client import Client as pygsheets_client

# ----- PREPARE ENV -----

# path to configured_catalog json file
TEST_CATALOG_PATH: str = "integration_tests/test_data/test_catalog.json"
# client instance
TEST_CLIENT: pygsheets_client = GoogleSheetsClient(TEST_CONFIG)
# authorized client
AUTHORIZED_CLIENT: pygsheets_client = TEST_CLIENT.authorize()


# ----- BEGIN TESTS -----


def test_client():
    client = TEST_CLIENT.authorize()
    assert isinstance(client, pygsheets_client)
    # if the authentication is successful we will have `token_uri` and `expiry` properties inside.
    for i in ["token_uri", "expiry"]:
        assert i in client.oauth.to_json()


@pytest.mark.parametrize(
    "property, expected_retries",
    [
        (TEST_CLIENT.retries, 100),
        (AUTHORIZED_CLIENT.drive.retries, 100),
        (AUTHORIZED_CLIENT.sheet.retries, 100),
    ],
    ids=["client_main_retries", "client_drive_retries", "client_sheet_retries"],
)
def test_max_retries_are_set(property, expected_retries):
    assert property == expected_retries


# ----- END TESTS -----
