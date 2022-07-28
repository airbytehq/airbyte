#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
import mock
# from http import HTTPStatus
# from unittest.mock import MagicMock

from source_discord.stream_serverPreview import DiscordServerPreviewStream


@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(DiscordServerPreviewStream, "path", "api/guilds/test_guild_id/preview")
    mocker.patch.object(DiscordServerPreviewStream, "primary_key", "test_primary_key")
    mocker.patch.object(DiscordServerPreviewStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    config = {
        "server_token": "test_token",
        "guild_id": "test_guild_id",
        "initial_timestamp": "2022-01-01T00:00:000"
    }
    stream = DiscordServerPreviewStream(config)
    assert stream.request_headers(**config) == {"Authorization": "Bot test_token"}

"""
def test_next_page_token(patch_base_class):
    stream = DiscordStream()
    # TODO: replace this with your input parameters
    inputs = {"response": MagicMock()}
    # TODO: replace this with your expected next page token
    expected_token = None
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class):
    stream = DiscordStream()
    # TODO: replace this with your input parameters
    inputs = {"response": MagicMock()}
    # TODO: replace this with your expected parced object
    expected_parsed_object = {}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object



def test_http_method(patch_base_class):
    stream = DiscordStream()
    # TODO: replace this with your expected http request method
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = DiscordStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = DiscordStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
"""