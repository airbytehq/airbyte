#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_google_sheets.client import GoogleSheetsClient
from integration_tests.test_helpers import TEST_CONFIG, TEST_SERVICE_CONFIG
from pygsheets.client import Client as pygsheets_client


# ----- PREPARE ENV -----

# path to configured_catalog json file
TEST_CATALOG_PATH: str = "integration_tests/test_data/test_catalog.json"
# client instance
TEST_CLIENT: pygsheets_client = GoogleSheetsClient(TEST_CONFIG)
# authorized client
AUTHORIZED_CLIENT: pygsheets_client = TEST_CLIENT.authorize()
# service account client - if using service account tests
TEST_SERVICE_CLIENT = GoogleSheetsClient(TEST_SERVICE_CONFIG)
AUTHORIZED_SERVICE_CLIENT = TEST_SERVICE_CLIENT.authorize()

# ----- BEGIN TESTS -----


def test_oauth_client():
    client = TEST_CLIENT.authorize()
    assert isinstance(client, pygsheets_client)
    # if the authentication is successful we will have `token_uri` and `expiry` properties inside.
    for i in ["token_uri", "expiry"]:
        assert i in client.oauth.to_json()


def test_service_account_client():
    client = TEST_SERVICE_CLIENT.authorize()
    assert isinstance(client, pygsheets_client)
    # Service account client has different structure than OAuth client
    assert hasattr(client, "drive")
    assert hasattr(client, "sheet")


@pytest.mark.parametrize(
    "client_instance, property, expected_retries",
    [
        (TEST_CLIENT, "retries", 100),
        (AUTHORIZED_CLIENT, "drive.retries", 100),
        (AUTHORIZED_CLIENT, "sheet.retries", 100),
            (TEST_SERVICE_CLIENT, "retries", 100),
            (AUTHORIZED_SERVICE_CLIENT, "drive.retries", 100),
            (AUTHORIZED_SERVICE_CLIENT, "sheet.retries", 100),
    ],
    ids=[
        "client_main_retries",
        "client_drive_retries",
        "client_sheet_retries",
            "service_client_main_retries",
            "service_client_drive_retries",
            "service_client_sheet_retries",
        ]
)
def test_max_retries_are_set(client_instance, property, expected_retries):
    if "." in property:
        parts = property.split(".")
        actual_property = getattr(client_instance, parts[0])
        for part in parts[1:]:
            actual_property = getattr(actual_property, part)
        assert actual_property == expected_retries
    else:
        assert getattr(client_instance, property) == expected_retries


# ----- END TESTS -----
