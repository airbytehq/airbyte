# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, OAuthBearerAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketMetricSetsResponseBuilder, TicketsRecordBuilder
from .test_oauth_refresh_flow import (
    _INITIAL_ACCESS_TOKEN,
    _INITIAL_REFRESH_TOKEN,
    _NEW_ACCESS_TOKEN,
    _OAUTH_TOKEN_URL,
    _ROTATED_REFRESH_TOKEN,
    _build_oauth_refresh_config,
    _build_token_refresh_response_json,
)
from .utils import get_log_messages_by_log_level, read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"
_ONE_HOUR = 3600

_INVALID_TOKEN_RESPONSE_BODY = {
    "error": "invalid_token",
    "error_description": "The access token provided is expired, revoked, malformed or invalid for other reasons.",
}


def _next_page_url(after_cursor: str) -> str:
    """`links.next` as Zendesk builds it: the original query, `include=metric_sets` included, plus `page[after]`."""
    return (
        "https://d3v-airbyte.zendesk.com/api/v2/tickets"
        f"?include=metric_sets&page%5Bafter%5D={after_cursor}&page%5Bsize%5D=100&sort=-updated_at&support_type_scope=all"
    )


def _config():
    return (
        ConfigBuilder()
        .with_basic_auth_credentials("user@example.com", "password")
        .with_subdomain("d3v-airbyte")
        .with_start_date(_START_DATE)
        .build()
    )


def _authenticator(config):
    return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])


def _ticket(ticket_id: int, updated_at: int) -> TicketsRecordBuilder:
    """A ticket whose `updated_at` and `generated_timestamp` are the same instant."""
    return TicketsRecordBuilder.tickets_record().with_id(ticket_id).with_cursor(updated_at)


