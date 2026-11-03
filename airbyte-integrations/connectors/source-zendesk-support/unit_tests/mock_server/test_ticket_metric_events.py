# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Tests for the `ticket_metric_events` stream.

Since 6.0.0 the stream reads `GET /tickets/{ticket_id}/metric_events` for every ticket the `tickets`
stream returns (an incremental dependency), instead of the Incremental Ticket Metric Event Export.
The per-ticket response is an object keyed by metric name whose values are the event lists.
"""

from datetime import timedelta
from typing import Any, Dict, List, Tuple
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now

from .config import ConfigBuilder
from .helpers import given_ticket_list
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


def _given_tickets(http_mocker: HttpMocker, tickets: List[Tuple[int, int]]) -> None:
    given_ticket_list(http_mocker, _AUTHENTICATOR, tickets)


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

    @HttpMocker()
    def test_given_ticket_without_events_when_read_then_return_nothing_for_it(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_metric_events(http_mocker, 101, [])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 0

    @HttpMocker()
    def test_given_events_older_than_start_date_when_read_then_drop_them(self, http_mocker: HttpMocker) -> None:
        """The endpoint returns the whole history of the ticket; the record filter keeps only events in the slice."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_metric_events(
            http_mocker,
            101,
            [_event(1001, 101, _at(_START_DATE, days=-1)), _event(1002, 101, _at(_START_DATE, days=1))],
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1002]


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
    def test_given_no_state_when_read_then_state_follows_the_latest_event_and_the_parent_cursor(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        latest_event = _START_DATE + timedelta(days=5)
        _given_tickets(http_mocker, [(102, start_time + 20), (101, start_time + 10)])
        _given_metric_events(http_mocker, 101, [_event(1001, 101, _at(_START_DATE, days=1))])
        _given_metric_events(http_mocker, 102, [_event(2001, 102, datetime_to_string(latest_event))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 2
        assert output.most_recent_state.stream_descriptor.name == _STREAM_NAME
        state = output.most_recent_state.stream_state.__dict__
        assert state["state"] == {"time": str(int(latest_event.timestamp()))}
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 20)}
        # Global substream cursor: one cursor value, no per-ticket entries.
        assert state["use_global_cursor"] is True
        assert not state.get("states")

    @HttpMocker()
    def test_given_state_when_read_then_parent_resumes_from_parent_state_and_old_events_are_dropped(self, http_mocker: HttpMocker) -> None:
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"time": str(previous)},
                    "lookback_window": 0,
                    "parent_state": {"tickets": {"updated_at": str(previous)}},
                },
            )
            .build()
        )
        # The parent walk resumes from the saved parent cursor, not from start_date; the whole history of a
        # changed ticket comes back and events older than the lookback window are dropped again.
        _given_tickets(http_mocker, [(101, latest)])
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
        # 1002 is within the one-hour lookback window of the saved cursor, so it is re-emitted.
        assert sorted(record.record.data["id"] for record in output.records) == [1002, 1003]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"time": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}

    @HttpMocker()
    def test_given_5_x_state_when_read_then_the_parent_walk_starts_from_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        """A 5.x state is the flat `{"time": "<unix timestamp>"}` cursor of the export. The CDK seeds the
        parent `tickets` cursor from that single value, so the first 6.0.0 sync walks the tickets changed
        since the saved cursor instead of every ticket since `start_date`."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"time": str(previous)}).build()
        _given_tickets(http_mocker, [(101, latest)])
        _given_metric_events(
            http_mocker,
            101,
            [_event(1001, 101, _at(_START_DATE, days=1)), _event(1002, 101, datetime_to_string(_NOW.subtract(timedelta(days=1))))],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1002]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"time": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}
