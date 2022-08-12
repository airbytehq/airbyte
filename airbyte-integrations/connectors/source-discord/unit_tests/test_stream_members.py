#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import mock
import pytest

from source_discord.stream_members import DiscordMembersStream

CONFIG = {
    "server_token": "test_token",
    "guild_id": "test_guild_id",
    "initial_timestamp": "2022-01-01T00:00:000"
}

@pytest.fixture
def patch_base_class(mocker):
    mocker.patch.object(DiscordMembersStream, "path", "api/guilds/test_guild_id/preview")
    mocker.patch.object(DiscordMembersStream, "primary_key", "test_primary_key")
    mocker.patch.object(DiscordMembersStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = DiscordMembersStream(CONFIG)
    assert stream.request_headers(**CONFIG) == {"Authorization": "Bot test_token"}


def test_next_page_token_with_response_null(patch_base_class):
    stream = DiscordMembersStream(CONFIG)
    response_mock = mock.MagicMock()
    response_mock.json.return_value = None
    assert stream.next_page_token(response_mock) == None


def test_next_page_token_with_ids(patch_base_class):
    stream = DiscordMembersStream(CONFIG)
    response_mock = mock.MagicMock()
    response_mock.json.return_value = [{"user": {"id": 1111}}, {"user": {"id": 9999}}]
    assert stream.next_page_token(response_mock) == {"after": 9999}


def test_parse_response_returning_200(patch_base_class):
    stream = DiscordMembersStream(CONFIG)
    response_mock = mock.MagicMock()
    type(response_mock).status_code = mock.PropertyMock(return_value=200)
    response_mock.json.return_value = {"test": "ok"}
    assert next(stream.parse_response(response_mock)) == "test"


def test_parse_response_returning_400(patch_base_class):
    stream = DiscordMembersStream(CONFIG)
    response_mock = mock.MagicMock()
    type(response_mock).status_code = mock.PropertyMock(return_value=400)
    assert len(list(stream.parse_response(response_mock))) == 0
