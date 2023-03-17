#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(name='config')
def config_fixture():
    return {
        "auth_token": "test_token",
        "counter_id": "00000000",
        "start_date": "2022-07-01",
        "end_date": "2022-07-02"
    }


@pytest.fixture(name='config_wrong_date')
def config_wrong_date_fixture():
    return {
        "auth_token": "test_token",
        "counter_id": "00000000",
        "start_date": "2022-07-02",
        "end_date": "2022-07-01"
    }
