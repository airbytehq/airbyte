# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse


class ZendeskSupportAuditCommentsExtractor(RecordExtractor):
    """Extracts `ticket_comments` records from `GET /tickets/{ticket_id}/audits.json`.

    A comment is an event of type `Comment` inside an audit. The audit carries the fields the comment
    record needs that the event itself lacks: `ticket_id`, `created_at` and `via` (the audit's `via` is
    the channel the comment came through), and `timestamp` is the unix form of `created_at`. The
    record shape matches what the Incremental Ticket Event Export based stream emitted before 6.0.0,
    including `via_reference_id`, which that stream always emitted as null.
    """

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            audits = response.json().get("audits") or []
        except requests.exceptions.JSONDecodeError:
            return []

        comments = []
        for audit in audits:
            for event in audit.get("events") or []:
                if event.get("type") != "Comment":
                    continue
                comment = dict(event)
                comment["ticket_id"] = audit.get("ticket_id")
                comment["created_at"] = audit.get("created_at")
                comment["timestamp"] = self._unix_timestamp(audit.get("created_at"))
                comment["via"] = audit.get("via") if isinstance(audit.get("via"), dict) else None
                comment["via_reference_id"] = None
                comment["event_type"] = "Comment"
                comments.append(comment)
        return comments

    @staticmethod
    def _unix_timestamp(created_at: Any) -> Optional[int]:
        if not created_at:
            return None
        try:
            return int(ab_datetime_parse(created_at).timestamp())
        except (TypeError, ValueError):
            return None


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


class ClosedTicketsSearchStateMigration(StateMigration):
    """Seeds the `closed_tickets_search` parent cursor from a state saved before that parent existed.

    The per-ticket substreams (`ticket_audits_per_ticket`, `ticket_events`, `ticket_comments` and
    `ticket_metric_events`) have two parents since 6.0.0: the `tickets` list and `closed_tickets_search`,
    an Export Search of the closed tickets updated since the cursor, which is how archived tickets are
    reached. A flat pre-6.0.0 state (one cursor value) seeds both parents through the CDK factory. A
    nested state whose `parent_state` lacks `closed_tickets_search` (5.7.0 `ticket_audits_per_ticket`
    states carry only `tickets`) reaches this migration as the child's global cursor instead, keyed on
    the child's cursor field (`_ab_updated_at`, `timestamp` or `created_at`). That value is the newest
    ticket the substream has read, so it is re-keyed onto `updated_at` and rewound by one hour, as
    `TicketsStateMigration` does for the `tickets` parent, so the first sync re-reads the closed
    tickets changed around the saved cursor rather than every closed ticket since `start_date`. State
    that already carries `updated_at` is left alone; a state with several values or an unparsable
    value drops the cursor so the parent walks from `start_date`.
    """

    REWIND_SECONDS = 3600

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and "updated_at" not in stream_state

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        values = [value for value in stream_state.values() if not isinstance(value, (dict, list))]
        if len(values) != 1 or len(values) != len(stream_state):
            return {}
        cursor_value = TicketMetricEventsStateMigration._to_unix_timestamp(values[0])
        if cursor_value is None:
            return {}
        return {"updated_at": str(max(cursor_value - self.REWIND_SECONDS, 0))}


class TicketMetricEventsStateMigration(StateMigration):
    """Migrates a 5.x `ticket_metric_events` state to the per-ticket cursor of 6.0.0.

    Versions before 6.0.0 read the Incremental Ticket Metric Event Export and saved the newest event
    `time` as a flat `{"time": "<unix timestamp>"}` state. 6.0.0 reads the metric events of every
    ticket the `tickets` stream returns and cursors on `_ab_updated_at`, the parent ticket's
    `generated_timestamp`, with the parent `tickets` cursor under `parent_state`. The event `time`
    cannot bound the stream: Zendesk records SLA `breach` events before the breach happens, dated
    with the future breach moment, so a saved `time` can lie ahead of the last sync. The migration
    clamps the value to the migration time, rewinds it by one hour (the rewind `TicketsStateMigration`
    applies to the parent cursor, on top of the parent's own lookback window) and uses the result as
    the global cursor and as the `updated_at` cursor of both parents (`tickets` and
    `closed_tickets_search`), so the first 6.0.0 sync walks the tickets changed since the last
    export. The parents are seeded here rather than by the CDK's flat-state fallback because the
    factory reads the migrated state, which is no longer flat. A state that already carries `_ab_updated_at`, `state` or
    `parent_state` is left alone; an unparsable value drops the state so the next sync re-reads from
    `start_date`.
    """

    REWIND_SECONDS = 3600

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return (
            bool(stream_state)
            and "time" in stream_state
            and not any(key in stream_state for key in ("_ab_updated_at", "state", "states", "parent_state"))
        )

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        cursor_value = self._to_unix_timestamp(stream_state.get("time"))
        if cursor_value is None:
            return {}
        now = int(ab_datetime_now().timestamp())
        value = str(max(min(cursor_value, now) - self.REWIND_SECONDS, 0))
        return {
            "_ab_updated_at": value,
            "parent_state": {"tickets": {"updated_at": value}, "closed_tickets_search": {"updated_at": value}},
        }

    @staticmethod
    def _to_unix_timestamp(value: Any) -> Optional[int]:
        if value is None or isinstance(value, bool):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            pass
        try:
            return int(ab_datetime_parse(str(value)).timestamp())
        except (TypeError, ValueError):
            return None
