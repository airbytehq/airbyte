# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

import pytest


@pytest.fixture(autouse=True)
def patch_sleep(mocker):
    mocker.patch("time.sleep")


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": 123,
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00",
        "end_date": "2020-10-10T00:00:00",
    }
    return config

