# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

"""Tests for the `ticket_comments` stream.

Since 6.0.0 the stream reads `GET /tickets/{ticket_id}/audits.json` for every ticket the `tickets`
stream returns (an incremental dependency) and extracts the Comment events of each audit.
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


_STREAM_NAME = "ticket_comments"
_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_AUTHENTICATOR = ApiTokenAuthenticator(email="user@example.com", password="password")
_VIA = {"channel": "web", "source": {"from": {}, "to": {}, "rel": None}}


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


def _comment(comment_id: int, audit_id: int) -> Dict[str, Any]:
    return {
        "id": comment_id,
        "type": "Comment",
        "author_id": 7,
        "body": "Hello",
        "html_body": "<p>Hello</p>",
        "plain_body": "Hello",
        "public": True,
        "attachments": [],
        "audit_id": audit_id,
    }


def _audit(audit_id: int, ticket_id: int, created_at: str, events: List[Dict[str, Any]]) -> TicketAuditsRecordBuilder:
    return (
        TicketAuditsRecordBuilder.ticket_audits_record()
        .with_id(audit_id)
        .with_ticket_id(ticket_id)
        .with_cursor(created_at)
        .with_via(_VIA)
        .with_events(events)
    )


def _audits_request(ticket_id: int, after_cursor: Optional[str] = None, page_size: int = 100):
    request = ZendeskSupportRequestBuilder.ticket_comments_endpoint(_AUTHENTICATOR, ticket_id).with_page_size(page_size)
    if after_cursor:
        request = request.with_after_cursor(after_cursor)
    return request.build()


def _given_audits(http_mocker: HttpMocker, ticket_id: int, audits: List[TicketAuditsRecordBuilder], page_size: int = 100) -> None:
    response = TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response()
    for audit in audits:
        response = response.with_record(audit)
    http_mocker.get(_audits_request(ticket_id, page_size=page_size), response.build())


def _given_tickets(http_mocker: HttpMocker, tickets: List[Tuple[int, int]]) -> None:
    given_ticket_list(http_mocker, _AUTHENTICATOR, tickets)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamFullRefresh(TestCase):
    @HttpMocker()
    def test_given_audits_when_read_then_return_the_comment_events_with_the_audit_fields(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        created_at = _START_DATE + timedelta(days=1)
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_audits(
            http_mocker,
            101,
            [
                _audit(
                    1001,
                    101,
                    datetime_to_string(created_at),
                    [{"id": 11, "type": "Create", "field_name": "subject", "value": "Help"}, _comment(12, 1001)],
                ),
                _audit(1002, 101, _at(_START_DATE, days=2), [{"id": 21, "type": "Change", "field_name": "status", "value": "open"}]),
                _audit(1003, 101, _at(_START_DATE, days=3), [_comment(31, 1003), {"id": 32, "type": "VoiceComment", "body": "..."}]),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert set(records) == {12, 31}
        comment = records[12]
        assert comment["ticket_id"] == 101
        assert comment["audit_id"] == 1001
        assert comment["created_at"] == datetime_to_string(created_at)
        assert comment["timestamp"] == int(created_at.timestamp())
        assert comment["via"] == _VIA
        assert comment.get("via_reference_id") is None  # always null, and the CDK serializer omits null fields
        assert comment["event_type"] == "Comment"
        assert comment["type"] == "Comment"
        assert comment["body"] == "Hello"
        assert comment["public"] is True

    @HttpMocker()
    def test_given_page_size_in_config_when_read_then_request_audits_with_that_page_size(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_audits(http_mocker, 101, [_audit(1001, 101, _at(_START_DATE, days=1), [_comment(12, 1001)])], page_size=25)

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, {**_config(), "page_size": 25})

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [12]

    @HttpMocker()
    def test_given_page_size_above_the_endpoint_maximum_when_read_then_clamp_it_to_100(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_audits(http_mocker, 101, [_audit(1001, 101, _at(_START_DATE, days=1), [_comment(12, 1001)])], page_size=100)

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, {**_config(), "page_size": 500})

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [12]

    @HttpMocker()
    def test_given_has_more_when_read_then_follow_links_next_until_has_more_is_false(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        next_page_url = "https://d3v-airbyte.zendesk.com/api/v2/tickets/101/audits.json?page%5Bafter%5D=after-cursor&page%5Bsize%5D=100"
        http_mocker.get(
            _audits_request(101),
            TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response(next_page_url)
            .with_record(_audit(1001, 101, _at(_START_DATE, days=1), [_comment(11, 1001)]))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            _audits_request(101, after_cursor="after-cursor"),
            TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response()
            .with_record(_audit(1002, 101, _at(_START_DATE, days=2), [_comment(21, 1002)]))
            .build(),
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [11, 21]

    @HttpMocker()
    def test_given_comments_older_than_start_date_when_read_then_drop_them(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(101, start_time + 10)])
        _given_audits(
            http_mocker,
            101,
            [
                _audit(1001, 101, _at(_START_DATE, days=-1), [_comment(11, 1001)]),
                _audit(1002, 101, _at(_START_DATE, days=1), [_comment(21, 1002)]),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [21]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamErrorHandling(TestCase):
    @HttpMocker()
    def test_given_403_and_404_for_some_tickets_when_read_then_skip_them_and_read_the_rest(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, [(103, start_time + 30), (102, start_time + 20), (101, start_time + 10)])
        http_mocker.get(_audits_request(101), ErrorResponseBuilder.response_with_status(403).with_empty_html_body().build())
        http_mocker.get(_audits_request(102), ErrorResponseBuilder.response_with_status(404).build())
        _given_audits(http_mocker, 103, [_audit(3001, 103, _at(_START_DATE, days=1), [_comment(31, 3001)])])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert [record.record.data["id"] for record in output.records] == [31]
        assert len(output.errors) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 30)}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_state_follows_the_latest_comment_and_the_parent_cursor(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        latest = _START_DATE + timedelta(days=5)
        _given_tickets(http_mocker, [(102, start_time + 20), (101, start_time + 10)])
        _given_audits(http_mocker, 101, [_audit(1001, 101, _at(_START_DATE, days=1), [_comment(11, 1001)])])
        _given_audits(http_mocker, 102, [_audit(2001, 102, datetime_to_string(latest), [_comment(21, 2001)])])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert len(output.records) == 2
        state = output.most_recent_state.stream_state.__dict__
        assert state["state"] == {"created_at": str(int(latest.timestamp()))}
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 20)}
        assert state["use_global_cursor"] is True
        assert not state.get("states")

    @HttpMocker()
    def test_given_5_x_state_when_read_then_the_parent_walk_starts_from_the_saved_cursor(self, http_mocker: HttpMocker) -> None:
        """A 5.x state is the flat `{"created_at": "<unix timestamp>"}` cursor of the export. The CDK seeds the
        parent `tickets` cursor from that single value, and every comment of a visited ticket is emitted."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = StateBuilder().with_stream_state(_STREAM_NAME, {"created_at": str(previous)}).build()
        _given_tickets(http_mocker, [(101, latest)])
        _given_audits(
            http_mocker,
            101,
            [
                _audit(1001, 101, _at(_START_DATE, days=1), [_comment(11, 1001)]),
                _audit(1002, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30))), [_comment(21, 1002)]),
                _audit(1003, 101, datetime_to_string(_NOW.subtract(timedelta(days=1))), [_comment(31, 1003)]),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        # 11 and 21 predate the saved cursor and are emitted anyway: the cursor bounds the parent walk, not the comments.
        assert sorted(record.record.data["id"] for record in output.records) == [11, 21, 31]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"created_at": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}

    @HttpMocker()
    def test_given_6_0_state_when_read_then_only_changed_tickets_are_visited_and_all_their_comments_are_re_emitted(
        self, http_mocker: HttpMocker
    ) -> None:
        """A second sync from a 6.0.0 global state: the parent walk resumes from `parent_state` (one hour of lookback),
        unchanged tickets are not visited, and the visited ticket re-emits all of its comments, including ones older
        than the global cursor (a ticket updated during the previous walk is first seen now, and its comments from
        before that walk must not be lost)."""
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        latest = int(_NOW.subtract(timedelta(days=1)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"created_at": str(previous)},
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
                _audit(1001, 101, _at(_START_DATE, days=1), [_comment(11, 1001)]),
                _audit(1002, 101, datetime_to_string(_NOW.subtract(timedelta(days=3, minutes=30))), [_comment(21, 1002)]),
                _audit(1003, 101, datetime_to_string(_NOW.subtract(timedelta(days=1))), [_comment(31, 1003)]),
            ],
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [11, 21, 31]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["state"] == {"created_at": str(latest)}
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}
