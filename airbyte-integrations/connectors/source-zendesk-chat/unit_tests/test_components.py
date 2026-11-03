# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping

import pytest
import requests


@pytest.fixture
def config() -> Mapping[str, Any]:
    return {
        "start_date": "2020-10-01T00:00:00Z",
        "subdomain": "airbyte",
        "credentials": {"credentials": "access_token", "access_token": "__access_token__"},
    }


@pytest.fixture
def bans_stream_record() -> Mapping[str, Any]:
    return {
        "ip_address": [{"reason": "test", "type": "ip_address", "id": 1234, "created_at": "2021-04-21T14:42:46Z", "ip_address": "0.0.0.0"}],
        "visitor": [
            {
                "type": "visitor",
                "id": 4444,
                "visitor_name": "Visitor 4444",
                "visitor_id": "visitor_id",
                "reason": "test",
                "created_at": "2021-04-27T13:25:01Z",
            }
        ],
    }


@pytest.fixture
def bans_stream_record_extractor_expected_output() -> List[Mapping[str, Any]]:
    return [
        {"reason": "test", "type": "ip_address", "id": 1234, "created_at": "2021-04-21T14:42:46Z", "ip_address": "0.0.0.0"},
        {
            "type": "visitor",
            "id": 4444,
            "visitor_name": "Visitor 4444",
            "visitor_id": "visitor_id",
            "reason": "test",
            "created_at": "2021-04-27T13:25:01Z",
        },
    ]


def test_bans_stream_record_extractor(
    components_module,
    config,
    requests_mock,
    bans_stream_record,
    bans_stream_record_extractor_expected_output,
) -> None:
    ZendeskChatBansRecordExtractor = components_module.ZendeskChatBansRecordExtractor
    test_url = f"https://{config['subdomain']}.zendesk.com/api/v2/chat/bans"
    requests_mock.get(test_url, json=bans_stream_record)
    test_response = requests.get(test_url)
    assert list(ZendeskChatBansRecordExtractor().extract_records(test_response)) == bans_stream_record_extractor_expected_output


class TestChatsStateMigration:
    """The pre-2.0.0 `chats` state is `{"update_timestamp": <epoch seconds or ISO>}`; 2.0.0 cursors on `timestamp`."""

    def setup_method(self) -> None:
        from components import ChatsStateMigration

        self.migration = ChatsStateMigration()

    @pytest.mark.parametrize(
        "legacy_value",
        ["1697795052", 1697795052, 1697795052.0, "2023-10-20T09:44:12Z", "2023-10-20T09:44:12.000Z"],
    )
    def test_legacy_state_seeds_both_cursors(self, legacy_value: Any) -> None:
        legacy_state = {"update_timestamp": legacy_value}

        assert self.migration.should_migrate(legacy_state)
        assert self.migration.migrate(legacy_state) == {
            "use_global_cursor": True,
            "state": {"timestamp": "2023-10-20T09:44:12Z"},
            "parent_state": {"chats_search": {"timestamp": "2023-10-20T09:44:12Z"}},
        }

    @pytest.mark.parametrize(
        "state",
        [
            {},
            {"timestamp": "2023-10-20T09:44:12Z"},
            {"use_global_cursor": True, "state": {"timestamp": "2023-10-20T09:44:12Z"}},
            {"states": [], "state": {"timestamp": "2023-10-20T09:44:12Z"}},
        ],
    )
    def test_new_or_empty_state_is_left_alone(self, state: Mapping[str, Any]) -> None:
        assert not self.migration.should_migrate(state)

    def test_unparseable_legacy_value_restarts_from_scratch(self) -> None:
        assert self.migration.migrate({"update_timestamp": "yesterday"}) == {}
