#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import mock
import pytest
from datetime import datetime

from source_discord.stream_messages import DiscordMessagesStream
from source_discord.stream_messages import string_to_timestamp

CONFIG = {
    "server_token": "test_token",
    "guild_id": "test_guild_id",
    "channel_ids": ["test_channel_id", "test_channel_2"]
}
INITIAL_TIMESTAMP = "2022-01-01T00:00:000"

@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(DiscordMessagesStream, "path", "api/guilds/test_guild_id/preview")
    mocker.patch.object(DiscordMessagesStream, "primary_key", "test_primary_key")
    mocker.patch.object(DiscordMessagesStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    assert stream.request_headers(**CONFIG) == {"Authorization": "Bot test_token"}


def test_request_params_return_none_if_no_next_page(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    next_page_token = None
    stream.request_params(next_page_token)
    assert stream.request_params(next_page_token) == None


def test_request_params_return_value_if_no_next_page(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    next_page_token = "value"
    stream.request_params(next_page_token)
    assert stream.request_params(next_page_token) == "value"


def test_parse_response_returning_200(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    response_mock = mock.MagicMock()
    type(response_mock).status_code = mock.PropertyMock(return_value=200)
    response_mock.json.return_value = {"test": "ok"}
    assert next(stream.parse_response(response_mock)) == "test"


def test_parse_response_returning_400(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    response_mock = mock.MagicMock()
    type(response_mock).status_code = mock.PropertyMock(return_value=400)
    assert len(list(stream.parse_response(response_mock))) == 0


def test_next_page_token_with_response_null(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    response_mock = mock.MagicMock()
    response_mock.json.return_value = None
    assert stream.next_page_token(response_mock) == None


def test_next_page_token_with_earlier_timestamp(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    stream.latest_stream_timestamp = datetime.strptime("2100-01-01T00:00", "%Y-%m-%dT%H:%M")
    response_mock = mock.MagicMock()
    response_mock.json.return_value = [{"timestamp": INITIAL_TIMESTAMP}]
    assert stream.next_page_token(response_mock) == None


def test_next_page_token_with_later_timestamp(patch_base_class):
    stream = DiscordMessagesStream(CONFIG, INITIAL_TIMESTAMP)
    stream.latest_stream_timestamp = datetime.strptime("2000-01-01T00:00", "%Y-%m-%dT%H:%M")
    response_mock = mock.MagicMock()
    response_mock.json.return_value = [{"timestamp": INITIAL_TIMESTAMP, "id": 9999}]
    assert stream.next_page_token(response_mock) == {"before": 9999}


def test_string_to_timestamp(patch_base_class):
    expected = datetime.strptime(
        "2022-01-01T00:00:00",
        "%Y-%m-%dT%H:%M:%S"
    )
    received = string_to_timestamp("2022-01-01T00:00:000")
    assert expected == received