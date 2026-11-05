# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the `ticket_audits_per_ticket` stream.

The stream reads GET /tickets/{ticket_id}/audits.json for every ticket returned by the `tickets`
incremental export. It exists because GET /ticket_audits (the `ticket_audits` stream) excludes
archived tickets. It is always discovered; users opt in by selecting it in the catalog.
"""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple
from unittest import TestCase
from unittest.mock import patch

import freezegun
import requests
import yaml

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HTTPAPIBudget as HTTPAPIBudgetModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from ..conftest import _YAML_FILE_PATH, get_source
from .config import ConfigBuilder
from .helpers import closed_tickets_search_query, given_closed_ticket_search
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ErrorResponseBuilder,
    TicketAuditsPerTicketResponseBuilder,
    TicketAuditsRecordBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
from .utils import get_log_messages_by_log_level, read_stream


_STREAM_NAME = "ticket_audits_per_ticket"
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


def _given_tickets(
    http_mocker: HttpMocker,
    start_time: int,
    tickets: List[Dict[str, int]],
    closed_tickets: Sequence[Tuple[int, int]] = (),
    closed_query: Optional[str] = None,
    closed_later_pages: Sequence[Sequence[Tuple[int, int]]] = (),
) -> None:
    """Mock both parent walks. Each ticket of the list is {"id": ..., "updated_at": <unix timestamp>}; the
    builder sets `generated_timestamp` to the same instant, which is what `_ab_updated_at` is derived from.

    The list request carries no start time: the parent filters client-side, so a ticket older than
    `start_time` would be dropped before any audits are requested for it. `closed_tickets` are the
    `(id, updated_at)` pairs the `closed_tickets_search` parent returns (archived tickets are only listed
    there); `closed_query` pins the exact search query, otherwise any query matches; `closed_later_pages` are
    the search pages after the first, reached through `links.next`.
    """
    response = TicketsResponseBuilder.tickets_response()
    for ticket in tickets:
        assert ticket["updated_at"] >= start_time
        response = response.with_record(TicketsRecordBuilder.tickets_record().with_id(ticket["id"]).with_cursor(ticket["updated_at"]))
    http_mocker.get(ZendeskSupportRequestBuilder.tickets_endpoint(_AUTHENTICATOR).build(), response.build())
    given_closed_ticket_search(http_mocker, _AUTHENTICATOR, closed_tickets, closed_query, closed_later_pages)


def _audit(audit_id: int, ticket_id: int) -> TicketAuditsRecordBuilder:
    return TicketAuditsRecordBuilder.ticket_audits_record().with_id(audit_id).with_field(FieldPath("ticket_id"), ticket_id)


def _audits_request(ticket_id: int, after_cursor: Optional[str] = None):
    request = ZendeskSupportRequestBuilder.ticket_audits_per_ticket_endpoint(_AUTHENTICATOR, ticket_id).with_page_size(100)
    if after_cursor:
        request = request.with_after_cursor(after_cursor)
    return request.build()


def _given_audits(http_mocker: HttpMocker, ticket_id: int, audit_ids: List[int]) -> None:
    response = TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response()
    for audit_id in audit_ids:
        response = response.with_record(_audit(audit_id, ticket_id))
    http_mocker.get(_audits_request(ticket_id), response.build())


class TestTicketAuditsPerTicketDiscovery(TestCase):
    """The stream is a regular stream: discovered with the default config, with no spec setting of its own."""

    @staticmethod
    def _discovered_streams(config: Dict[str, Any]) -> Dict[str, Any]:
        catalog = get_source(config=config).discover(logging.getLogger("airbyte"), config)
        return {stream.name: stream for stream in catalog.streams}

    def test_given_default_config_when_discover_then_stream_is_present_and_incremental(self) -> None:
        streams = self._discovered_streams(_config())
        assert _STREAM_NAME in streams
        assert "ticket_audits" in streams
        stream = streams[_STREAM_NAME]
        assert stream.source_defined_primary_key == [["id"]]
        assert stream.default_cursor_field == ["_ab_updated_at"]
        assert SyncMode.incremental in stream.supported_sync_modes

    def test_spec_has_no_setting_for_the_stream(self) -> None:
        """Opt-in is stream selection only, and the stream has no rate-limit setting of its own."""
        spec = get_source(config=_config()).spec(logging.getLogger("airbyte"))
        properties = spec.connectionSpecification["properties"]
        assert not [name for name in properties if "audit" in name]

    def test_schema_matches_ticket_audits_plus_cursor_field(self) -> None:
        """The schema $refs every `ticket_audits` property; this guards against the two drifting apart."""
        streams = self._discovered_streams(_config())
        per_ticket_properties = dict(streams[_STREAM_NAME].json_schema["properties"])
        assert per_ticket_properties.pop("_ab_updated_at")["type"] == ["null", "integer"]
        assert per_ticket_properties == streams["ticket_audits"].json_schema["properties"]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsPerTicketRead(TestCase):
    @HttpMocker()
    def test_given_tickets_when_read_then_return_audits_for_each_ticket_with_parent_cursor(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(
            http_mocker,
            start_time,
            [{"id": 101, "updated_at": start_time + 10}, {"id": 102, "updated_at": start_time + 20}],
        )
        _given_audits(http_mocker, 101, [1001, 1002])
        _given_audits(http_mocker, 102, [2001])

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert set(records) == {1001, 1002, 2001}
        assert records[1001]["ticket_id"] == 101
        assert records[1001]["_ab_updated_at"] == start_time + 10
        assert records[2001]["_ab_updated_at"] == start_time + 20

    @HttpMocker()
    def test_given_has_more_when_read_then_follow_links_next_until_has_more_is_false(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, start_time, [{"id": 101, "updated_at": start_time + 10}])
        next_page_url = "https://d3v-airbyte.zendesk.com/api/v2/tickets/101/audits.json?page%5Bafter%5D=after-cursor&page%5Bsize%5D=100"
        http_mocker.get(
            _audits_request(101),
            TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response(next_page_url)
            .with_record(_audit(1001, 101))
            .with_pagination()
            .build(),
        )
        # The template's last page has meta.has_more = false, which must stop pagination.
        http_mocker.get(
            _audits_request(101, after_cursor="after-cursor"),
            TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response().with_record(_audit(1002, 101)).build(),
        )

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002]

    @HttpMocker()
    def test_given_unpaginated_archived_ticket_response_when_read_then_read_one_page(self, http_mocker: HttpMocker) -> None:
        """Zendesk returns audits for archived tickets unpaginated, without `meta`/`links`; read it as one page."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, start_time, [{"id": 101, "updated_at": start_time + 10}])
        archived_body = {
            "audits": [_audit(1001, 101).build(), _audit(1002, 101).build()],
            "next_page": None,
            "previous_page": None,
            "count": 2,
        }
        http_mocker.get(_audits_request(101), HttpResponse(json.dumps(archived_body), 200))

        output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1002]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsPerTicketErrorHandling(TestCase):
    @HttpMocker()
    def test_given_403_and_404_for_some_tickets_when_read_then_skip_them_and_read_the_rest(self, http_mocker: HttpMocker) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(
            http_mocker,
            start_time,
            [
                {"id": 101, "updated_at": start_time + 10},
                {"id": 102, "updated_at": start_time + 20},
                {"id": 103, "updated_at": start_time + 30},
            ],
        )
        # Zendesk can send a refusal with an empty, non-JSON body, so the filter must key on the status code.
        http_mocker.get(_audits_request(101), ErrorResponseBuilder.response_with_status(403).with_empty_html_body().build())
        http_mocker.get(_audits_request(102), ErrorResponseBuilder.response_with_status(404).build())
        _given_audits(http_mocker, 103, [3001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert [record.record.data["id"] for record in output.records] == [3001]
        assert len(output.errors) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
        # The ignored tickets must not stop the parent cursor from advancing.
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"]["tickets"] == {"updated_at": str(start_time + 30)}

    @HttpMocker()
    def test_given_429_with_retry_after_when_read_then_wait_and_retry(self, http_mocker: HttpMocker) -> None:
        """With no `api_budget` policy for this endpoint, Zendesk's 429 + Retry-After is the only throttle."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, start_time, [{"id": 101, "updated_at": start_time + 10}])
        success = TicketAuditsPerTicketResponseBuilder.ticket_audits_per_ticket_response().with_record(_audit(1001, 101)).build()
        http_mocker.get(
            _audits_request(101),
            [HttpResponse(json.dumps({"error": "APIRateLimitExceeded"}), 429, {"Retry-After": "7"}), success],
        )

        with patch("time.sleep") as sleep:
            output = read_stream(_STREAM_NAME, SyncMode.full_refresh, _config())

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1001]
        # The wait comes from the header (the CDK may add up to a second), not from the default exponential backoff.
        assert any(call.args and 7 <= call.args[0] <= 8 for call in sleep.call_args_list)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsPerTicketIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_parent_starts_at_start_date_and_state_tracks_parent_cursor(
        self, http_mocker: HttpMocker
    ) -> None:
        start_time = int(_START_DATE.timestamp())
        latest = start_time + 20
        _given_tickets(
            http_mocker,
            start_time,
            [{"id": 101, "updated_at": start_time + 10}, {"id": 102, "updated_at": latest}],
        )
        _given_audits(http_mocker, 101, [1001])
        _given_audits(http_mocker, 102, [2001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.records) == 2
        state = output.most_recent_state.stream_state.__dict__
        assert output.most_recent_state.stream_descriptor.name == _STREAM_NAME
        assert state["parent_state"]["tickets"] == {"updated_at": str(latest)}
        assert state["state"] == {"_ab_updated_at": str(latest)}
        # Global substream cursor: one cursor value, no per-ticket entries.
        assert state["use_global_cursor"] is True
        assert not state.get("states")

    @HttpMocker()
    def test_given_state_when_read_then_parent_resumes_from_parent_state_and_state_progresses(self, http_mocker: HttpMocker) -> None:
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
                    "parent_state": {"tickets": {"updated_at": str(previous)}},
                },
            )
            .build()
        )
        # The parent walk resumes from the saved parent cursor (minus its lookback window), not from start_date.
        _given_tickets(
            http_mocker,
            previous,
            [{"id": 101, "updated_at": previous}, {"id": 102, "updated_at": latest}],
        )
        _given_audits(http_mocker, 101, [1001])
        _given_audits(http_mocker, 102, [2001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        # A ticket whose updated_at equals the saved cursor is still re-read.
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 2001]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(latest)}
        assert new_state["state"] == {"_ab_updated_at": str(latest)}

    @HttpMocker()
    def test_given_5_x_parent_state_when_read_then_parent_cursor_is_migrated_onto_updated_at(self, http_mocker: HttpMocker) -> None:
        """`parent_state` written by 5.x carries the parent's old `generated_timestamp` cursor. The tickets
        state migration also runs on it: the value is rewound by one hour (plus the parent's one-hour
        lookback) onto `updated_at`, so a ticket updated shortly before the saved cursor is read again."""
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
        _given_tickets(http_mocker, previous - 7200, [{"id": 101, "updated_at": previous - 7200 + 60}])
        _given_audits(http_mocker, 101, [1001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1001]
        # The cursor never moves backwards: the re-read ticket is older than the migrated value, so the
        # parent state is the migrated value itself (saved cursor minus the one-hour migration rewind).
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(previous - 3600)}


class TestTicketAuditsPerTicketApiBudget(TestCase):
    """Like the other per-ticket endpoints, the per-ticket audits endpoint matches no `api_budget`
    policy: it runs at the connector's concurrency and relies on 429 + Retry-After backoff."""

    @staticmethod
    def _budget(config: Dict[str, Any]):
        manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
        return ModelToComponentFactory().create_component(
            model_type=HTTPAPIBudgetModel, component_definition=manifest["api_budget"], config=config
        )

    @staticmethod
    def _request(path: str) -> requests.PreparedRequest:
        return requests.Request("GET", f"https://d3v-airbyte.zendesk.com{path}").prepare()

    def test_per_ticket_audit_requests_match_no_policy(self) -> None:
        budget = self._budget(_config())
        assert budget.get_matching_policy(self._request("/api/v2/tickets/123/audits.json")) is None
        assert budget.get_matching_policy(self._request("/api/v2/tickets/123/audits.json?page%5Bsize%5D=100")) is None
        assert budget.get_matching_policy(self._request("/api/v2/tickets/123/metrics")) is None
        # The parent walk goes through the ticket list policy, whichever spelling `links.next` uses.
        assert (
            budget.get_matching_policy(self._request("/api/v2/tickets?sort=-updated_at&support_type_scope=all&page%5Bsize%5D=100"))
            is not None
        )
        assert budget.get_matching_policy(self._request("/api/v2/tickets.json?page%5Bafter%5D=abc&page%5Bsize%5D=100")) is not None

    def test_closed_ticket_search_walk_matches_the_search_policy_on_every_page(self) -> None:
        """The second parent walks Export Search Results; its `links.next` URLs end in `.json`, and both
        spellings must share the search policy (one policy per endpoint, shared with `tickets_search`)."""
        budget = self._budget(_config())
        first_page = budget.get_matching_policy(
            self._request(
                "/api/v2/search/export?filter%5Btype%5D=ticket&page%5Bsize%5D=100&query=updated_at%3E%3D2026-01-01T00%3A00%3A00Z+status%3Aclosed"
            )
        )
        next_page = budget.get_matching_policy(
            self._request("/api/v2/search/export.json?filter%5Btype%5D=ticket&page%5Bafter%5D=abc&page%5Bsize%5D=100")
        )
        assert first_page is not None
        assert next_page is first_page
        assert budget.get_matching_policy(self._request("/api/v2/search?query=type%3Aticket")) is not first_page


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsPerTicketArchivedTickets(TestCase):
    """The partition router has a second parent, `closed_tickets_search`: an Export Search of the closed
    tickets updated since its cursor. The ticket list never returns an archived ticket, so that walk is how
    archived tickets (and the audits they gain after being archived) are reached."""

    @HttpMocker()
    def test_given_no_state_when_read_then_the_search_walk_starts_at_start_date_and_the_archived_ticket_is_read(
        self, http_mocker: HttpMocker
    ) -> None:
        start_time = int(_START_DATE.timestamp())
        _given_tickets(
            http_mocker,
            start_time,
            [{"id": 101, "updated_at": start_time + 10}],
            closed_tickets=[(185, start_time + 5)],
            closed_query=closed_tickets_search_query(start_time, int(_NOW.timestamp())),
        )
        _given_audits(http_mocker, 101, [1001])
        _given_audits(http_mocker, 185, [1851])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        records = {record.record.data["id"]: record.record.data for record in output.records}
        assert sorted(records) == [1001, 1851]
        # The search record's `generated_timestamp` feeds `_ab_updated_at`, as the list's does.
        assert records[1851]["_ab_updated_at"] == start_time + 5
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"] == {
            "tickets": {"updated_at": str(start_time + 10)},
            "closed_tickets_search": {"updated_at": str(start_time + 5)},
        }
        assert state["state"] == {"_ab_updated_at": str(start_time + 10)}

    @HttpMocker()
    def test_given_closed_ticket_listed_by_both_parents_when_read_then_its_audits_are_still_emitted(self, http_mocker: HttpMocker) -> None:
        """A closed ticket that is not archived yet is returned by the list and by the search. The per-partition
        cursor skips the second copy while the first is still being processed and reads it again otherwise, so
        the audits come back once or twice; `id` deduplicates downstream."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, start_time, [{"id": 101, "updated_at": start_time + 10}], closed_tickets=[(101, start_time + 10)])
        _given_audits(http_mocker, 101, [1001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert {record.record.data["id"] for record in output.records} == {1001}
        assert 1 <= len(output.records) <= 2
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"] == {
            "tickets": {"updated_at": str(start_time + 10)},
            "closed_tickets_search": {"updated_at": str(start_time + 10)},
        }

    @HttpMocker()
    def test_given_5_7_state_when_read_then_the_search_parent_is_seeded_from_the_global_cursor(self, http_mocker: HttpMocker) -> None:
        """A 5.7.0 state carries `parent_state.tickets` only. The CDK hands the search parent the global
        cursor instead, and `ClosedTicketsSearchStateMigration` re-keys it onto `updated_at` minus one hour, so
        with the parent's one-hour lookback the search walk starts two hours before the saved cursor rather
        than at `start_date`."""
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
        _given_tickets(
            http_mocker,
            previous - 7200,
            [{"id": 101, "updated_at": previous - 1800}],
            closed_tickets=[(185, previous - 3000)],
            closed_query=closed_tickets_search_query(previous - 7200, int(_NOW.timestamp())),
        )
        _given_audits(http_mocker, 101, [1001])
        _given_audits(http_mocker, 185, [1851])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 1851]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["parent_state"]["tickets"] == {"updated_at": str(previous - 1800)}
        assert new_state["parent_state"]["closed_tickets_search"] == {"updated_at": str(previous - 3000)}

    @HttpMocker()
    def test_given_state_with_both_parents_when_read_then_the_search_walk_resumes_from_its_own_cursor(
        self, http_mocker: HttpMocker
    ) -> None:
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        search_previous = previous - 86400
        state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "use_global_cursor": True,
                    "state": {"_ab_updated_at": str(previous)},
                    "lookback_window": 0,
                    "parent_state": {
                        "tickets": {"updated_at": str(previous)},
                        "closed_tickets_search": {"updated_at": str(search_previous)},
                    },
                },
            )
            .build()
        )
        _given_tickets(
            http_mocker,
            previous - 3600,
            [{"id": 101, "updated_at": previous}],
            closed_query=closed_tickets_search_query(search_previous - 3600, int(_NOW.timestamp())),
        )
        _given_audits(http_mocker, 101, [1001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        assert [record.record.data["id"] for record in output.records] == [1001]
        new_state = output.most_recent_state.stream_state.__dict__
        # No closed ticket changed, so the search cursor stays where it was.
        assert new_state["parent_state"]["closed_tickets_search"] == {"updated_at": str(search_previous)}

    @HttpMocker()
    def test_given_two_search_pages_when_read_then_both_pages_tickets_are_read(self, http_mocker: HttpMocker) -> None:
        """The search walk paginates on `links.next`, whose URL spells the path `search/export.json` and repeats
        the query, until a page says `has_more: false`."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(
            http_mocker,
            start_time,
            [],
            closed_tickets=[(185, start_time + 5)],
            closed_query=closed_tickets_search_query(start_time, int(_NOW.timestamp())),
            closed_later_pages=[[(186, start_time + 6)]],
        )
        _given_audits(http_mocker, 185, [1851])
        _given_audits(http_mocker, 186, [1861])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.errors) == 0
        assert sorted(record.record.data["id"] for record in output.records) == [1851, 1861]
        state = output.most_recent_state.stream_state.__dict__
        assert state["parent_state"]["closed_tickets_search"] == {"updated_at": str(start_time + 6)}

    @HttpMocker()
    def test_given_search_forbidden_when_read_then_the_error_names_the_streams_that_need_it(self, http_mocker: HttpMocker) -> None:
        """`closed_tickets_search` is not a stream the user can see, so its 403 names the four streams it serves
        and the permission they need, and it fails the sync rather than silently skipping archived tickets."""
        start_time = int(_START_DATE.timestamp())
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(_AUTHENTICATOR).build(), TicketsResponseBuilder.tickets_response().build()
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_search_endpoint(_AUTHENTICATOR).with_any_query_params().build(),
            ErrorResponseBuilder.response_with_status(403).with_error_message("Forbidden").build(),
        )

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any(
            "Unable to search for updated closed tickets, which the 'ticket_comments', 'ticket_events', 'ticket_metric_events' and "
            "'ticket_audits_per_ticket' streams need to reach archived tickets" in message
            for message in error_logs
        ), error_logs
        assert any("Error message: Forbidden" in message for message in error_logs), error_logs
