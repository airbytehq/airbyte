#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from unittest.mock import patch

import pytest
import requests
from airbyte_cdk import AirbyteLogger
from source_zendesk_chat.source import SourceZendeskChat, ZendeskAuthentication
from source_zendesk_chat.streams import (
    Accounts,
    Agents,
    AgentTimelines,
    Bans,
    Chats,
    Departments,
    Goals,
    Roles,
    RoutingSettings,
    Shortcuts,
    Skills,
    Triggers,
)

TEST_CONFIG: dict = {
    "start_date": "2020-10-01T00:00:00Z",
    "access_token": "access_token",
}
TEST_INSTANCE: SourceZendeskChat = SourceZendeskChat()


def test_get_auth():
    expected = {"Authorization": "Bearer access_token"}
    result = ZendeskAuthentication(TEST_CONFIG).get_auth().get_auth_header()
    assert expected == result


@pytest.mark.parametrize(
    "response, check_passed",
    [
        (iter({"id": 123}), True),
        (requests.HTTPError(), False),
    ],
    ids=["Success", "Fail"],
)
def test_check(response, check_passed):
    with patch.object(RoutingSettings, "read_records", return_value=response) as mock_method:
        result = TEST_INSTANCE.check_connection(logger=AirbyteLogger, config=TEST_CONFIG)
        mock_method.assert_called()
        assert check_passed == result[0]


@pytest.mark.parametrize(
    "stream_cls",
    [
        (Accounts),
        (Agents),
        (AgentTimelines),
        (Bans),
        (Chats),
        (Departments),
        (Goals),
        (Roles),
        (RoutingSettings),
        (Shortcuts),
        (Skills),
        (Triggers),
    ],
)
def test_streams(stream_cls):
    streams = TEST_INSTANCE.streams(config=TEST_CONFIG)
    for stream in streams:
        if stream_cls in streams:
            assert isinstance(stream, stream_cls)
