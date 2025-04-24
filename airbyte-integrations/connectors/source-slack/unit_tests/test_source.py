#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_slack.source import SourceSlack

from .conftest import parametrized_configs


def get_stream_by_name(stream_name, config):
    streams = SourceSlack().streams(config=config)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@parametrized_configs
def test_streams(conversations_list, config, is_valid):
    source = SourceSlack()
    if is_valid:
        streams = source.streams(config)
        assert len(streams) == 5
    else:
        with pytest.raises(Exception) as exc_info:
            _ = source.streams(config)
        assert "The path from `authenticator_selection_path` is not found in the config." in repr(exc_info.value)


@pytest.mark.parametrize(
    "status_code, response, is_connection_successful, error_msg",
    (
        (200, {"members": [{"id": 1, "name": "Abraham"}]}, True, None),
        (200, {"ok": False, "error": "invalid_auth"}, False, "Authentication has failed, please update your credentials."),
        (
            400,
            "Bad request",
            False,
            "Got an exception while trying to set up the connection. Most probably, there are no users in the given Slack instance or your token is incorrect.",
        ),
        (
            403,
            "Forbidden",
            False,
            "Got an exception while trying to set up the connection. Most probably, there are no users in the given Slack instance or your token is incorrect.",
        ),
    ),
)
def test_check_connection(token_config, requests_mock, status_code, response, is_connection_successful, error_msg):
    requests_mock.register_uri("GET", "https://slack.com/api/users.list?limit=1000", status_code=status_code, json=response)
    source = SourceSlack()
    success, error = source.check_connection(logger=logging.getLogger("airbyte"), config=token_config)
    assert success is is_connection_successful
    if not success:
        assert error_msg in error


def test_threads_auth(token_config, oauth_config):
    source = SourceSlack()
    auth = source._threads_authenticator(token_config)
    assert auth.token == "Bearer api-token"
    source = SourceSlack()
    auth = source._threads_authenticator(oauth_config)
    assert auth.token == "Bearer access-token"


def test_get_threads_stream(token_config):
    source = SourceSlack()
    threads_stream = source.get_threads_stream(token_config)
    assert threads_stream
