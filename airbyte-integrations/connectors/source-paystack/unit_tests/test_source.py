#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY, MagicMock

import pytest
import requests
from source_paystack.source import SourcePaystack


@pytest.mark.parametrize(
    ("items",),
    [([{"createdAt": "2022-07-01T00:00:00Z", "id": 12345}],), ([],)],  # single customer  #  no customers
)
def test_check_connection_success(mocker, requests_mock, items):
    source = SourcePaystack()
    logger_mock = MagicMock()
    config_mock = {"start_date": "2020-07-01T00:00:00Z", "secret_key": "sk_test_abc123"}
    requests_mock.get(
        "https://api.paystack.co/customer",
        json={
            "data": items,
            "meta": {"page": 1, "pageCount": 0},
        },
    )

    assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_check_connection_failure(mocker, requests_mock):
    source = SourcePaystack()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://api.paystack.co/customer", json={"status": False, "message": "Failed"})

    assert source.check_connection(logger_mock, config_mock) == (False, ANY)


def test_check_connection_error(mocker, requests_mock):
    source = SourcePaystack()
    logger_mock, config_mock = MagicMock(), MagicMock()
    requests_mock.get("https://api.paystack.co/customer", exc=requests.exceptions.ConnectTimeout)

    assert source.check_connection(logger_mock, config_mock) == (False, ANY)


def test_streams(mocker):
    source = SourcePaystack()
    streams = source.streams({"start_date": "2020-08-01", "secret_key": "sk_test_123456"})

    assert len(streams) == 8
