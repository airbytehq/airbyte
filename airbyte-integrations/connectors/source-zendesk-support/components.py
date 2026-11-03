# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration


class ZendeskSupportExtractorEvents(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = response.json().get("ticket_events") or []
        except requests.exceptions.JSONDecodeError:
            records = []

        events = []
        for record in records:
            for event in record.get("child_events", []):
                if event.get("event_type") == "Comment":
                    for prop in ["via_reference_id", "ticket_id", "timestamp"]:
                        event[prop] = record.get(prop)

                    # https://github.com/airbytehq/oncall/issues/1001
                    if not isinstance(event.get("via"), dict):
                        event["via"] = None
                    events.append(event)
        return events


class ZendeskSupportAttributeDefinitionsExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            records = []
            for definition in response.json()["definitions"]["conditions_all"]:
                definition["condition"] = "all"
                records.append(definition)
            for definition in response.json()["definitions"]["conditions_any"]:
                definition["condition"] = "any"
                records.append(definition)
        except requests.exceptions.JSONDecodeError:
            records = []
        return records


class TicketsStateMigration(StateMigration):
    """Migrates `tickets` state from the `generated_timestamp` cursor to the `updated_at` cursor.

    Versions before 6.0.0 read the Incremental Ticket Export, which is keyed on `generated_timestamp`
    (a unix timestamp Zendesk bumps on every ticket change). 6.0.0 reads the ticket list sorted by
    `updated_at`. A ticket's `generated_timestamp` is never earlier than its `updated_at`, so the saved
    value is an upper bound for the tickets already synced. The migration rewinds it by one hour, on
    top of the stream's own lookback window, so a ticket whose two timestamps straddle the cursor is
    read again rather than skipped. The same migration runs on the `parent_state` of the per-ticket
    substreams. State that already carries `updated_at` (5.2.x) is left alone; an unparsable value
    drops the cursor so the next sync re-reads from `start_date`.
    """

    REWIND_SECONDS = 3600

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and "generated_timestamp" in stream_state and "updated_at" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            cursor_value = int(stream_state["generated_timestamp"])
        except (KeyError, TypeError, ValueError):
            return {}
        return {"updated_at": str(max(cursor_value - self.REWIND_SECONDS, 0))}
