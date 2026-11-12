# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

import freezegun
import pytest

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse

from .config import ConfigBuilder
from .helpers import given_tickets_with_state
from .request_builder import ApiTokenAuthenticator, OAuthBearerAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ErrorResponseBuilder,
    TicketMetricsRecordBuilder,
    TicketMetricsResponseBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
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

_INVALID_TOKEN_RESPONSE_BODY = {
    "error": "invalid_token",
    "error_description": "The access token provided is expired, revoked, malformed or invalid for other reasons.",
}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsFullRefresh(TestCase):
    """Test full refresh sync behavior for ticket_metrics stream.

    Per playbook requirement: All streams should test full refresh sync behavior at minimum.
    """

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_TWO_YEARS_AGO_DATETIME)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_ticket_metrics_then_return_records(self, http_mocker):
        """Test basic full refresh sync returns records."""
        record_updated_at: str = ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        api_token_authenticator = self._get_authenticator(self._config)
        ticket_metrics_record_builder = TicketMetricsRecordBuilder.stateless_ticket_metrics_record().with_cursor(record_updated_at)

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateless_ticket_metrics_endpoint(api_token_authenticator).with_page_size(100).build(),
            TicketMetricsResponseBuilder.stateless_ticket_metrics_response().with_record(ticket_metrics_record_builder).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsIncremental(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_TWO_YEARS_AGO_DATETIME)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_no_state_and_successful_sync_when_read_then_set_state_to_most_recently_read_record_cursor(self, http_mocker):
        record_updated_at: str = ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        api_token_authenticator = self._get_authenticator(self._config)
        ticket_metrics_record_builder = TicketMetricsRecordBuilder.stateless_ticket_metrics_record().with_cursor(record_updated_at)

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateless_ticket_metrics_endpoint(api_token_authenticator).with_page_size(100).build(),
            TicketMetricsResponseBuilder.stateless_ticket_metrics_response().with_record(ticket_metrics_record_builder).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert output.most_recent_state.stream_state.__dict__ == {
            "_ab_updated_at": str(int(ab_datetime_parse(record_updated_at).timestamp()))
        }

    @HttpMocker()
    def test_given_state_when_read_then_migrate_state_to_per_partition(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        state_cursor_value = int(ab_datetime_now().subtract(timedelta(days=3)).timestamp())
        state = StateBuilder().with_stream_state("ticket_metrics", state={"_ab_updated_at": state_cursor_value}).build()
        # Deliberately newer than the seeded state so the resulting parent_state can only come from the
        # parent record's `generated_timestamp`, not from the incoming state value.
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(
            http_mocker, ab_datetime_parse(state_cursor_value), parent_cursor_value, api_token_authenticator
        )
        ticket = tickets_records_builder.build()

        child_cursor_value = ab_datetime_now().subtract(timedelta(days=1))
        child_cursor_str = child_cursor_value.strftime("%Y-%m-%dT%H:%M:%SZ")
        ticket_metrics_first_record_builder = (
            TicketMetricsRecordBuilder.stateful_ticket_metrics_record()
            .with_field(FieldPath("ticket_id"), ticket["id"])
            .with_cursor(child_cursor_str)
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            TicketMetricsResponseBuilder.stateful_ticket_metrics_response().with_record(ticket_metrics_first_record_builder).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        # The stateful ticket_metrics stream derives its `_ab_updated_at` cursor from the parent's
        # `generated_timestamp` (see the AddFields transformation in manifest.yaml), and the parent cursor
        # serialises state with datetime_format "%s", i.e. as a Unix-timestamp string.
        state_dict = output.most_recent_state.stream_state.__dict__

        assert state_dict["lookback_window"] == 0
        assert state_dict["use_global_cursor"] == False
        assert "_ab_updated_at" in state_dict["state"]
        assert len(state_dict["states"]) == 1

        assert state_dict["parent_state"]["tickets"] == {"generated_timestamp": str(int(parent_cursor_value.timestamp()))}


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsErrorHandling(TestCase):
    """Test error handling for ticket_metrics stream.

    The stateful ticket_metrics stream has IGNORE error handlers for 403 and 404 responses.
    Per the playbook, we must verify:
    1. The error is gracefully ignored (no records returned for that partition)
    2. No ERROR logs are produced
    """

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_TWO_YEARS_AGO_DATETIME)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_403_error_when_read_stateful_then_ignore_error_and_no_error_logs(self, http_mocker):
        """Test that 403 errors are gracefully ignored in stateful mode with no ERROR logs."""
        api_token_authenticator = self._get_authenticator(self._config)

        state_cursor_value = int(ab_datetime_now().subtract(timedelta(days=2)).timestamp())
        state = StateBuilder().with_stream_state("ticket_metrics", state={"_ab_updated_at": state_cursor_value}).build()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(
            http_mocker, ab_datetime_parse(state_cursor_value), parent_cursor_value, api_token_authenticator
        )
        ticket = tickets_records_builder.build()

        # Mock 403 error response for the ticket metrics endpoint
        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state)

        # Verify no records returned for this partition (error was ignored)
        assert len(output.records) == 0
        # Verify no ERROR logs were produced (per playbook requirement for IGNORE handlers)
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_given_404_error_when_read_stateful_then_ignore_error_and_no_error_logs(self, http_mocker):
        """Test that 404 errors are gracefully ignored in stateful mode with no ERROR logs."""
        api_token_authenticator = self._get_authenticator(self._config)

        state_cursor_value = int(ab_datetime_now().subtract(timedelta(days=2)).timestamp())
        state = StateBuilder().with_stream_state("ticket_metrics", state={"_ab_updated_at": state_cursor_value}).build()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(
            http_mocker, ab_datetime_parse(state_cursor_value), parent_cursor_value, api_token_authenticator
        )
        ticket = tickets_records_builder.build()

        # Mock 404 error response for the ticket metrics endpoint (ticket was deleted)
        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state)

        # Verify no records returned for this partition (error was ignored)
        assert len(output.records) == 0
        # Verify no ERROR logs were produced (per playbook requirement for IGNORE handlers)
        assert not any(log.log.level == "ERROR" for log in output.logs)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsTransformations(TestCase):
    """Test transformations for ticket_metrics stream.

    The ticket_metrics stream adds _ab_updated_at transformation:
    - Stateless mode: _ab_updated_at = format_datetime(record['updated_at'], '%s')
    - Stateful mode: _ab_updated_at = record['generated_timestamp'] or stream_slice.extra_fields['generated_timestamp']
    """

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_TWO_YEARS_AGO_DATETIME)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_stateless_mode_transformation_adds_ab_updated_at_from_updated_at(self, http_mocker):
        """Test that stateless mode adds _ab_updated_at derived from updated_at field."""
        record_updated_at: str = ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        api_token_authenticator = self._get_authenticator(self._config)
        ticket_metrics_record_builder = TicketMetricsRecordBuilder.stateless_ticket_metrics_record().with_cursor(record_updated_at)

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateless_ticket_metrics_endpoint(api_token_authenticator).with_page_size(100).build(),
            TicketMetricsResponseBuilder.stateless_ticket_metrics_response().with_record(ticket_metrics_record_builder).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        # Verify _ab_updated_at transformation is applied and equals the expected timestamp
        record = output.records[0].record.data
        assert "_ab_updated_at" in record
        expected_timestamp = int(ab_datetime_parse(record_updated_at).timestamp())
        # The transformation returns an integer (value_type: "integer" in manifest)
        assert record["_ab_updated_at"] == expected_timestamp


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsOAuthTokenRefresh(TestCase):
    """Tests for REFRESH_TOKEN_THEN_RETRY handling of 401 invalid_token on the stateful ticket_metrics path.

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

    def _state(self):
        state_cursor_value = int(ab_datetime_now().subtract(timedelta(days=2)).timestamp())
        return StateBuilder().with_stream_state("ticket_metrics", state={"_ab_updated_at": state_cursor_value}).build(), ab_datetime_parse(
            state_cursor_value
        )

    @staticmethod
    def _invalid_token_response() -> HttpResponse:
        return HttpResponse(json.dumps(_INVALID_TOKEN_RESPONSE_BODY), 401)

    @HttpMocker()
    def test_given_401_invalid_token_when_read_stateful_then_refresh_token_and_retry(self, http_mocker):
        state, state_cursor = self._state()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(
            http_mocker, state_cursor, parent_cursor_value, OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN)
        )
        ticket = tickets_records_builder.build()

        ticket_metrics_record_builder = (
            TicketMetricsRecordBuilder.stateful_ticket_metrics_record()
            .with_field(FieldPath("ticket_id"), ticket["id"])
            .with_cursor(ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(
                OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN), ticket["id"]
            ).build(),
            self._invalid_token_response(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(
                OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN), ticket["id"]
            ).build(),
            TicketMetricsResponseBuilder.stateful_ticket_metrics_response().with_record(ticket_metrics_record_builder).build(),
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
    def test_given_concurrent_401s_when_read_then_refresh_token_only_once(self, http_mocker):
        """Zendesk's refresh token is single-use: concurrent 401s must trigger exactly one refresh."""
        state, state_cursor = self._state()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))

        ticket_builders = [
            TicketsRecordBuilder.tickets_record().with_id(ticket_id).with_cursor(int(parent_cursor_value.timestamp()))
            for ticket_id in (1001, 1002, 1003)
        ]
        tickets_response_builder = TicketsResponseBuilder.tickets_response()
        for ticket_builder in ticket_builders:
            tickets_response_builder = tickets_response_builder.with_record(ticket_builder)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN))
            .with_start_time(int(state_cursor.timestamp()))
            .build(),
            tickets_response_builder.build(),
        )

        for ticket_builder in ticket_builders:
            ticket = ticket_builder.build()
            ticket_metrics_record_builder = (
                TicketMetricsRecordBuilder.stateful_ticket_metrics_record()
                .with_field(FieldPath("ticket_id"), ticket["id"])
                .with_cursor(ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
            )
            # Registered on the raw requests_mock so it is allowed to match zero times: depending on
            # worker scheduling, any subset of the partitions may race the stale token before the
            # first refresh lands; requests after it already carry the new token.
            http_mocker._mocker.get(
                f"https://d3v-airbyte.zendesk.com/api/v2/tickets/{ticket['id']}/metrics",
                request_headers={"Authorization": f"Bearer {_INITIAL_ACCESS_TOKEN}"},
                status_code=401,
                text=json.dumps(_INVALID_TOKEN_RESPONSE_BODY),
            )
            http_mocker.get(
                ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(
                    OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN), ticket["id"]
                ).build(),
                TicketMetricsResponseBuilder.stateful_ticket_metrics_response().with_record(ticket_metrics_record_builder).build(),
            )
        token_refresh_matcher = http_mocker._mocker.post(
            _OAUTH_TOKEN_URL,
            text=_build_token_refresh_response_json(_NEW_ACCESS_TOKEN, _ROTATED_REFRESH_TOKEN),
            status_code=200,
        )

        with patch("time.sleep", return_value=None):
            output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state)

        assert len(output.records) == 3
        assert token_refresh_matcher.call_count == 1
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_401_after_refresh_when_read_then_fail_without_looping(self, http_mocker):
        """A second 401 after the refresh must fail fast — at most one refresh per request."""
        state, state_cursor = self._state()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(
            http_mocker, state_cursor, parent_cursor_value, OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN)
        )
        ticket = tickets_records_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(
                OAuthBearerAuthenticator(_INITIAL_ACCESS_TOKEN), ticket["id"]
            ).build(),
            self._invalid_token_response(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(
                OAuthBearerAuthenticator(_NEW_ACCESS_TOKEN), ticket["id"]
            ).build(),
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
        config = (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_TWO_YEARS_AGO_DATETIME)
            .build()
        )
        api_token_authenticator = ApiTokenAuthenticator(email="user@example.com", password="password")

        state, state_cursor = self._state()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(http_mocker, state_cursor, parent_cursor_value, api_token_authenticator)
        ticket = tickets_records_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.stateful_ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            ErrorResponseBuilder.response_with_status(401).with_error_message("Couldn't authenticate you").build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, config, state, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("Couldn't authenticate you" in msg for msg in error_logs), "Expected the 401 error message in logs"
