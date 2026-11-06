#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, List, Mapping

import requests

from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


date_time_parser = DatetimeParser()

_CHATS_SEARCH_STREAM_NAME = "chats_search"
_CHATS_CURSOR_FIELD = "timestamp"
_CHATS_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
_LEGACY_CHATS_CURSOR_FIELD = "update_timestamp"


@dataclass
class ZendeskChatBansRecordExtractor(RecordExtractor):
    """
    Unnesting nested bans: `visitor`, `ip_address`.
    """

    def extract_records(
        self,
        response: requests.Response,
    ) -> Iterable[Mapping[str, Any]]:
        response_data = response.json()
        ip_address: List[Mapping[str, Any]] = response_data.get("ip_address", [])
        visitor: List[Mapping[str, Any]] = response_data.get("visitor", [])
        bans = ip_address + visitor
        bans = sorted(
            bans,
            key=lambda x: date_time_parser.parse(date=x["created_at"], format="%Y-%m-%dT%H:%M:%SZ")
            if x["created_at"]
            else date_time_parser.parse(date=DatetimeParser._UNIX_EPOCH, format="%Y-%m-%dT%H:%M:%SZ"),
        )
        yield from bans


class ChatsStateMigration(StateMigration):
    """
    Migrates the `chats` state written before 2.0.0 to the state shape of the search-plus-fetch read path.

    Before 2.0.0 the stream read the incremental export with cursor `update_timestamp`, so the state was
    `{"update_timestamp": <value>}` where the value is either epoch seconds (the format the export took as
    `start_time`) or an ISO 8601 timestamp. Since 2.0.0 the stream is a substream of the internal `chats_search`
    parent, which searches by `update_timestamp` windows and tracks `timestamp` as its cursor; the stream itself
    keeps a global `timestamp` cursor. The state becomes
    `{"use_global_cursor": true, "state": {"timestamp": <iso>}, "parent_state": {"chats_search": {"timestamp": <iso>}}}`.

    Seeding both cursors with the old `update_timestamp` value never skips data: every chat the old state had not
    seen was created or updated after that value, so the next search windows (which start one day earlier, see the
    parent's `lookback_window`) return it again.
    """

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return (
            bool(stream_state)
            and _LEGACY_CHATS_CURSOR_FIELD in stream_state
            and "state" not in stream_state
            and "states" not in stream_state
        )

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_value = self._to_iso_timestamp(stream_state[_LEGACY_CHATS_CURSOR_FIELD])
        if cursor_value is None:
            # An unreadable value falls back to a full read from `start_date`, which re-reads but never skips.
            return {}
        return {
            "use_global_cursor": True,
            "state": {_CHATS_CURSOR_FIELD: cursor_value},
            "parent_state": {_CHATS_SEARCH_STREAM_NAME: {_CHATS_CURSOR_FIELD: cursor_value}},
        }

    @staticmethod
    def _to_iso_timestamp(value: Any) -> Any:
        if isinstance(value, bool) or value is None:
            return None
        if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().lstrip("-").isdigit()):
            return datetime.fromtimestamp(int(float(value)), tz=timezone.utc).strftime(_CHATS_DATETIME_FORMAT)
        if isinstance(value, str):
            for fmt in (_CHATS_DATETIME_FORMAT, "%Y-%m-%dT%H:%M:%S.%fZ"):
                try:
                    return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc).strftime(_CHATS_DATETIME_FORMAT)
                except ValueError:
                    continue
        return None
