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
    """Migrates tickets stream state from the `updated_at` cursor back to `generated_timestamp`.

    Background: v5.2.0 switched the `tickets` stream from the Incremental Ticket Export API
    (keyed on `generated_timestamp`) to the Export Search Results API (filtered/checkpointed on
    `updated_at`). Because Zendesk only bumps `updated_at` when an update generates a ticket
    event, automation/macro/system-driven updates were silently dropped. We revert the stream to
    `generated_timestamp`, so existing connections carrying `updated_at`-based state must be
    migrated back.

    Backfill: to recover every ticket missed while the regression was live, the migrated cursor
    is clamped back to an absolute floor of 2026-03-01T00:00:00Z (epoch 1772323200) — just before
    v5.2.0 merged (2026-03-12) / rolled out to Cloud (~2026-03-24). This guarantees a complete
    one-time backfill regardless of when a connection upgrades (a relative "N-day" window computed
    at migration time would drift forward and miss the earliest affected tickets). `min(...)`
    ensures we only ever pull the cursor back, never forward, so connections whose cursor has not
    yet reached the floor are left untouched.

    Only connections that ran the buggy `updated_at`-cursor versions carry `updated_at` state, so
    keying `should_migrate` on that field means the floor is applied exactly once (on the first
    sync after upgrade); subsequent syncs write `generated_timestamp` state and are left alone.
    Connections still on a pre-5.2.0 `generated_timestamp` cursor were never broken and are not
    migrated.
    """

    # 2026-03-01T00:00:00Z
    BACKFILL_FLOOR = 1772323200

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and "updated_at" in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        try:
            cursor_value = int(stream_state["updated_at"])
        except (KeyError, TypeError, ValueError):
            cursor_value = self.BACKFILL_FLOOR
        return {"generated_timestamp": min(cursor_value, self.BACKFILL_FLOOR)}
