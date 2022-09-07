#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

import pytest
from source_slack.source import SourceSlack

from .conftest import parametrized_configs


@parametrized_configs
def test_streams(conversations_list, join_channels, config, is_valid):
    source = SourceSlack()
    if is_valid:
        streams = source.streams(config)
        assert len(streams) == 5
        assert join_channels.call_count == 4
    else:
        with pytest.raises(Exception) as exc_info:
            _ = source.streams(config)
        assert "No supported option_title: None specified. See spec.json for references" in repr(exc_info.value)


@pytest.mark.parametrize(
    "status_code, response, is_connection_successful, error_msg",
    (
        (200, {"members": [{"id": 1, "name": "Abraham"}]}, True, None),
        (
            400,
            "Bad request",
            False,
            "Got an exception while trying to set up the connection: 400 Client Error: "
            "None for url: https://slack.com/api/users.list?limit=100. Most probably, there are no users in the given Slack instance or "
            "your token is incorrect",
        ),
        (
            403,
            "Forbidden",
            False,
            "Got an exception while trying to set up the connection: 403 Client Error: "
            "None for url: https://slack.com/api/users.list?limit=100. Most probably, there are no users in the given Slack instance or "
            "your token is incorrect",
        ),
    ),
)
def test_check_connection(token_config, requests_mock, status_code, response, is_connection_successful, error_msg):
    requests_mock.register_uri("GET", "https://slack.com/api/users.list?limit=100", status_code=status_code, json=response)
    source = SourceSlack()
    success, error = source.check_connection(logger=logging.getLogger("airbyte"), config=token_config)
    assert success is is_connection_successful
    assert error == error_msg
