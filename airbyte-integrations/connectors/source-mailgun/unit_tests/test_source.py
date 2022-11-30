#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
import requests as requests
import responses
from source_mailgun.source import SourceMailgun

from . import TEST_CONFIG


@pytest.fixture
def check_connection_url():
    return "https://api.mailgun.net/v3/domains"


@pytest.fixture
def source_mailgun(test_config):
    source = SourceMailgun()
    yield source
    del source


@pytest.mark.parametrize(
    "config",
    [
        TEST_CONFIG,
        dict(**TEST_CONFIG, **{"start_date": "2021-01-01T00:00:00Z"}),
        dict(**TEST_CONFIG, **{"start_date": "2021-01-01T00:00:00Z", "end_date": "2021-12-31T23:59:59Z"}),
    ],
)
def test_check_connection(mocked_responses, source_mailgun, auth_header, check_connection_url, config):
    bad_config = config.copy()
    bad_config["private_key"] = bad_config["private_key"][-1::-1]
    bad_key_message = "Bad key message"
    bad_key_body = json.dumps({"message": bad_key_message})

    def request_callback(request):
        if request.headers.get("Authorization") == auth_header:
            return 200, {}, ""
        else:
            return 401, {}, bad_key_body

    mocked_responses.add_callback(responses.GET, check_connection_url, callback=request_callback, content_type="application/json")

    logger_mock = MagicMock()

    assert source_mailgun.check_connection(logger_mock, config) == (True, None)

    check_result = source_mailgun.check_connection(logger_mock, bad_config)
    assert not check_result[0]
    assert bad_key_message in check_result[1]


def test_check_connection_config_region_error(mocked_responses, source_mailgun, check_connection_url, test_config):
    test_config["domain_region"] = "WRONG_REGION"
    check_result = source_mailgun.check_connection(MagicMock(), test_config)
    assert not check_result[0]
    assert "domain_region" in check_result[1]


def test_check_connection_request_error(mocked_responses, source_mailgun, check_connection_url, test_config):
    custom_exception = requests.RequestException()
    mocked_responses.add(responses.GET, check_connection_url, body=custom_exception)
    assert source_mailgun.check_connection(MagicMock(), test_config) == (False, custom_exception)


@pytest.mark.parametrize(
    "config, error",
    [
        (TEST_CONFIG, None),
        (dict(**TEST_CONFIG, **{"start_date": "2021-01-01T00:00:00Z"}), None),
        (dict(**TEST_CONFIG, **{"start_date": "wrong format"}), "date format"),
    ],
)
def test_streams(config, error):
    source = SourceMailgun()
    expected_streams_number = 2
    if error is None:
        streams = source.streams(config)
        assert len(streams) == expected_streams_number
    else:
        with pytest.raises(ValueError) as exc_info:
            source.streams(config)
        assert error in str(exc_info.value)
