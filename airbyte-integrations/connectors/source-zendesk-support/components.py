# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, List, Mapping, Optional

import requests

from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse


logger = logging.getLogger("airbyte")


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
        return _to_unix_timestamp(value)


def _to_unix_timestamp(value: Any) -> Optional[int]:
    """Parses a unix timestamp (int or numeric string) or an ISO 8601 datetime into epoch seconds."""
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


class ZendeskSupportTicketMetricSetsExtractor(RecordExtractor):
    """Extracts the `metric_sets` side-load of a ticket list page.

    `GET /api/v2/tickets?sort=-updated_at&include=metric_sets` returns, next to the page's `tickets`,
    one metric set per listed ticket under `metric_sets`, with the same shape as
    `GET /tickets/{ticket_id}/metrics`. The ticket list is sorted and bounded on the tickets'
    `updated_at`, and a metric set carries no field that follows the ticket (its own `updated_at` can
    be years older than the ticket's), so each metric set is joined to its ticket on the same page by
    `ticket_id` and stamped with the ticket's `updated_at`, as a unix timestamp, as `_ab_updated_at`,
    the stream's cursor. That is the value the list is sorted and filtered on, so the stream saves the
    same resume point as `tickets`. The ticket's `generated_timestamp`, which the per-ticket path wrote
    there, is not used: Zendesk bumps it on system-only updates that leave `updated_at` alone, so a
    ticket deep in a long walk could carry a value later than every ticket on the first page and push
    the saved cursor past tickets updated while the walk ran, which the next sync would skip. No extra
    request is needed: Zendesk side-loads the metric set on the page that lists the ticket. A metric
    set whose ticket is not on the page (not observed on live data) is stamped with its own
    `updated_at`, and the record filter keeps or drops it on that value.
    """

    def extract_records(self, response: requests.Response) -> List[Mapping[str, Any]]:
        try:
            body = response.json()
        except requests.exceptions.JSONDecodeError:
            return []
        if not isinstance(body, Mapping):
            return []

        tickets_updated_at = {
            ticket.get("id"): ticket.get("updated_at") for ticket in body.get("tickets") or [] if isinstance(ticket, Mapping)
        }
        metric_sets = body.get("metric_sets")
        if tickets_updated_at and metric_sets is None:
            # The page lists tickets but carries no side-load at all: Zendesk ignored `include=metric_sets`.
            # Without this warning the stream would report success with no records and a frozen state.
            logger.warning(
                "The ticket list page carries no `metric_sets` side-load although it lists %d tickets; "
                "`ticket_metrics` emits nothing for this page.",
                len(tickets_updated_at),
            )

        records = []
        for metric_set in metric_sets or []:
            cursor_value = _to_unix_timestamp(tickets_updated_at.get(metric_set.get("ticket_id")))
            if cursor_value is None:
                cursor_value = _to_unix_timestamp(metric_set.get("updated_at"))
            if cursor_value is not None:
                metric_set["_ab_updated_at"] = cursor_value
            records.append(metric_set)
        return records


class TicketMetricsStateMigration(StateMigration):
    """Converts a `ticket_metrics` state written before this change into the flat `_ab_updated_at` cursor.

    Before 6.0.0 `ticket_metrics` was a `StateDelegatingStream`. Its full-refresh path (`GET
    /ticket_metrics`) wrote `{"_ab_updated_at": "<epoch>"}`, the newest metric set `updated_at` it
    read, which is the shape this stream saves and is left alone. Its incremental path was a per-ticket
    substream of `tickets`, so its state has the per-partition shape, with the parent cursor under
    `parent_state`:

        {"use_global_cursor": false, "lookback_window": 0,
         "state": {"_ab_updated_at": "<epoch>"},
         "states": [{"partition": {"ticket_id": 1, "parent_slice": {}}, "cursor": {"_ab_updated_at": "<epoch>"}}],
         "parent_state": {"tickets": {"generated_timestamp": "<epoch>"}}}   # 5.5.0 to 5.7.0 (export parent)
         "parent_state": {"tickets": {"updated_at": "<epoch>"}}}            # 5.2.0 to 5.4.x and the 6.0.0 branch

    The stream now walks the ticket list like `tickets` and cursors on the ticket's `updated_at`, so
    the resume point is the parent `tickets` cursor: with `incremental_dependency` the CDK only
    advanced `parent_state` once every ticket before it had its metrics read, while the global `state`
    kept the previous sync's value between checkpoints. A 6.0.0 parent cursor (`updated_at`) is used
    as is. A 5.x parent cursor (`generated_timestamp`) gets the one-hour rewind of
    `TicketsStateMigration`, so the first sync after the upgrade reaches the same tickets as `tickets`
    does. The CDK runs a stream's own migrations on its full state and only runs a parent's migrations
    on `parent_state` while building a substream; this stream has no parent any more, so this
    migration always sees the raw parent cursor and handles both keys itself. Without a parent cursor
    the fallback is the saved `_ab_updated_at` (the global `state`, or a flat value next to other
    keys) or a flat `generated_timestamp` (the cursor before 4.3.0); the per-ticket path filled both
    with a ticket's `generated_timestamp`, so they get the same one-hour rewind.

    Any other shape without a usable cursor (for example a full-refresh marker) becomes `{}`, so the
    next sync reads from `start_date` as a first sync does.
    """

    CURSOR_FIELD = "_ab_updated_at"

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return bool(stream_state) and set(stream_state.keys()) != {self.CURSOR_FIELD}

    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.should_migrate(stream_state):
            return stream_state
        cursor_value = self._parent_tickets_cursor(stream_state.get("parent_state"))
        if cursor_value is None:
            generated_timestamp_candidates = (
                _to_unix_timestamp(self._get(stream_state.get("state"), self.CURSOR_FIELD)),
                _to_unix_timestamp(stream_state.get(self.CURSOR_FIELD)),
                _to_unix_timestamp(stream_state.get("generated_timestamp")),
            )
            saved_value = next((value for value in generated_timestamp_candidates if value is not None), None)
            if saved_value is not None:
                cursor_value = max(saved_value - TicketsStateMigration.REWIND_SECONDS, 0)
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
        return _to_unix_timestamp(tickets_state.get("updated_at"))
