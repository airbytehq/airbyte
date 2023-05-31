#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from pytest import fixture


@fixture(name="config")
def config_fixture(requests_mock):
    config = {"start_date": "2022-11-13", "base": "USD", "app_id": "KEY"}

    return config


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None, status_code=200):
        if response is None:
            response = {}

        url = f"https://openexchangerates.org/api/{path}.json"
        requests_mock.get(url, json=response, status_code=status_code)

    return _mock_stream
