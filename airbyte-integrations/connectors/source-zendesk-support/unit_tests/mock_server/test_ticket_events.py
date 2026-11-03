# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""Tests for the `ticket_events` stream.

Since 6.0.0 the stream reads `GET /tickets/{ticket_id}/audits.json` for every ticket the `tickets`
stream returns (an incremental dependency) and maps each audit onto the record shape of the
Incremental Ticket Event Export it replaces.
"""

from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now

from .config import ConfigBuilder
from .helpers import given_ticket_list
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketAuditsPerTicketResponseBuilder, TicketAuditsRecordBuilder
from .utils import datetime_to_string, read_stream


_STREAM_NAME = "ticket_events"
_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_AUTHENTICATOR = ApiTokenAuthenticator(email="user@example.com", password="password")
_EVENTS = [
    {"id": 11, "type": "Create", "field_name": "subject", "value": "Help"},
    {"id": 12, "type": "Comment", "body": "Hello", "public": True, "author_id": 7, "audit_id": 1001},
    {"id": 13, "type": "Notification", "subject": "Request received", "via": {"channel": "rule"}},
]


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


def _audit(audit_id: int, ticket_id: int, created_at: str, events: Optional[List[Dict[str, Any]]] = None) -> TicketAuditsRecordBuilder:
    return (
        TicketAuditsRecordBuilder.ticket_audits_record()
        .with_id(audit_id)
        .with_ticket_id(ticket_id)
        .with_cursor(created_at)
        .with_author_id(7)
        .with_via({"channel": "api", "source": {"from": {}, "to": {}, "rel": None}})
        .with_metadata({"system": {"client": "curl", "ip_address": "198.51.100.7", "location": "Kyiv"}, "custom": {}})
        .with_events(_EVENTS if events is None else events)
    )


def _audits_request(ticket_id: int, after_cursor: Optional[str] = None):
    request = ZendeskSupportRequestBuilder.ticket_events_endpoint(_AUTHENTICATOR, ticket_id).with_page_size(100)
    if after_cursor:
        request = request.with_after_cursor(after_cursor)
    return request.build()


def _given_audits(http_mocker: HttpMocker, ticket_id: int, audits: List[TicketAuditsRecordBuilder]) -> None:
    response = TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response()
    for audit in audits:
        response = response.with_record(audit)
    http_mocker.get(_audits_request(ticket_id), response.build())


def _given_tickets(http_mocker: HttpMocker, tickets: List[Tuple[int, int]]) -> None:
    given_ticket_list(http_mocker, _AUTHENTICATOR, tickets)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketEventsStreamFullRefresh(TestCase):
    @HttpMocker()
    def test_given_audits_when_read_then_map_each_audit_onto_the_export_record_shape(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        created_at = _START_DATE + timedelta(days=1)
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_audits(http_mocker, 101, [_audit(1001, 101, datetime_to_string(created_at))])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 1001
        assert record["ticket_id"] == 101
        assert record["event_type"] == "Audit"
        assert record["created_at"] == datetime_to_string(created_at)
        assert record["timestamp"] == int(created_at.timestamp())
        assert record["updater_id"] == 7
        assert record["via"] == "api"
        # `system` keeps the export's four-key projection; `ip_address` stays only under `metadata`.
        assert record["system"] == {"client": "curl", "latitude": None, "location": "Kyiv", "longitude": None}
        assert record["metadata"]["system"]["ip_address"] == "198.51.100.7"
        assert record["child_events"] == _EVENTS
        assert "events" not in record
        assert "author_id" not in record

    @HttpMocker()
    def test_given_audit_without_via_or_metadata_when_read_then_map_them_to_nulls(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        audit = _audit(1001, 101, _at(_START_DATE, days=1), events=[]).with_via(None).with_metadata({})
        _given_audits(http_mocker, 101, [audit])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        record = output.records[0].record.data
        # The CDK serializer omits top-level null fields from emitted records.
        assert record.get("via") is None
        assert record["system"] == {"client": None, "latitude": None, "location": None, "longitude": None}
        assert record["child_events"] == []

    @HttpMocker()
    def test_given_has_more_when_read_then_follow_links_next_until_has_more_is_false(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        next_page_url = "https://d3v-airbyte.zendesk.com/api/v2/tickets/101/audits.json?page%5Bafter%5D=after-cursor&page%5Bsize%5D=100"
        http_mocker.get(
            _audits_request(101),
            TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response(next_page_url)
            .with_record(_audit(1001, 101, _at(_START_DATE, days=1)))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            _audits_request(101, after_cursor="after-cursor"),
            TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response()
            .with_record(_audit(1002, 101, _at(_START_DATE, days=2)))
            .build(),
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002]

    @HttpMocker()
    def test_given_audits_older_than_start_date_when_read_then_drop_them(self, http_mocker: HttpMocker) -> None:
        """The endpoint returns the whole audit history of the ticket; the record filter keeps only the slice."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_audits(http_mocker, 101, [_audit(1001, 101, _at(_START_DATE, days=-1)), _audit(1002, 101, _at(_START_DATE, days=1))])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1002]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketEventsStreamErrorHandling(TestCase):
    @HttpMocker()
    def test_given_403_and_404_for_some_tickets_when_read_then_skip_them_and_read_the_rest(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(103, start_time + 30), (102, start_time + 20), (101, start_time + 10)])
        http_mocker.get(_audits_request(101), ErrorResponseBuilder.response_with_status(403).with_empty_html_body().build())
        http_mocker.get(_audits_request(102), ErrorResponseBuilder.response_with_status(404).build())
        _given_audits(http_mocker, 103, [_audit(3001, 103, _at(_START_DATE, days=1))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert [record.record.data["id"] for record in output.records] == [3001]
        assert len(output.errors) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 30)}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketEventsStreamIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_state_follows_the_latest_audit_and_the_parent_cursor(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        latest = _START_DATE + timedelta(days=5)
        _given_tickets(http_mocker, [(102, start_time + 20), (101, start_time + 10)])
        _given_audits(http_mocker, 101, [_audit(1001, 101, _at(_START_DATE, days=1))])
        _given_audits(http_mocker, 102, [_audit(2001, 102, datetime_to_string(latest))])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 2
        state = output.most_recent_state.stream_state.__dict__
        assert state["state"] == {"timestamp": str(int(latest.timestamp()))}
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 20)}
        assert state["use_global_cursor"] is True
        assert not state.get("states")

    @HttpMocker()
    def test_given_5_x_state_when_read_then_the_parent_walk_starts_from_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        """A 5.x state is the flat `{"timestamp": "<unix timestamp>"}` cursor of the export. The CDK seeds the
        parent `tickets` cursor from that single value, and every audit of a visited ticket is emitted."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"timestamp": str(previous)}).build()
        _given_tickets(http_mocker, [(101, latest)])
        _given_audits(
            http_mocker,
            101,
            [
                _audit(1001, 101, _at(_START_DATE, days=1)),
                _audit(1002, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30)))),
                _audit(1003, 101, datetime_to_string(_NOW.subtract(timedelta(days=1)))),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        # 1001 and 1002 predate the saved cursor and are emitted anyway: the cursor bounds the parent walk, not the audits.
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002, 1003]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"timestamp": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}

    @HttpMocker()
    def test_given_6_0_state_when_read_then_only_changed_tickets_are_visited_and_all_their_audits_are_re_emitted(
        self, http_mocker: HttpMocker
    ) -> None:
        """A second sync from a 6.0.0 global state: the parent walk resumes from `parent_state` (one hour of lookback),
        unchanged tickets are not visited, and the visited ticket re-emits all of its audits, including ones older
        than the global cursor (a ticket updated during the previous walk is first seen now, and its audits from
        before that walk must not be lost)."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"timestamp": str(previous)},
                    "lookback_window": 0,
                    "parent_state": {"tickets": {"updated_at": str(previous)}},
                },
            )
            .build()
        )
        # 102 is older than the parent cursor minus one hour, so the walk stops before visiting it.
        _given_tickets(http_mocker, [(101, latest), (102, previous - 7200)])
        _given_audits(
            http_mocker,
            101,
            [
                _audit(1001, 101, _at(_START_DATE, days=1)),
                _audit(1002, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30)))),
                _audit(1003, 101, datetime_to_string(_NOW.subtract(timedelta(days=1)))),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002, 1003]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"timestamp": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}
