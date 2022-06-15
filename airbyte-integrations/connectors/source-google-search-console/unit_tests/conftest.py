#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture(requests_mock):
    url = "https://oauth2.googleapis.com/token"
    requests_mock.post(url, json={"access_token": "token", "expires_in": 10})
    config = {
        "site_urls": ["https://example.com"],
        "start_date": "start_date",
        "end_date": "end_date",
        "authorization": {
            "auth_type": "Client",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
        },
    }

    return config
