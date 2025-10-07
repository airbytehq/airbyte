#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import Status
from unit_tests.conftest import get_source


def test_check_connection(requests_mock, test_config):
    requests_mock.get("https://api.pinterest.com/v5/boards", status_code=200)
    source = get_source(test_config)
    logger_mock = MagicMock()
    check_result = source.check(logger_mock, test_config)
    status_ok, error = check_result.status, check_result.message
    assert status_ok == Status.SUCCEEDED


def test_check_wrong_date_connection(wrong_date_config):
    source = get_source(wrong_date_config)
    logger_mock = MagicMock()
    check_result = source.check(logger_mock, wrong_date_config)
    status_ok, error = check_result.status, check_result.message
    assert status_ok == Status.FAILED
    assert (
        error == "\"Encountered an error while discovering streams. Error: time data 'wrong_date_format' does not match format '%Y-%m-%d'\""
    )


def test_check_connection_expired_token(requests_mock, test_config):
    requests_mock.post("https://api.pinterest.com/v5/oauth/token", status_code=401)
    source = get_source(test_config)
    logger_mock = MagicMock()
    check_result = source.check(logger_mock, test_config)
    status_ok, error = check_result.status, check_result.message
    assert status_ok == Status.FAILED
    assert (
        error
        == f"'Encountered an error while checking availability of stream boards. Error: 401 Client Error: None for url: https://api.pinterest.com/v5/oauth/token'"
    )


def test_invalid_account_id(wrong_account_id_config):
    source = get_source(wrong_account_id_config)
    logger_mock = MagicMock()

    check_result = source.check(logger_mock, wrong_account_id_config)
    status_ok, error = check_result.status, check_result.message

    assert status_ok == Status.FAILED
    assert (
        error
        == "'Encountered an error while checking availability of stream boards. Error: No mock address: GET https://api.pinterest.com/v5/boards?ad_account_id=invalid_account'"
    )
