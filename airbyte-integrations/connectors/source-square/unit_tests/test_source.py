#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
import requests_mock
from source_square.source import SourceSquare

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
CURSOR_GRANULARITY = "PT0.000001S"


@pytest.fixture
def req_mock():
    with requests_mock.Mocker() as mock:
        yield mock


def test_source_wrong_credentials():
    source = SourceSquare()
    config = {
        "credentials": {"auth_type": "Apikey", "api_key": "bla"},
        "is_sandbox": True,
        "start_date": "2021-06-01",
        "include_deleted_objects": False,
    }

    with pytest.raises(ValueError) as key_error:
        status, error = source.check_connection(logger=logging.getLogger("airbyte"), config=config)
    assert str(key_error.value) == "The authenticator `Apikey` is not found."
