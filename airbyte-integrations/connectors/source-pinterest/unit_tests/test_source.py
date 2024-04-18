#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
import responses
from airbyte_cdk.utils import AirbyteTracedException
from source_pinterest.source import SourcePinterest


def setup_responses():
    responses.add(
        responses.POST,
        "https://api.pinterest.com/v5/oauth/token",
        json={"access_token": "fake_access_token", "expires_in": 3600},
    )
    responses.add(
        responses.GET,
        "https://api.pinterest.com/v5/user_account",
        json={},
    )


@responses.activate
def test_check_connection(test_config):
    setup_responses()
    source = SourcePinterest()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


def test_check_wrong_date_connection(wrong_date_config):
    source = SourcePinterest()
    logger_mock = MagicMock()
    with pytest.raises(AirbyteTracedException) as e:
        source.check_connection(logger_mock, wrong_date_config)
    assert e.value.message == "Entered `Start Date` wrong_date_format does not match format YYYY-MM-DD"


@responses.activate
def test_check_connection_expired_token(test_config):
    responses.add(responses.POST, "https://api.pinterest.com/v5/oauth/token", status=401)
    source = SourcePinterest()
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (
        False,
        "Try to re-authenticate because current refresh token is not valid. "
        "401 Client Error: Unauthorized for url: https://api.pinterest.com/v5/oauth/token",
    )


def test_get_authenticator(test_config):
    source = SourcePinterest()
    auth = source.get_authenticator(test_config)
    expected = test_config.get("refresh_token")
    assert auth.refresh_token == expected
