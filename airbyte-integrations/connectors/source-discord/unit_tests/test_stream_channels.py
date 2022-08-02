#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock
import mock
import pytest

from source_discord.stream_channels import DiscordChannelsStream

CONFIG = {
    "server_token": "test_token",
    "guild_id": "test_guild_id",
    "initial_timestamp": "2022-01-01T00:00:000"
}

@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(DiscordChannelsStream, "path", "api/guilds/test_guild_id/preview")
    mocker.patch.object(DiscordChannelsStream, "primary_key", "test_primary_key")
    mocker.patch.object(DiscordChannelsStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = DiscordChannelsStream(CONFIG)
    assert stream.request_headers(**CONFIG) == {"Authorization": "Bot test_token"}


def test_next_page_token(patch_base_class):
    stream = DiscordChannelsStream(CONFIG)
    inputs = {"response": MagicMock()}
    assert stream.next_page_token(inputs) == None


def test_parse_response_returning_200(patch_base_class):
    stream = DiscordChannelsStream(CONFIG)
    response_mock = mock.MagicMock()
    type(response_mock).status_code = mock.PropertyMock(return_value=200)
    response_mock.json.return_value = {"test": "ok"}
    assert next(stream.parse_response(response_mock)) == "test"


def test_parse_response_returning_400(patch_base_class):
    stream = DiscordChannelsStream(CONFIG)
    response_mock = mock.MagicMock()
    type(response_mock).status_code = mock.PropertyMock(return_value=400)
    assert len(list(stream.parse_response(response_mock))) == 0
