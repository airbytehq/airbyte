#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest

replication_start_date = "2017-01-25T00:00:00Z"


@pytest.fixture(name="config_oauth")
def config_oauth():
    return {
        "divisions": [123],
        "credentials": {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
            "token_expiry_date": "2345-03-07T14:14:49.775368+00:00",
        },
    }


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock
