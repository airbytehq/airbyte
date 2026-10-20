# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.utils.datetime_helpers import ab_datetime_parse


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


class ZendeskSupportTicketMetricSetsExtractor(RecordExtractor):
    """Extracts the `metric_sets` side-load of an Incremental Ticket Export page.

    `GET incremental/tickets/cursor.json?include=metric_sets` returns one metric set per ticket on
    the page next to the `tickets` array. A metric set has the same shape as
    `GET tickets/{id}/metrics`, but it carries no `generated_timestamp`, and that is the value the
    export filters on. Each metric set is stamped with its ticket's `generated_timestamp` as
    `_ab_updated_at`, the stream cursor, so the saved state is a valid `start_time` for the export.
    The ticket is always on the same page, so the join needs no extra request.
    """

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            body = response.json()
        except requests.exceptions.JSONDecodeError:
            return []

        generated_timestamps = {ticket.get("id"): ticket.get("generated_timestamp") for ticket in body.get("tickets") or []}

        records = []
        for metric_set in body.get("metric_sets") or []:
            cursor_value = _to_unix_timestamp(generated_timestamps.get(metric_set.get("ticket_id")))
            if cursor_value is None:
                # Not observed on live data. Fall back to the metric set's own `updated_at`, which
                # Zendesk writes within a second or so of the ticket's `generated_timestamp`.
                cursor_value = _to_unix_timestamp(metric_set.get("updated_at"))
            if cursor_value is not None:
                metric_set["_ab_updated_at"] = cursor_value
            records.append(metric_set)
        return records


def _to_unix_timestamp(value: Any) -> Optional[int]:
    """Parses a unix timestamp (int or numeric string) or an ISO 8601 datetime into epoch seconds."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        pass
    try:
        return int(ab_datetime_parse(str(value)).timestamp())
    except (TypeError, ValueError):
        return None


class TicketMetricsStateMigration(StateMigration):
    """Converts `ticket_metrics` state written before 5.7.0 into a plain `_ab_updated_at` cursor.

    Up to 5.6.x `ticket_metrics` was a `StateDelegatingStream`. Its full-refresh path wrote
    `{"_ab_updated_at": "<epoch>"}`, which is already the current shape and is left alone. Its
    incremental path was a per-ticket substream of `tickets`, so its state is per-partition:

        {"use_global_cursor": false, "lookback_window": 0,
         "state": {"_ab_updated_at": "<epoch>"},
         "states": [{"partition": {"ticket_id": 1, "parent_slice": {}}, "cursor": {"_ab_updated_at": "<epoch>"}}],
         "parent_state": {"tickets": {"generated_timestamp": "<epoch>"}}}

    The stream now reads the same Incremental Ticket Export as `tickets` and filters it with
    `start_time`, so the resume point is the parent `tickets` cursor: with `incremental_dependency`
    the CDK only advances `parent_state` once every ticket before it has had its metrics read, and
    intermediate checkpoints advance it while the global `state` keeps the previous sync's value.
    The global `state` is the fallback when there is no parent cursor.

    A parent cursor still on the legacy `updated_at` key (5.2.x-5.4.x) is clamped exactly like
    `TicketsStateMigration` does for `tickets`. The old stream applied that migration to its
    `parent_state`, so this keeps the same backfill for `ticket_metrics`.

    Any other shape without a usable cursor (for example a full-refresh-only state) becomes `{}`,
    so the stream starts from `start_date`.
    """

    CURSOR_FIELD = "_ab_updated_at"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and set(stream_state.keys()) != {self.CURSOR_FIELD}

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        candidates = (
            self._parent_tickets_cursor(stream_state.get("parent_state")),
            _to_unix_timestamp(self._get(stream_state.get("state"), self.CURSOR_FIELD)),
            _to_unix_timestamp(stream_state.get(self.CURSOR_FIELD)),
            # Pre-4.3.0 state keyed on the ticket's `generated_timestamp`.
            _to_unix_timestamp(stream_state.get("generated_timestamp")),
        )
        cursor_value = next((value for value in candidates if value is not None), None)
        return {self.CURSOR_FIELD: str(cursor_value)} if cursor_value is not None else {}

    @staticmethod
    def _get(mapping: Any, key: str) -> Any:
        return mapping.get(key) if isinstance(mapping, Mapping) else None

    @classmethod
    def _parent_tickets_cursor(cls, parent_state: Any) -> Optional[int]:
        tickets_state = cls._get(parent_state, "tickets")
        if not isinstance(tickets_state, Mapping) or not tickets_state:
            return None
        tickets_migration = TicketsStateMigration()
        if tickets_migration.should_migrate(tickets_state):
            tickets_state = tickets_migration.migrate(tickets_state)
        return _to_unix_timestamp(tickets_state.get("generated_timestamp"))
