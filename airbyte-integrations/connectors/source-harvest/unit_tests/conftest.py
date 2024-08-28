#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pendulum import parse
from pytest import fixture


@fixture(name="config")
def config_fixture(requests_mock):
    url = "https://id.getharvest.com/api/v2/oauth2/token"
    requests_mock.get(url, json={})
    config = {"account_id": "ID", "replication_start_date": "2021-01-01T21:20:07Z", "credentials": {"auth_type": "Token", "api_token": "TOKEN"}}
    return config


@fixture(name="replication_start_date")
def replication_start_date_fixture(config):
    return parse(config["replication_start_date"])


@fixture(name="from_date")
def from_date_fixture(replication_start_date):
    return replication_start_date.date()


@fixture(name="mock_stream")
def mock_stream_fixture(requests_mock):
    def _mock_stream(path, response=None):
        if response is None:
            response = {}

        url = f"https://api.harvestapp.com/v2/{path}"
        requests_mock.get(url, json=response)

    return _mock_stream