def _per_partition_state(parent_cursor: dict, global_cursor: str = "1700000000") -> dict:
    """State of the per-ticket `ticket_metrics` substream of 5.x (`parent_state.tickets.generated_timestamp`)
    and of the 6.0.0 `StateDelegatingStream` (`parent_state.tickets.updated_at`)."""
    return {
        "use_global_cursor": False,
        "lookback_window": 0,
        "state": {"_ab_updated_at": global_cursor},
        "states": [{"partition": {"ticket_id": 35436, "parent_slice": {}}, "cursor": {"_ab_updated_at": global_cursor}}],
        "parent_state": {"tickets": parent_cursor},
    }


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsStream(TestCase):
    """`ticket_metrics` reads `GET /tickets?sort=-updated_at&include=metric_sets&page[size]=100` (newest first),
    emits the page's `metric_sets` stamped with their ticket's `updated_at` (as a unix timestamp) as
    `_ab_updated_at`, and stops paginating once the last ticket of a page is older than the slice start. No
    per-ticket request."""

    @HttpMocker()
    def test_given_one_page_when_read_then_emit_metric_sets_joined_to_their_tickets(self, http_mocker):
        config = _config()
        first_page = ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build()
        start = int(_START_DATE.timestamp())
        http_mocker.get(
            first_page,
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response()
            .with_ticket(_ticket(1, start + 200), metric_set_id=1001, metric_set_updated_at="2020-01-01T00:00:00Z")
            .with_ticket(_ticket(2, start + 100), metric_set_id=2001)
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        records = [r.record.data for r in output.records]
        assert [(r["id"], r["ticket_id"], r["_ab_updated_at"]) for r in records] == [(1001, 1, start + 200), (2001, 2, start + 100)]
        # The metric set's own `updated_at` is not the cursor: it can be far older than the ticket's.
        assert records[0]["updated_at"] == "2020-01-01T00:00:00Z"
        assert "generated_timestamp" not in records[0]
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_given_two_pages_when_read_then_follow_links_next_with_the_side_load(self, http_mocker):
        """A page whose last ticket is still inside the window does not end pagination; `links.next` keeps
        `include=metric_sets`, so the second page side-loads metric sets too."""
        config = _config()
        authenticator = _authenticator(config)
        start = int(_START_DATE.timestamp())

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(authenticator).build(),
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response(_next_page_url(_A_CURSOR))
            .with_ticket(_ticket(1, start + 200))
            .with_ticket(_ticket(2, start + 100))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(authenticator).with_after_cursor(_A_CURSOR).build(),
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response().with_ticket(_ticket(3, start + 50)).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["ticket_id"] for r in output.records] == [1, 2, 3]

    @HttpMocker()
    def test_given_first_sync_when_last_ticket_of_page_older_than_start_date_then_stop_and_drop_its_metric_set(self, http_mocker):
        """A first sync is bounded by `start_date`: the page says `has_more`, but its last ticket was updated
        before `start_date`, so the next page is never requested and that ticket's metric set is dropped."""
        config = _config()
        start = int(_START_DATE.timestamp())
        first_page = ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response(_next_page_url(_A_CURSOR))
            .with_ticket(_ticket(1, start + 10))
            .with_ticket(_ticket(2, start - 10))
            .with_pagination()
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["ticket_id"] for r in output.records] == [1]
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_given_ticket_generated_after_slice_start_but_updated_before_when_read_then_drop_its_metric_set(self, http_mocker):
        """`_ab_updated_at` is the ticket's `updated_at`, not its `generated_timestamp`: a ticket whose
        `generated_timestamp` was bumped after the slice start (a system-only update) but whose `updated_at`
        lies before it ends the walk and is dropped by the record filter, as `tickets` drops the ticket, and
        its `generated_timestamp` does not advance the state."""
        config = _config()
        start = int(_START_DATE.timestamp())
        first_page = ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response(_next_page_url(_A_CURSOR))
            .with_ticket(_ticket(1, start + 10))
            .with_ticket(_ticket(2, start - 10).with_generated_timestamp(start + 5))
            .with_pagination()
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, config)

        assert len(output.errors) == 0
        assert [(r.record.data["ticket_id"], r.record.data["_ab_updated_at"]) for r in output.records] == [(1, start + 10)]
        assert output.most_recent_state.stream_state.__dict__ == {"_ab_updated_at": str(start + 10)}
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_given_ticket_without_metric_set_when_read_then_emit_the_other_metric_sets(self, http_mocker):
        config = _config()
        start = int(_START_DATE.timestamp())
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build(),
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response()
            .with_ticket(_ticket(1, start + 200), with_metric_set=False)
            .with_ticket(_ticket(2, start + 100))
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["ticket_id"] for r in output.records] == [2]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsStreamIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_emit_newest_ticket_updated_at_as_state(self, http_mocker):
        """The state follows the tickets' `updated_at`, like `tickets`; a later `generated_timestamp` (bumped
        by a system-only update during the walk) must not push it past tickets updated meanwhile."""
        config = _config()
        start = int(_START_DATE.timestamp())
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build(),
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response()
            .with_ticket(_ticket(1, start + 100).with_generated_timestamp(start + 150))
            .with_ticket(_ticket(2, start + 50))
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, config)

        assert [r.record.data["_ab_updated_at"] for r in output.records] == [start + 100, start + 50]
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert output.most_recent_state.stream_state.__dict__ == {"_ab_updated_at": str(start + 100)}

    @HttpMocker()
    def test_given_state_when_read_then_apply_lookback_and_drop_older_tickets(self, http_mocker):
        """Metric sets of tickets updated within the one-hour lookback are re-read; older ones are dropped
        and end pagination."""
        config = _config()
        state_cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        first_page = ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response(_next_page_url(_A_CURSOR))
            .with_ticket(_ticket(1, state_cursor + 86400))
            .with_ticket(_ticket(2, state_cursor - 1800))
            .with_ticket(_ticket(3, state_cursor - 7200))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_metrics", {"_ab_updated_at": str(state_cursor)}).build()
        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert [r.record.data["ticket_id"] for r in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.__dict__ == {"_ab_updated_at": str(state_cursor + 86400)}
        http_mocker.assert_number_of_calls(first_page, 1)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsStreamStateMigration(TestCase):
    """End-to-end coverage for TicketMetricsStateMigration: the per-partition state of the former per-ticket
    substream resumes from its parent `tickets` cursor, on the flat `_ab_updated_at` cursor."""

    def _read_with_state(self, http_mocker, stream_state: dict, cursor: int):
        """Mocks one page with a ticket just after the resume point and tickets one hour and two hours
        before it (plus or minus a minute), reads the stream with `stream_state` and returns the ticket ids."""
        config = _config()
        first_page = ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build()
        http_mocker.get(
            first_page,
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response(_next_page_url(_A_CURSOR))
            .with_ticket(_ticket(1, cursor + 60))
            .with_ticket(_ticket(2, cursor - _ONE_HOUR + 60))
            .with_ticket(_ticket(3, cursor - _ONE_HOUR - 60))
            .with_ticket(_ticket(4, cursor - 2 * _ONE_HOUR + 60))
            .with_ticket(_ticket(5, cursor - 2 * _ONE_HOUR - 60))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_metrics", stream_state).build()
        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert output.most_recent_state.stream_state.__dict__ == {"_ab_updated_at": str(cursor + 60)}
        http_mocker.assert_number_of_calls(first_page, 1)
        return [r.record.data["ticket_id"] for r in output.records]

    @HttpMocker()
    def test_given_5_x_per_partition_state_when_read_then_resume_from_parent_generated_timestamp_rewound(self, http_mocker):
        """The 5.x parent cursor (`generated_timestamp`) gets the one-hour rewind `tickets` applies to it and
        the cursor's lookback adds another hour, so tickets updated up to two hours before it are re-read."""
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        state = _per_partition_state({"generated_timestamp": str(cursor)})

        assert self._read_with_state(http_mocker, state, cursor) == [1, 2, 3, 4]

    @HttpMocker()
    def test_given_5_x_global_cursor_state_when_read_then_resume_from_parent_generated_timestamp_rewound(self, http_mocker):
        """Above 10,000 partitions the 5.x cursor switched to a global cursor and dropped `states`."""
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        state = {
            "use_global_cursor": True,
            "lookback_window": 3600,
            "state": {"_ab_updated_at": "1700000000"},
            "parent_state": {"tickets": {"generated_timestamp": str(cursor)}},
        }

        assert self._read_with_state(http_mocker, state, cursor) == [1, 2, 3, 4]

    @HttpMocker()
    def test_given_5_x_state_without_parent_cursor_when_read_then_resume_from_global_cursor_rewound(self, http_mocker):
        """The global `state._ab_updated_at` of 5.x is a ticket's `generated_timestamp` too, so it gets the same
        one-hour rewind when there is no parent cursor to resume from."""
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        state = {"use_global_cursor": True, "lookback_window": 3600, "state": {"_ab_updated_at": str(cursor)}}

        assert self._read_with_state(http_mocker, state, cursor) == [1, 2, 3, 4]

    @HttpMocker()
    def test_given_6_0_0_state_delegating_stream_state_when_read_then_resume_from_parent_updated_at(self, http_mocker):
        """The 6.0.0 per-ticket path saved the parent cursor as `updated_at`, already on the list's sort key:
        it is used as is and only the one-hour lookback applies."""
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        state = _per_partition_state({"updated_at": str(cursor)})

        assert self._read_with_state(http_mocker, state, cursor) == [1, 2]

    @HttpMocker()
    def test_given_flat_cursor_state_when_read_then_state_is_not_rewound_by_the_migration(self, http_mocker):
        """State in the shape this stream saves (also what the 5.x and 6.0.0 full-refresh path wrote) is left
        alone, so the migration is idempotent on it."""
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())

        assert self._read_with_state(http_mocker, {"_ab_updated_at": str(cursor)}, cursor) == [1, 2]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsOAuthTokenRefresh(TestCase):
    """Tests for REFRESH_TOKEN_THEN_RETRY handling of 401 invalid_token on the `ticket_metrics` list request.

    Zendesk rotates single-use refresh tokens, and access tokens can be rejected mid-sync with a
    401 `invalid_token` body (oncall #13609). The OAuth config uses a `token_expiry_date` far in
    the future so that no proactive refresh happens: the refresh must be triggered only by the
    rejected request.
    """

    @property
    def _config(self):
        return _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=(_NOW + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    @staticmethod
    def _state():
        state_cursor = int(_NOW.subtract(timedelta(days=2)).timestamp())
        return StateBuilder().with_stream_state("ticket_metrics", {"_ab_updated_at": str(state_cursor)}).build(), state_cursor

    @staticmethod
    def _invalid_token_response() -> HttpResponse:
        return HttpResponse(json.dumps(_INVALID_TOKEN_RESPONSE_BODY), 401)

    @HttpMocker()
    def test_given_401_invalid_token_when_read_then_refresh_token_and_retry(self, http_mocker):
        state, state_cursor = self._state()
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN)).build(),
            self._invalid_token_response(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)).build(),
            TicketMetricSetsResponseBuilder.tickets_with_metric_sets_response().with_ticket(_ticket(1, state_cursor + 60)).build(),
        )
        token_refresh_matcher = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert token_refresh_matcher.call_count == 1
        assert len(output.errors) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_given_401_after_refresh_when_read_then_fail_without_looping(self, http_mocker):
        """A second 401 after the refresh must fail fast: at most one refresh per request."""
        state, _ = self._state()
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN)).build(),
            self._invalid_token_response(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN)).build(),
            self._invalid_token_response(),
        )
        token_refresh_matcher = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state, expecting_exception=True)

        assert len(output.records) == 0
        assert token_refresh_matcher.call_count == 1
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("401" in msg for msg in error_logs), "Expected 401 error code in logs"

    @HttpMocker()
    def test_given_api_token_401_when_read_then_no_refresh(self, http_mocker):
        """api_token (basic auth) has no refresh token: a 401 must still fail, unchanged."""
        config = _config()
        state, _ = self._state()
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metrics_endpoint(_authenticator(config)).build(),
            ErrorResponseBuilder.response_with_status(401).with_error_message("Couldn't authenticate you").build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("Couldn't authenticate you" in msg for msg in error_logs), "Expected the 401 error message in logs"
