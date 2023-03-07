#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import patch

import pytest
from requests.exceptions import HTTPError
from source_recharge.api import Shop
from source_recharge.source import RechargeTokenAuthenticator, SourceRecharge


# config
@pytest.fixture(name="config")
def config():
    return {
        "authenticator": None,
        "access_token": "access_token",
        "start_date": "2021-08-15T00:00:00Z",
    }


# logger
@pytest.fixture(name="logger_mock")
def logger_mock_fixture():
    return patch("source_recharge.source.AirbyteLogger")


def test_get_auth_header(config):
    expected = {"X-Recharge-Access-Token": config.get("access_token")}
    actual = RechargeTokenAuthenticator(token=config["access_token"]).get_auth_header()
    assert actual == expected


@pytest.mark.parametrize(
    "patch, expected",
    [
        (
            patch.object(Shop, "read_records", return_value=[{"shop": {"id": 123}}]),
            (True, None),
        ),
        (
            patch.object(Shop, "read_records", side_effect=HTTPError(403)),
            (False, "Unable to connect to Recharge API with the provided credentials - HTTPError(403)"),
        ),
    ],
    ids=["success", "fail"],
)
def test_check_connection(logger_mock, config, patch, expected):
    with patch:
        result = SourceRecharge().check_connection(logger_mock, config=config)
        assert result == expected


def test_streams(config):
    streams = SourceRecharge().streams(config)
    assert len(streams) == 11
