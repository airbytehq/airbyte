#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(name="config")
def config_fixture(requests_mock):
    config = {"start_date": "2022-09-08", "base": "USD", "access_key": "KEY"}

    return config


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None, status_code=200):
        if response is None:
            response = {}

        url = f"https://api.apilayer.com/exchangerates_data/{path}"
        requests_mock.get(url, json=response, status_code=status_code)

    return _mock_stream
