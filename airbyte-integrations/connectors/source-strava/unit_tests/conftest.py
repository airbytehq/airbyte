#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture
def start_date():
    return "2016-01-01T00:00:00"


@fixture
def config():
    return {
        "client_id": "12345",
        "client_secret": "0000000000000000000000000000000000000000",
        "refresh_token": "0000000000000000000000000000000000000000",
        "athlete_id": 12345678,
        "start_date": "2016-01-01 00:00:00"
    }
