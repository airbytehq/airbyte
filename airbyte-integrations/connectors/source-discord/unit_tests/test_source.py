#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests_mock
from unittest.mock import MagicMock

from source_discord.source import SourceDiscord


def test_check_connection_does_not_contain_id():
    source = SourceDiscord()
    logger_mock, config_mock = MagicMock(), MagicMock()
    assert source.check_connection(logger_mock, config_mock) == (False, "missing id")


def test_check_connection_id_do_not_match():
    url = "https://discord.com/api/users/@me"
    config = {
        "server_token": "test_token",
        "bot_id": "test_bot_id",
        "channel_ids": ["test_channel_id", "test_channel_2"]
    }
    request_headers = {"Authorization": f"Bot {config['server_token']}"}
    with requests_mock.Mocker() as rm:
        rm.get(url, text='{"id": "test_bot_id_fail"}', request_headers=request_headers)
        source = SourceDiscord()
        logger_mock = MagicMock()
        assert source.check_connection(logger_mock, config) == (False, "wrong id")


def test_check_connection_id_matches():
    url = "https://discord.com/api/users/@me"
    config = {
        "server_token": "test_token",
        "bot_id": "test_bot_id",
        "channel_ids": ["test_channel_id", "test_channel_2"]
    }
    request_headers = {"Authorization": f"Bot {config['server_token']}"}
    with requests_mock.Mocker() as rm:
        rm.get(url, text='{"id": "test_bot_id"}', request_headers=request_headers)
        source = SourceDiscord()
        logger_mock = MagicMock()
        assert source.check_connection(logger_mock, config) == (True, "accepted")


def test_streams():
    config = {
        "server_token": "test_token",
        "bot_id": "test_bot_id",
        "guild_id": "test_guild_id",
        "channel_ids": ["test_channel_id", "test_channel_2"],
        "initial_timestamp": "2022-01-01T00:00:000"
    }
    source = SourceDiscord()
    streams = source.streams(config)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number
