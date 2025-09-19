#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

import pytest
from source_pinterest.source import SourcePinterest

from airbyte_cdk.utils import AirbyteTracedException


def test_check_connection(requests_mock, test_config):
    requests_mock.get("https://api.pinterest.com/v5/boards", status_code=200)
    source = SourcePinterest(None, test_config, None)
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (True, None)


def test_check_wrong_date_connection(wrong_date_config):
    source = SourcePinterest(None, wrong_date_config, None)
    logger_mock = MagicMock()
    status_ok, error = source.check_connection(logger_mock, wrong_date_config)
    assert not status_ok
    assert error == "Encountered an error while discovering streams. Error: time data 'wrong_date_format' does not match format '%Y-%m-%d'"


def test_check_connection_expired_token(requests_mock, test_config):
    requests_mock.post("https://api.pinterest.com/v5/oauth/token", status_code=401)
    source = SourcePinterest(None, test_config, None)
    logger_mock = MagicMock()
    assert source.check_connection(logger_mock, test_config) == (
        False,
        "Encountered an error while checking availability of stream boards. Error: 401 Client Error: None for url: https://api.pinterest.com/v5/oauth/token",
    )


def test_get_authenticator(test_config):
    source = SourcePinterest(None, test_config, None)
    auth = source.get_authenticator(test_config)
    expected = test_config.get("refresh_token")
    assert auth._refresh_token == expected


def test_invalid_account_id(wrong_account_id_config):
    source = SourcePinterest(None, wrong_account_id_config, None)
    logger_mock = MagicMock()

    with patch("source_pinterest.source.AdAccountValidationStream") as MockStream:
        instance = MockStream.return_value
        instance.read_records.return_value = []

        status_ok, error = source.check_connection(logger_mock, wrong_account_id_config)

        assert not status_ok
        assert error == f"Encountered an error while discovering streams. Error: The provided ad_account_id does not exist."
