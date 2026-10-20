# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from datetime import timedelta
from typing import Any, Dict, Optional
from unittest import TestCase
from unittest.mock import patch

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, Authenticator, OAuthBearerAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketMetricSetsResponseBuilder
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
_TWO_YEARS_AGO_DATETIME = _NOW.subtract(timedelta(weeks=104))
_EXPORT_URL = "https://d3v-airbyte.zendesk.com/api/v2/incremental/tickets/cursor.json"
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"
# 2026-03-01T00:00:00Z, `TicketsStateMigration.BACKFILL_FLOOR`
_TICKETS_BACKFILL_FLOOR = 1772323200

_INVALID_TOKEN_RESPONSE_BODY = {
    "error": "invalid_token",
    "error_description": "The access token provided is expired, revoked, malformed or invalid for other reasons.",
}


def _config() -> Dict[str, Any]:
    return (
        ConfigBuilder()
        .with_basic_auth_credentials("user@example.com", "password")
        .with_subdomain("d3v-airbyte")
        .with_start_date(_TWO_YEARS_AGO_DATETIME)
        .build()
    )


def _api_token_authenticator() -> ApiTokenAuthenticator:
    return ApiTokenAuthenticator(email="user@example.com", password="password")


def _export_request(authenticator: Authenticator, start_time: Any) -> HttpRequest:
    return ZendeskSupportRequestBuilder.tickets_endpoint(authenticator).with_start_time(start_time).with_include("metric_sets").build()


def _next_page_request(authenticator: Authenticator, cursor: str = _A_CURSOR) -> HttpRequest:
    return ZendeskSupportRequestBuilder.tickets_endpoint(authenticator).with_cursor(cursor).with_include("metric_sets").build()


def _days_ago(days: int) -> int:
    return int(_NOW.subtract(timedelta(days=days)).timestamp())


def _assert_no_per_ticket_requests(http_mocker: HttpMocker) -> None:
    """The stream must only read the export: no `tickets/{id}/metrics` and no `GET /ticket_metrics`."""
    paths = [request.path for request in http_mocker._mocker.request_history]
    assert paths, "Expected at least one request"
    assert all(path == "/api/v2/incremental/tickets/cursor.json" for path in paths), paths


