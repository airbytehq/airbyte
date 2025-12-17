# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketFormsRecordBuilder, TicketFormsResponseBuilder
from .utils import datetime_to_string, get_log_messages_by_log_level, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketFormsStreamFullRefresh(TestCase):
    """Test ticket_forms stream which is a semi-incremental stream with error handlers."""

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_ticket_forms_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
            TicketFormsResponseBuilder.ticket_forms_response().with_record(TicketFormsRecordBuilder.ticket_forms_record()).build(),
        )

        output = read_stream("ticket_forms", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketFormsStreamIncremental(TestCase):
    """Test ticket_forms stream incremental sync (semi-incremental behavior)."""

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_no_state_when_read_ticket_forms_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = datetime_to_string(start_date.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
            TicketFormsResponseBuilder.ticket_forms_response()
            .with_record(TicketFormsRecordBuilder.ticket_forms_record().with_field(FieldPath("updated_at"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_forms", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_forms"

    @HttpMocker()
    def test_given_state_when_read_ticket_forms_then_filter_records_by_state(self, http_mocker):
        """Semi-incremental streams filter records client-side based on state."""
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        old_cursor_value = datetime_to_string(state_cursor_value.subtract(timedelta(days=1)))
        new_cursor_value = datetime_to_string(state_cursor_value.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
            TicketFormsResponseBuilder.ticket_forms_response()
            .with_record(TicketFormsRecordBuilder.ticket_forms_record().with_id(1).with_field(FieldPath("updated_at"), old_cursor_value))
            .with_record(TicketFormsRecordBuilder.ticket_forms_record().with_id(2).with_field(FieldPath("updated_at"), new_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_forms", {"updated_at": datetime_to_string(state_cursor_value)}).build()

        output = read_stream("ticket_forms", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 2
        assert output.most_recent_state is not None


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketFormsErrorHandling(TestCase):
    """Test error handling for ticket_forms stream.

    Per manifest.yaml, ticket_forms has FAIL error handlers for 403 and 404.
    This stream used to define enterprise plan, so permission errors should fail.
    Per playbook: FAIL error handlers must assert both error code AND error message.
    """

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_START_DATE)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_403_error_when_read_ticket_forms_then_fail_with_error_log(self, http_mocker):
        """Test that 403 errors cause the stream to fail with proper error logging."""
        api_token_authenticator = self._get_authenticator(self._config)

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("ticket_forms", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"

    @HttpMocker()
    def test_given_404_error_when_read_ticket_forms_then_fail_with_error_log(self, http_mocker):
        """Test that 404 errors cause the stream to fail with proper error logging."""
        api_token_authenticator = self._get_authenticator(self._config)

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_forms_endpoint(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("ticket_forms", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
