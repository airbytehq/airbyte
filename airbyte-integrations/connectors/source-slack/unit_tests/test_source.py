#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging

import pytest

from airbyte_cdk.models import Status

from .conftest import get_source, parametrized_configs


def get_stream_by_name(stream_name, config):
    streams = get_source(config, stream_name)
    for stream in streams:
        if stream.name == stream_name:
            return stream
    raise ValueError(f"Stream {stream_name} not found")


@parametrized_configs
def test_streams(conversations_list, config, is_valid):
    source = get_source(config)
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
    source = get_source(token_config)
    connection_status = source.check(logger=logging.getLogger("airbyte"), config=token_config)
    success = connection_status.status == Status.SUCCEEDED
    assert success is is_connection_successful
    if not success:
        assert error_msg in connection_status.message
