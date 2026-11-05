# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Tests for the `ticket_metric_events` stream.

Since 6.0.0 the stream reads `GET /tickets/{ticket_id}/metric_events` for every ticket the `tickets`
stream returns (an incremental dependency), instead of the Incremental Ticket Metric Event Export.
The per-ticket response is an object keyed by metric name whose values are the event lists. The
cursor is `_ab_updated_at`, the parent ticket's `generated_timestamp`: the event `time` is not a
usable cursor because Zendesk dates SLA `breach` events with the future breach moment.
"""

from datetime import timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now

from .config import ConfigBuilder
from .helpers import closed_tickets_search_query, given_closed_ticket_search, given_ticket_list
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketMetricEventsRecordBuilder, TicketMetricEventsResponseBuilder
from .utils import datetime_to_string, read_stream


_STREAM_NAME = "ticket_metric_events"
_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_AUTHENTICATOR = ApiTokenAuthenticator(email="user@example.com", password="password")


def _config() -> Dict[str, Any]:
    return (
        ConfigBuilder()
        .with_basic_auth_credentials("user@example.com", "password")
        .with_subdomain("d3v-airbyte")
        .with_start_date(_START_DATE)
        .build()
    )


def _at(moment: AirbyteDateTime, **delta: int) -> str:
    return datetime_to_string(moment + timedelta(**delta))


def _event(event_id: int, ticket_id: int, time: str, metric: str = "agent_work_time") -> TicketMetricEventsRecordBuilder:
    return (
        TicketMetricEventsRecordBuilder.ticket_metric_events_record()
        .with_id(event_id)
        .with_ticket_id(ticket_id)
        .with_metric(metric)
        .with_cursor(time)
    )


def _given_metric_events(http_mocker: HttpMocker, ticket_id: int, events: List[TicketMetricEventsRecordBuilder]) -> None:
    response = TicketMetricEventsResponseBuilder.ticket_metric_events_response()
    for event in events:
        response = response.with_event(event)
    http_mocker.get(ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(_AUTHENTICATOR, ticket_id).build(), response.build())


def _given_tickets(
    http_mocker: HttpMocker,
    tickets: List[Tuple[int, int]],
    closed_tickets: Sequence[Tuple[int, int]] = (),
    closed_query: Optional[str] = None,
) -> None:
    """Mock both parent walks: the ticket list and the `closed_tickets_search` walk (`closed_tickets`, where
    archived tickets are listed; `closed_query` pins its exact query)."""
    given_ticket_list(http_mocker, _AUTHENTICATOR, tickets)
    given_closed_ticket_search(http_mocker, _AUTHENTICATOR, closed_tickets, closed_query)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsStreamFullRefresh(TestCase):
    @HttpMocker()
    def test_given_tickets_when_read_then_return_the_events_of_every_metric_for_each_ticket(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(102, start_time + 20), (101, start_time + 10)])
        _given_metric_events(
            http_mocker,
            101,
            [_event(1001, 101, _at(_START_DATE, days=1)), _event(1002, 101, _at(_START_DATE, days=2), metric="reply_time")],
        )
        _given_metric_events(http_mocker, 102, [_event(2001, 102, _at(_START_DATE, days=3), metric="resolution_time")])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert set(records) == {1001, 1002, 2001}
        assert records[1002]["metric"] == "reply_time"
        assert records[2001]["ticket_id"] == 102
        # The cursor is the parent ticket's `generated_timestamp`, added to every record.
        assert records[1001]["_ab_updated_at"] == start_time + 10
        assert records[2001]["_ab_updated_at"] == start_time + 20

    @HttpMocker()
    def test_given_ticket_without_events_when_read_then_return_nothing_for_it(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_metric_events(http_mocker, 101, [])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 0

    @HttpMocker()
    def test_given_events_older_than_start_date_when_read_then_keep_the_whole_history_of_the_ticket(self, http_mocker: HttpMocker) -> None:
        """The endpoint returns the whole history of the ticket and no event is filtered by its `time`: the
        parent walk decides which tickets are read, and `id` deduplicates the re-emitted events."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_metric_events(
            http_mocker,
            101,
            [_event(1001, 101, _at(_START_DATE, days=-1)), _event(1002, 101, _at(_START_DATE, days=1))],
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsStreamErrorHandling(TestCase):
    @HttpMocker()
    def test_given_403_and_404_for_some_tickets_when_read_then_skip_them_and_read_the_rest(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(103, start_time + 30), (102, start_time + 20), (101, start_time + 10)])
        # Zendesk can send a refusal with an empty, non-JSON body, so the filter must key on the status code.
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(_AUTHENTICATOR, 101).build(),
            ErrorResponseBuilder.response_with_status(403).with_empty_html_body().build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(_AUTHENTICATOR, 102).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )
        _given_metric_events(http_mocker, 103, [_event(3001, 103, _at(_START_DATE, days=1))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert [record.record.data["id"] for record in output.records] == [3001]
        assert len(output.errors) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The ignored tickets must not stop the parent cursor from advancing.
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 30)}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsStreamIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_state_follows_the_parent_cursor(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(102, start_time + 20), (101, start_time + 10)])
        _given_metric_events(http_mocker, 101, [_event(1001, 101, _at(_START_DATE, days=1))])
        _given_metric_events(http_mocker, 102, [_event(2001, 102, _at(_START_DATE, days=5))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 2
        assert output.most_recent_state.stream_descriptor.name == _STREAM_NAME
        state = output.most_recent_state.stream_state.__dict__
        assert state["state"] == {"_ab_updated_at": str(start_time + 20)}
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 20)}
        # Global substream cursor: one cursor value, no per-ticket entries.
        assert state["use_global_cursor"] is True
        assert not state.get("states")

    @HttpMocker()
    def test_given_breach_event_dated_in_the_future_when_read_then_it_is_emitted_and_the_cursor_stays_on_the_parent(
        self, http_mocker: HttpMocker
    ) -> None:
        """Zendesk records an SLA `breach` event when the policy is applied, dated with the moment the target
        will be breached. The event is emitted like any other, and the saved cursor is the parent ticket's
        `generated_timestamp`, never the event time, so the next sync does not start in the future."""
        updated_at = int(_NOW.subtract(timedelta(minutes=10)).timestamp())
        _given_tickets(http_mocker, [(101, updated_at)])
        _given_metric_events(
            http_mocker,
            101,
            [
                _event(1001, 101, datetime_to_string(_NOW.subtract(timedelta(minutes=10))), metric="reply_time"),
                _event(1002, 101, datetime_to_string(_NOW.add(timedelta(days=2))), metric="reply_time"),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002]
        state = output.most_recent_state.stream_state.__dict__
        assert state["state"] == {"_ab_updated_at": str(updated_at)}
        assert state["parent_state"]["tickets"] == {"updated_at": str(updated_at)}

    @HttpMocker()
    def test_given_state_when_read_then_parent_resumes_from_parent_state_and_the_changed_ticket_re_emits_its_events(
        self, http_mocker: HttpMocker
    ) -> None:
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"_ab_updated_at": str(previous)},
                    "lookback_window": 0,
                    "parent_state": {"tickets": {"updated_at": str(previous)}, "closed_tickets_search": {"updated_at": str(previous)}},
                },
            )
            .build()
        )
        # The parent walks resume from the saved parent cursors, not from start_date; the whole history of a
        # changed ticket comes back, including events older than the saved cursor.
        _given_tickets(http_mocker, [(101, latest)], closed_query=closed_tickets_search_query(previous - 3600))
        _given_metric_events(
            http_mocker,
            101,
            [
                _event(1001, 101, _at(_START_DATE, days=1)),
                _event(1002, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30)))),
                _event(1003, 101, datetime_to_string(_NOW.subtract(timedelta(days=1)))),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002, 1003]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"_ab_updated_at": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}

    @HttpMocker()
    def test_given_5_x_state_when_read_then_the_parent_walk_starts_one_hour_before_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        """A 5.x state is the flat `{"time": "<unix timestamp>"}` cursor of the export. The migration turns
        it into both parent cursors (`tickets` and `closed_tickets_search`), rewound by one hour, so the first
        6.0.0 sync walks the tickets changed since the saved cursor instead of every ticket since `start_date`;
        the search walk starts a further hour earlier (its lookback)."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"time": str(previous)}).build()
        # One ticket updated 30 minutes before the saved cursor (inside the one-hour rewind) and one after.
        _given_tickets(http_mocker, [(102, latest), (101, previous - 1800)], closed_query=closed_tickets_search_query(previous - 7200))
        _given_metric_events(http_mocker, 101, [_event(1001, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30))))])
        _given_metric_events(http_mocker, 102, [_event(2001, 102, datetime_to_string(_NOW.subtract(timedelta(days=1))))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 2001]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"_ab_updated_at": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}
        # No closed ticket was listed, so the search cursor stays at the migrated value.
        assert new_state["parent_state"]["closed_tickets_search"] == {"updated_at": str(previous - 3600)}

    @HttpMocker()
    def test_given_5_x_state_dated_in_the_future_when_read_then_the_parent_walk_starts_from_the_clock(
        self, http_mocker: HttpMocker
    ) -> None:
        """The export returned SLA `breach` events dated with the future breach moment, so a 5.x `time` can
        lie ahead of the sync that saved it. Seeded as-is it would leave the parent walk with an empty
        slice; the migration clamps it to the migration time before the one-hour rewind."""
        future = int(_NOW.add(timedelta(days=2)).timestamp())
        updated_at = int(_NOW.subtract(timedelta(minutes=30)).timestamp())
        now = int(_NOW.timestamp())
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"time": str(future)}).build()
        _given_tickets(http_mocker, [(101, updated_at)], closed_query=closed_tickets_search_query(now - 7200))
        _given_metric_events(http_mocker, 101, [_event(1001, 101, datetime_to_string(_NOW.subtract(timedelta(minutes=30))))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1001]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"_ab_updated_at": str(updated_at)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(updated_at)}
        assert new_state["parent_state"]["closed_tickets_search"] == {"updated_at": str(now - 3600)}

    @HttpMocker()
    def test_given_5_x_parent_state_when_read_then_parent_cursor_is_migrated_onto_updated_at(self, http_mocker: HttpMocker) -> None:
        """A `parent_state` that still carries the parent's old `generated_timestamp` cursor goes through the
        `tickets` state migration: rewound by one hour onto `updated_at`. Such a state predates the
        `closed_tickets_search` parent, which is seeded from the global cursor the same way."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"_ab_updated_at": str(previous)},
                    "lookback_window": 0,
                    "parent_state": {"tickets": {"generated_timestamp": str(previous)}},
                },
            )
            .build()
        )
        _given_tickets(http_mocker, [(101, previous - 1800)], closed_query=closed_tickets_search_query(previous - 7200))
        _given_metric_events(http_mocker, 101, [_event(1001, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30))))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1001]
        new_state = output.most_recent_state.stream_state.__dict__
        # The parent cursor moves on to the re-read ticket, which is newer than the migrated value.
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(previous - 1800)}
        assert new_state["parent_state"]["closed_tickets_search"] == {"updated_at": str(previous - 3600)}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsArchivedTickets(TestCase):
    @HttpMocker()
    def test_given_archived_ticket_listed_by_the_search_parent_when_read_then_its_metric_events_are_emitted(
        self, http_mocker: HttpMocker
    ) -> None:
        """The ticket list never returns an archived ticket; the `closed_tickets_search` parent does, so a new
        connection still backfills the metric events of tickets archived before its first sync."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)], closed_tickets=[(185, start_time + 5)])
        _given_metric_events(http_mocker, 101, [_event(1001, 101, _at(_START_DATE, days=1))])
        _given_metric_events(http_mocker, 185, [_event(1851, 185, _at(_START_DATE, days=2))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert sorted(records) == [1001, 1851]
        assert records[1851]["_ab_updated_at"] == start_time + 5
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"]["closed_tickets_search"] == {"updated_at": str(start_time + 5)}
