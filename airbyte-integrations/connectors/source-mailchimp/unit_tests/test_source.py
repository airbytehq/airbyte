#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_mailchimp.source import MailChimpAuthenticator, SourceMailchimp

logger = logging.getLogger("airbyte")


def test_check_connection_ok(requests_mock, config, data_center):
    responses = [
        {"json": {"health_status": "Everything's Chimpy!"}},
    ]
    requests_mock.register_uri("GET", f"https://{data_center}.api.mailchimp.com/3.0/ping", responses)
    ok, error_msg = SourceMailchimp().check_connection(logger, config=config)

    assert ok
    assert not error_msg


@pytest.mark.parametrize(
    "response, expected_message",
    [
        (
            {
                "json": {
                    "title": "API Key Invalid",
                    "details": "Your API key may be invalid, or you've attempted to access the wrong datacenter.",
                }
            },
            "Encountered an error while connecting to Mailchimp. Type: API Key Invalid. Details: Your API key may be invalid, or you've attempted to access the wrong datacenter.",
        ),
        (
            {"json": {"title": "Forbidden", "details": "You don't have permission to access this resource."}},
            "Encountered an error while connecting to Mailchimp. Type: Forbidden. Details: You don't have permission to access this resource.",
        ),
        (
            {"json": {}},
            "Encountered an error while connecting to Mailchimp. Type: Unknown Error. Details: An unknown error occurred. Please verify your credentials and try again.",
        ),
    ],
    ids=["API Key Invalid", "Forbidden", "Unknown Error"],
)
def test_check_connection_error(requests_mock, config, data_center, response, expected_message):
    requests_mock.register_uri("GET", f"https://{data_center}.api.mailchimp.com/3.0/ping", json=response["json"])
    ok, error_msg = SourceMailchimp().check_connection(logger, config=config)

    assert not ok
    assert error_msg == expected_message


def test_get_oauth_data_center_ok(requests_mock, access_token, data_center):
    responses = [
        {"json": {"dc": data_center}, "status_code": 200},
    ]
    requests_mock.register_uri("GET", "https://login.mailchimp.com/oauth2/metadata", responses)
    assert MailChimpAuthenticator().get_oauth_data_center(access_token) == data_center


def test_get_oauth_data_center_exception(requests_mock, access_token):
    responses = [
        {"json": {}, "status_code": 200},
        {"json": {"error": "invalid_token"}, "status_code": 200},
        {"status_code": 403},
    ]
    requests_mock.register_uri("GET", "https://login.mailchimp.com/oauth2/metadata", responses)
    with pytest.raises(Exception):
        MailChimpAuthenticator().get_oauth_data_center(access_token)


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


@pytest.mark.parametrize(
    "config, expected_return",
    [
        ({}, None),
        ({"start_date": "2021-01-01T00:00:00.000Z"}, None),
        ({"start_date": "2021-99-99T79:89:99.123Z"}, "The provided start date is not a valid date. Please check the date you input and try again."),
        ({"start_date": "2021-01-01T00:00:00.000"}, "Please check the format of the start date against the pattern descriptor."),
        ({"start_date": "2025-01-25T00:00:00.000Z"}, "The start date cannot be greater than the current date."),
    ],
    ids=[
        "No start date",
        "Valid start date",
        "Invalid start date",
        "Invalid format",
        "Future start date",
    ]
)
def test_validate_start_date(config, expected_return):
    source = SourceMailchimp()
    result = source._validate_start_date(config)
    assert result == expected_return


def test_streams_count(config):
    streams = SourceMailchimp().streams(config)
    assert len(streams) == 12
