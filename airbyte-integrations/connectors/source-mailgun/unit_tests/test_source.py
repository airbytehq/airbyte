#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import json
from typing import Any, Dict
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
def test_config():
    return TEST_CONFIG.copy()


@pytest.fixture
def source_mailgun():
    source = SourceMailgun()
    yield source
    del source


def test_check_connection(mocked_responses, source_mailgun, auth_header, check_connection_url, test_config):
    bad_key_message = 'Bad key message'
    bad_key_body = json.dumps({"message": bad_key_message})
    mocked_responses.add(
        responses.GET, check_connection_url, status=200,
        match=[responses.matchers.header_matcher(auth_header)]
    )
    mocked_responses.add(
        responses.GET, check_connection_url, body=bad_key_body, status=401
    )
    logger_mock = MagicMock()

    assert source_mailgun.check_connection(logger_mock, test_config) == (True, None)

    test_config["private_key"] = test_config["private_key"][-1::-1]
    check_result = source_mailgun.check_connection(logger_mock, MagicMock())
    assert not check_result[0]
    assert bad_key_message in check_result[1]


def test_check_connection_error(mocked_responses, source_mailgun, check_connection_url):
    custom_exception = requests.RequestException()
    mocked_responses.add(
        responses.GET, check_connection_url, body=custom_exception
    )
    assert source_mailgun.check_connection(MagicMock(), MagicMock()) == (False, custom_exception)


def test_streams(test_config):
    source = SourceMailgun()
    streams = source.streams(test_config)
    expected_streams_number = 2
    assert len(streams) == expected_streams_number
