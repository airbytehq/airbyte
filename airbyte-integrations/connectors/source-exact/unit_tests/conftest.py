#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest

replication_start_date = "2017-01-25T00:00:00Z"


@pytest.fixture(name="config_oauth")
def config_oauth():
    return {
        "division": 123,
        "credentials": {
            "client_id": "client_id",
            "client_secret": "client_secret",
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        },
    }


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock
