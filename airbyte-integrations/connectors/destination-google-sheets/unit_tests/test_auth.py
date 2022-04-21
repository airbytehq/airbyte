#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from destination_google_sheets.auth import GoogleSheetsAuth

TEST_CONFIG: dict = {
    "spreadsheet_id": "URL",
    "credentials": {"auth_type": "Client", "client_id": "CLIENT_ID", "client_secret": "CLIENT_SECRET", "refresh_token": "REFRESH_TOKEN"},
}


def test_get_credentials(config: dict = TEST_CONFIG):
    credentials = GoogleSheetsAuth.get_credentials(config)
    assert credentials.get("auth_type") == "Client"


def test_get_authenticated_google_credentials(config: dict = TEST_CONFIG):
    config_creds = GoogleSheetsAuth.get_credentials(config)
    authenticated_creds = GoogleSheetsAuth.get_authenticated_google_credentials(config_creds)
    # if the authentication is successful we will have `token_uri` and `expiry` properties inside.
    for i in ["token_uri", "expiry"]:
        assert i in authenticated_creds.to_json()
