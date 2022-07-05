#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import requests
from airbyte_cdk.logger import AirbyteLogger
from source_mailchimp.source import MailChimpAuthenticator, SourceMailchimp

logger = AirbyteLogger()


def test_check_connection_ok(requests_mock, config, data_center):
    responses = [
        {"json": [], "status_code": 200},
    ]
    requests_mock.register_uri("GET", f"https://{data_center}.api.mailchimp.com/3.0/ping", responses)
    ok, error_msg = SourceMailchimp().check_connection(logger, config=config)

    assert ok
    assert not error_msg


def test_check_connection_error(requests_mock, config, data_center):
    requests_mock.register_uri("GET", f"https://{data_center}.api.mailchimp.com/3.0/ping", body=requests.ConnectionError())
    ok, error_msg = SourceMailchimp().check_connection(logger, config=config)

    assert not ok
    assert error_msg


def test_get_server_prefix_ok(requests_mock, access_token, data_center):
    responses = [
        {"json": {"dc": data_center}, "status_code": 200},
    ]
    requests_mock.register_uri("GET", "https://login.mailchimp.com/oauth2/metadata", responses)
    assert MailChimpAuthenticator().get_server_prefix(access_token) == data_center


def test_get_server_prefix_exception(requests_mock, access_token, data_center):
    responses = [
        {"json": {}, "status_code": 200},
        {"status_code": 403},
    ]
    requests_mock.register_uri("GET", "https://login.mailchimp.com/oauth2/metadata", responses)
    with pytest.raises(Exception):
        MailChimpAuthenticator().get_server_prefix(access_token)


def test_oauth_config(requests_mock, oauth_config, data_center):
    responses = [
        {"json": {"dc": data_center}, "status_code": 200},
    ]
    requests_mock.register_uri("GET", "https://login.mailchimp.com/oauth2/metadata", responses)
    assert MailChimpAuthenticator().get_auth(oauth_config)


def test_apikey_config(apikey_config):
    assert MailChimpAuthenticator().get_auth(apikey_config)


def test_wrong_config(wrong_config):
    with pytest.raises(Exception):
        MailChimpAuthenticator().get_auth(wrong_config)


def test_streams_count(config):
    streams = SourceMailchimp().streams(config)
    assert len(streams) == 3
