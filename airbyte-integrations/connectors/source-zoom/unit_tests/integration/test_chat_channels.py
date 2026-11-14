# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from unittest import TestCase

import freezegun

from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.models.outcome import ExpectedOutcome

from .zoom_mocks import (
    assert_completed_without_errors,
    assert_failed_with_config_error,
    json_response,
    mock_token,
    mock_users,
    read_stream,
    records_data,
    request,
    zoom_error,
)


_STREAM = "chat_channels"
_CHANNEL = {"id": "shared-channel", "name": "Announcements", "type": 2}


def _channels_request(user_id: str, next_page_token: str = ""):
    params = {"page_size": "50"}
    if next_page_token:
        params["next_page_token"] = next_page_token
    return request(f"/chat/users/{user_id}/channels", params)


def _mock_parents(http_mocker: HttpMocker, users=None):
    mock_token(http_mocker)
    return mock_users(http_mocker, users)


@freezegun.freeze_time("2026-10-20T12:00:00Z")
class TestChatChannels(TestCase):
    @HttpMocker()
    def test_duplicates_shared_channels_for_each_user(self, http_mocker: HttpMocker):
        users_request = _mock_parents(http_mocker, [{"id": "u1"}, {"id": "u2"}])
        user_one = _channels_request("u1")
        user_two = _channels_request("u2")
        http_mocker.get(user_one, json_response({"channels": [_CHANNEL]}))
        http_mocker.get(user_two, json_response({"channels": [_CHANNEL]}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert sorted(records_data(output), key=lambda record: record["user_id"]) == [
            {**_CHANNEL, "user_id": "u1"},
            {**_CHANNEL, "user_id": "u2"},
        ]
        http_mocker.assert_number_of_calls(users_request, 1)
        http_mocker.assert_number_of_calls(user_one, 1)
        http_mocker.assert_number_of_calls(user_two, 1)

    @HttpMocker()
    def test_paginates_channels(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        first = _channels_request("u1")
        second = _channels_request("u1", "channel-page-2")
        http_mocker.get(first, json_response({"channels": [_CHANNEL], "next_page_token": "channel-page-2"}))
        http_mocker.get(second, json_response({"channels": [{"id": "second-channel", "name": "Team"}]}))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert {record["id"] for record in records_data(output)} == {"shared-channel", "second-channel"}
        assert {record["user_id"] for record in records_data(output)} == {"u1"}
        http_mocker.assert_number_of_calls(first, 1)
        http_mocker.assert_number_of_calls(second, 1)

    @HttpMocker()
    def test_unknown_user_is_ignored(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        current = _channels_request("u1")
        http_mocker.get(current, zoom_error(1001, "User does not exist.", status_code=404))

        output = read_stream(_STREAM)

        assert_completed_without_errors(output, _STREAM)
        assert output.records == []
        http_mocker.assert_number_of_calls(current, 1)

    @HttpMocker()
    def test_missing_scope_is_configuration_error(self, http_mocker: HttpMocker):
        _mock_parents(http_mocker)
        current = _channels_request("u1")
        http_mocker.get(current, zoom_error(4711, "Missing chat scope.", status_code=400))

        output = read_stream(_STREAM, expected_outcome=ExpectedOutcome.EXPECT_EXCEPTION)

        assert_failed_with_config_error(output, _STREAM)
        assert output.is_in_logs("chat_channel:read:admin")
        assert output.is_in_logs("team_chat:read:list_user_channels:admin")
        http_mocker.assert_number_of_calls(current, 1)
