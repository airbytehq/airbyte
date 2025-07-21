#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from conftest import get_source


def test_streams_config_based(config):
    streams = get_source(config).streams(config)
    assert len(streams) == 77


def test_source_check_connection_ok(config, logger_mock, mock_auth_token, mock_user_query, mock_account_query):
    source = get_source(config)
    assert source.check_connection(logger_mock, config=config) == (True, None)


def test_source_check_connection_ok_but_user_do_not_have_accounts(config, logger_mock, mock_auth_token, mock_user_query, requests_mock):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        status_code=200,
        json={"Accounts": []},
    )
    source = get_source(config)
    connected, reason = source.check_connection(logger_mock, config=config)
    assert connected is True


def test_source_check_connection_failed_invalid_creds(config, logger_mock, mock_auth_token, mock_user_query, requests_mock):
    requests_mock.post(
        "https://clientcenter.api.bingads.microsoft.com/CustomerManagement/v13/Accounts/Search",
        status_code=401,
        json={"error": "invalid credentials"},
    )
    source = get_source(config)
    connected, reason = source.check_connection(logger_mock, config=config)
    assert connected is False


def test_check_connection_with_accounts_names_config(
    config_with_account_names, logger_mock, mock_auth_token, mock_user_query, mock_account_query
):
    source = get_source(config_with_account_names)
    assert source.check_connection(logger_mock, config=config_with_account_names) == (True, None)
