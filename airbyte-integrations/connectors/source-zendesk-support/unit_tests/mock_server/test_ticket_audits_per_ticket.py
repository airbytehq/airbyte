# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Tests for the `ticket_audits_per_ticket` stream.

The stream reads GET /tickets/{ticket_id}/audits.json for every ticket returned by the `tickets`
incremental export. It exists because GET /ticket_audits (the `ticket_audits` stream) excludes
archived tickets. It is always discovered; users opt in by selecting it in the catalog.
"""

import json
import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional
from unittest import TestCase
from unittest.mock import patch

import freezegun
import requests
import yaml

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models.declarative_component_schema import HTTPAPIBudget as HTTPAPIBudgetModel
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from ..conftest import _YAML_FILE_PATH, get_source
from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ErrorResponseBuilder,
    TicketAuditsPerTicketResponseBuilder,
    TicketAuditsRecordBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
from .utils import read_stream


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


def _given_tickets(http_mocker: HttpMocker, start_time: int, tickets: List[Dict[str, int]]) -> None:
    """Mock the parent `tickets` incremental export. Each ticket is {"id": ..., "generated_timestamp": ...}."""
    response = TicketsResponseBuilder.tickets_response()
    for ticket in tickets:
        response = response.with_record(
            TicketsRecordBuilder.tickets_record().with_id(ticket["id"]).with_cursor(ticket["generated_timestamp"])
        )
    http_mocker.get(
        ZendeskSupportRequestBuilder.tickets_endpoint(_AUTHENTICATOR).with_start_time(start_time).build(),
        response.build(),
    )


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
            [{"id": 101, "generated_timestamp": start_time + 10}, {"id": 102, "generated_timestamp": start_time + 20}],
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
        _given_tickets(http_mocker, start_time, [{"id": 101, "generated_timestamp": start_time + 10}])
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
        _given_tickets(http_mocker, start_time, [{"id": 101, "generated_timestamp": start_time + 10}])
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
                {"id": 101, "generated_timestamp": start_time + 10},
                {"id": 102, "generated_timestamp": start_time + 20},
                {"id": 103, "generated_timestamp": start_time + 30},
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
        assert state["parent_state"]["tickets"] == {"generated_timestamp": str(start_time + 30)}

    @HttpMocker()
    def test_given_429_with_retry_after_when_read_then_wait_and_retry(self, http_mocker: HttpMocker) -> None:
        """With no `api_budget` policy for this endpoint, Zendesk's 429 + Retry-After is the only throttle."""
        start_time = int(_START_DATE.timestamp())
        _given_tickets(http_mocker, start_time, [{"id": 101, "generated_timestamp": start_time + 10}])
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
            [{"id": 101, "generated_timestamp": start_time + 10}, {"id": 102, "generated_timestamp": latest}],
        )
        _given_audits(http_mocker, 101, [1001])
        _given_audits(http_mocker, 102, [2001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config())

        assert len(output.records) == 2
        state = output.most_recent_state.stream_state.__dict__
        assert output.most_recent_state.stream_descriptor.name == _STREAM_NAME
        assert state["parent_state"]["tickets"] == {"generated_timestamp": str(latest)}
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
                    "parent_state": {"tickets": {"generated_timestamp": str(previous)}},
                },
            )
            .build()
        )
        # The parent export must be requested from the saved parent cursor, not from start_date.
        _given_tickets(
            http_mocker,
            previous,
            [{"id": 101, "generated_timestamp": previous}, {"id": 102, "generated_timestamp": latest}],
        )
        _given_audits(http_mocker, 101, [1001])
        _given_audits(http_mocker, 102, [2001])

        output = read_stream(_STREAM_NAME, SyncMode.incremental, _config(), state)

        assert len(output.errors) == 0
        # A ticket whose generated_timestamp equals the saved cursor is still re-read.
        assert sorted(record.record.data["id"] for record in output.records) == [1001, 2001]
        new_state = output.most_recent_state.stream_state.__dict__
        assert new_state["parent_state"]["tickets"] == {"generated_timestamp": str(latest)}
        assert new_state["state"] == {"_ab_updated_at": str(latest)}


class TestTicketAuditsPerTicketApiBudget(TestCase):
    """Like the per-ticket `ticket_metrics` calls, the per-ticket audits endpoint matches no `api_budget`
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
        # The parent walk still goes through the incremental export policy.
        assert budget.get_matching_policy(self._request("/api/v2/incremental/tickets/cursor.json")) is not None