def _state_dict(output) -> Optional[Dict[str, Any]]:
    return output.most_recent_state.stream_state.__dict__ if output.most_recent_state else None


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsFullRefresh(TestCase):
    @HttpMocker()
    def test_given_one_page_when_read_then_emit_side_loaded_metric_sets_with_ticket_generated_timestamp(self, http_mocker):
        config = _config()
        http_mocker.get(
            _export_request(_api_token_authenticator(), config["start_date"]),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response()
            .with_ticket(1, _days_ago(3), metric_set_id=361110475196)
            .with_ticket(2, _days_ago(2), metric_set_id=361593978316)
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert [(r.record.data["id"], r.record.data["ticket_id"], r.record.data["_ab_updated_at"]) for r in output.records] == [
            (361110475196, 1, _days_ago(3)),
            (361593978316, 2, _days_ago(2)),
        ]
        _assert_no_per_ticket_requests(http_mocker)

    @HttpMocker()
    def test_given_archived_and_deleted_tickets_when_read_then_emit_their_metric_sets(self, http_mocker):
        """`GET /ticket_metrics` leaves archived tickets out; the export side-load returns them."""
        config = _config()
        http_mocker.get(
            _export_request(_api_token_authenticator(), config["start_date"]),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response()
            .with_ticket(1, _days_ago(5), status="closed")
            .with_ticket(191, _days_ago(4), status="deleted")
            .with_ticket(192, _days_ago(3), status="open")
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert sorted(r.record.data["ticket_id"] for r in output.records) == [1, 191, 192]

    @HttpMocker()
    def test_given_ticket_without_metric_set_when_read_then_skip_it(self, http_mocker):
        config = _config()
        http_mocker.get(
            _export_request(_api_token_authenticator(), config["start_date"]),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response()
            .with_ticket(1, _days_ago(5))
            .with_ticket(2, _days_ago(4), with_metric_set=False)
            .build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert [r.record.data["ticket_id"] for r in output.records] == [1]

    @HttpMocker()
    def test_given_two_pages_when_read_then_follow_after_url_and_emit_all_metric_sets(self, http_mocker):
        config = _config()
        authenticator = _api_token_authenticator()
        # Zendesk's after_url carries the `include` parameter, as the live API does.
        http_mocker.get(
            _export_request(authenticator, config["start_date"]),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response()
            .with_ticket(1, _days_ago(5))
            .with_next_page(f"{_EXPORT_URL}?cursor={_A_CURSOR}&include=metric_sets")
            .build(),
        )
        http_mocker.get(
            _next_page_request(authenticator),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(2, _days_ago(4)).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert [r.record.data["ticket_id"] for r in output.records] == [1, 2]
        _assert_no_per_ticket_requests(http_mocker)

    @HttpMocker()
    def test_given_after_url_without_include_when_read_next_page_then_still_request_metric_sets(self, http_mocker):
        """The `include` request parameter is sent on paginated requests too, so the side-load never drops."""
        config = _config()
        authenticator = _api_token_authenticator()
        http_mocker.get(
            _export_request(authenticator, config["start_date"]),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response()
            .with_ticket(1, _days_ago(5))
            .with_next_page(f"{_EXPORT_URL}?cursor={_A_CURSOR}")
            .build(),
        )
        http_mocker.get(
            _next_page_request(authenticator),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(2, _days_ago(4)).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config)

        assert [r.record.data["ticket_id"] for r in output.records] == [1, 2]


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_then_start_from_start_date_and_emit_plain_cursor_state(self, http_mocker):
        config = _config()
        authenticator = _api_token_authenticator()
        http_mocker.get(
            _export_request(authenticator, config["start_date"]),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response()
            .with_ticket(1, _days_ago(5))
            .with_next_page(f"{_EXPORT_URL}?cursor={_A_CURSOR}&include=metric_sets")
            .build(),
        )
        http_mocker.get(
            _next_page_request(authenticator),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(2, _days_ago(2)).with_ticket(3, _days_ago(3)).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, config)

        assert len(output.records) == 3
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert _state_dict(output) == {"_ab_updated_at": str(_days_ago(2))}
        _assert_no_per_ticket_requests(http_mocker)

    @HttpMocker()
    def test_given_new_shape_state_when_read_then_resume_from_state_cursor(self, http_mocker):
        config = _config()
        state_cursor = _days_ago(3)
        http_mocker.get(
            _export_request(_api_token_authenticator(), state_cursor),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(1, _days_ago(1)).build(),
        )
        state = StateBuilder().with_stream_state("ticket_metrics", {"_ab_updated_at": str(state_cursor)}).build()

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.records) == 1
        assert _state_dict(output) == {"_ab_updated_at": str(_days_ago(1))}

    @HttpMocker()
    def test_given_integer_state_from_former_full_refresh_path_when_read_then_resume_from_it(self, http_mocker):
        """5.6.x's `GET /ticket_metrics` path wrote `{"_ab_updated_at": <int>}`; it is already a valid cursor."""
        config = _config()
        state_cursor = _days_ago(3)
        http_mocker.get(
            _export_request(_api_token_authenticator(), state_cursor),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(1, _days_ago(1)).build(),
        )
        state = StateBuilder().with_stream_state("ticket_metrics", {"_ab_updated_at": state_cursor}).build()

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.records) == 1
        assert _state_dict(output) == {"_ab_updated_at": str(_days_ago(1))}

    @HttpMocker()
    def test_given_per_partition_state_when_read_then_migrate_and_resume_from_parent_tickets_cursor(self, http_mocker):
        config = _config()
        parent_cursor = _days_ago(2)
        old_state = {
            "use_global_cursor": False,
            "lookback_window": 0,
            # Deliberately older than the parent cursor, as in an intermediate checkpoint.
            "state": {"_ab_updated_at": str(_days_ago(10))},
            "states": [
                {"partition": {"ticket_id": 35436, "parent_slice": {}}, "cursor": {"_ab_updated_at": str(_days_ago(10))}},
            ],
            "parent_state": {"tickets": {"generated_timestamp": str(parent_cursor)}},
        }
        http_mocker.get(
            _export_request(_api_token_authenticator(), parent_cursor),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(1, _days_ago(1)).build(),
        )
        state = StateBuilder().with_stream_state("ticket_metrics", old_state).build()

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.records) == 1
        assert _state_dict(output) == {"_ab_updated_at": str(_days_ago(1))}
        _assert_no_per_ticket_requests(http_mocker)

    @HttpMocker()
    def test_given_global_cursor_state_when_read_then_migrate_and_resume_from_parent_tickets_cursor(self, http_mocker):
        config = _config()
        parent_cursor = _days_ago(2)
        old_state = {
            "use_global_cursor": True,
            "lookback_window": 3600,
            "state": {"_ab_updated_at": str(_days_ago(2))},
            "parent_state": {"tickets": {"generated_timestamp": str(parent_cursor)}},
        }
        http_mocker.get(
            _export_request(_api_token_authenticator(), parent_cursor),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(1, _days_ago(1)).build(),
        )
        state = StateBuilder().with_stream_state("ticket_metrics", old_state).build()

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.records) == 1
        assert _state_dict(output) == {"_ab_updated_at": str(_days_ago(1))}

    @HttpMocker()
    def test_given_per_partition_state_with_legacy_parent_cursor_when_read_then_resume_from_tickets_backfill_floor(self, http_mocker):
        config = _config()
        old_state = {
            "use_global_cursor": False,
            "state": {"_ab_updated_at": str(_days_ago(2))},
            "states": [],
            "parent_state": {"tickets": {"updated_at": str(_days_ago(2))}},
        }
        http_mocker.get(
            _export_request(_api_token_authenticator(), _TICKETS_BACKFILL_FLOOR),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(1, _days_ago(1)).build(),
        )
        state = StateBuilder().with_stream_state("ticket_metrics", old_state).build()

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.records) == 1
        assert _state_dict(output) == {"_ab_updated_at": str(_days_ago(1))}

    @HttpMocker()
    def test_given_state_and_no_new_tickets_when_read_then_keep_state_cursor(self, http_mocker):
        config = _config()
        state_cursor = _days_ago(3)
        http_mocker.get(
            _export_request(_api_token_authenticator(), state_cursor),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().build(),
        )
        state = StateBuilder().with_stream_state("ticket_metrics", {"_ab_updated_at": str(state_cursor)}).build()

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state)

        assert len(output.records) == 0
        assert _state_dict(output) == {"_ab_updated_at": str(state_cursor)}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsErrorHandling(TestCase):
    """The export uses the shared error handler, the same as the `tickets` stream."""

    @HttpMocker()
    def test_given_403_when_read_then_fail_with_config_error(self, http_mocker):
        config = _config()
        http_mocker.get(
            _export_request(_api_token_authenticator(), config["start_date"]),
            ErrorResponseBuilder.response_with_status(403).with_error_message("Forbidden").build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, config, expecting_exception=True)

        assert len(output.records) == 0
        assert output.errors
        assert output.errors[0].trace.error.failure_type.value == "config_error"
        assert "Unable to read data for stream 'ticket_metrics'" in output.errors[0].trace.error.message


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsOAuthTokenRefresh(TestCase):
    """REFRESH_TOKEN_THEN_RETRY on a 401 `invalid_token` from the export request.

    The OAuth config uses a `token_expiry_date` far in the future so that no proactive refresh
    happens: the refresh must be triggered only by the rejected request.
    """

    @property
    def _config(self):
        return _build_oauth_refresh_config(
            refresh_token=_INITIAL_REFRESH_TOKEN,
            access_token=_INITIAL_ACCESS_TOKEN,
            token_expiry_date=(_NOW + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    @staticmethod
    def _state_cursor() -> int:
        return _days_ago(2)

    def _state(self):
        return StateBuilder().with_stream_state("ticket_metrics", {"_ab_updated_at": str(self._state_cursor())}).build()

    @staticmethod
    def _invalid_token_response() -> HttpResponse:
        return HttpResponse(json.dumps(_INVALID_TOKEN_RESPONSE_BODY), 401)

    @HttpMocker()
    def test_given_401_invalid_token_when_read_then_refresh_token_and_retry(self, http_mocker):
        http_mocker.get(
            _export_request(OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN), self._state_cursor()),
            self._invalid_token_response(),
        )
        http_mocker.get(
            _export_request(OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN), self._state_cursor()),
            TicketMetricSetsResponseBuilder.ticket_metric_sets_response().with_ticket(1, _days_ago(1)).build(),
        )
        token_refresh_matcher = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("ticket_metrics", SyncMode.incremental, self._config, self._state())

        assert len(output.records) == 1
        assert token_refresh_matcher.call_count == 1
        assert len(output.errors) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_given_401_after_refresh_when_read_then_fail_without_looping(self, http_mocker):
        """A second 401 after the refresh must fail fast — at most one refresh per request."""
        http_mocker.get(
            _export_request(OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN), self._state_cursor()),
            self._invalid_token_response(),
        )
        http_mocker.get(
            _export_request(OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN), self._state_cursor()),
            self._invalid_token_response(),
        )
        token_refresh_matcher = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("ticket_metrics", SyncMode.incremental, self._config, self._state(), expecting_exception=True)

        assert len(output.records) == 0
        assert token_refresh_matcher.call_count == 1
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("401" in msg for msg in error_logs), "Expected 401 error code in logs"

    @HttpMocker()
    def test_given_api_token_401_when_read_then_no_refresh(self, http_mocker):
        """api_token (basic auth) has no refresh token: a 401 must still fail, unchanged."""
        http_mocker.get(
            _export_request(_api_token_authenticator(), self._state_cursor()),
            ErrorResponseBuilder.response_with_status(401).with_error_message("Couldn't authenticate you").build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, _config(), self._state(), expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("Couldn't authenticate you" in msg for msg in error_logs), "Expected the 401 error message in logs"
