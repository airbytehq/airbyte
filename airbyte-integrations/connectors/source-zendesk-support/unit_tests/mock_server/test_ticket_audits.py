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
from .response_builder import ErrorResponseBuilder, TicketAuditsRecordBuilder, TicketAuditsResponseBuilder
from .utils import datetime_to_string, get_log_messages_by_log_level, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsStreamFullRefresh(TestCase):
    """Test ticket_audits stream which is a semi-incremental stream with error handlers."""

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
    def test_given_one_page_when_read_ticket_audits_then_return_records(self, http_mocker):
        """Test full refresh sync for ticket_audits stream.

        Per manifest.yaml, ticket_audits has:
        - request_parameters: sort_by=created_at, sort_order=desc
        - page_size_option.field_name: "limit" with page_size: 200
        Per playbook: Tests must use .with_query_param() for all static request parameters.

        Note: ticket_audits is a semi-incremental stream that filters records client-side
        based on start_date, so we must set created_at to be after start_date.
        """
        api_token_authenticator = self._get_authenticator(self._config)
        # Record must have created_at after start_date to pass client-side filtering
        cursor_value = datetime_to_string(_START_DATE.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            TicketAuditsResponseBuilder.ticket_audits_response()
            .with_record(TicketAuditsRecordBuilder.ticket_audits_record().with_field(FieldPath("created_at"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_audits", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsStreamIncremental(TestCase):
    """Test ticket_audits stream incremental sync (semi-incremental behavior)."""

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
    def test_given_no_state_when_read_ticket_audits_then_return_records_and_emit_state(self, http_mocker):
        """Test incremental sync with no prior state (first sync).

        Per manifest.yaml, ticket_audits has:
        - request_parameters: sort_by=created_at, sort_order=desc
        - page_size_option.field_name: "limit" with page_size: 200
        """
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = datetime_to_string(start_date.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            TicketAuditsResponseBuilder.ticket_audits_response()
            .with_record(TicketAuditsRecordBuilder.ticket_audits_record().with_field(FieldPath("created_at"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_audits", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_audits"

    @HttpMocker()
    def test_given_state_when_read_ticket_audits_then_filter_records_by_state(self, http_mocker):
        """Semi-incremental streams filter records client-side based on state.

        Per manifest.yaml, ticket_audits has:
        - request_parameters: sort_by=created_at, sort_order=desc
        - page_size_option.field_name: "limit" with page_size: 200
        """
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        old_cursor_value = datetime_to_string(state_cursor_value.subtract(timedelta(days=1)))
        new_cursor_value = datetime_to_string(state_cursor_value.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            TicketAuditsResponseBuilder.ticket_audits_response()
            .with_record(TicketAuditsRecordBuilder.ticket_audits_record().with_id(1).with_field(FieldPath("created_at"), old_cursor_value))
            .with_record(TicketAuditsRecordBuilder.ticket_audits_record().with_id(2).with_field(FieldPath("created_at"), new_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_audits", {"created_at": datetime_to_string(state_cursor_value)}).build()

        output = read_stream("ticket_audits", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 2
        assert output.most_recent_state is not None


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsErrorHandling(TestCase):
    """Test error handling for ticket_audits stream.

    Per manifest.yaml, ticket_audits has FAIL error handlers for:
    - 504: Gateway timeout
    - 403, 404: Permission/not found errors
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
    def test_given_403_error_when_read_ticket_audits_then_fail_with_error_log(self, http_mocker):
        """Test that 403 errors cause the stream to fail with proper error logging.

        Per playbook: FAIL error handlers must assert both error code AND error message.
        Per manifest.yaml, ticket_audits has:
        - request_parameters: sort_by=created_at, sort_order=desc
        - page_size_option.field_name: "limit" with page_size: 200
        """
        api_token_authenticator = self._get_authenticator(self._config)
        error_message = "Forbidden - You do not have access to this resource"

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            ErrorResponseBuilder.response_with_status(403).with_error_message(error_message).build(),
        )

        output = read_stream("ticket_audits", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any(error_message in msg for msg in error_logs), f"Expected error message '{error_message}' in logs"

    @HttpMocker()
    def test_given_404_error_when_read_ticket_audits_then_fail_with_error_log(self, http_mocker):
        """Test that 404 errors cause the stream to fail with proper error logging.

        Per playbook: FAIL error handlers must assert both error code AND error message.
        Per manifest.yaml, ticket_audits has:
        - request_parameters: sort_by=created_at, sort_order=desc
        - page_size_option.field_name: "limit" with page_size: 200
        """
        api_token_authenticator = self._get_authenticator(self._config)
        error_message = "Not Found - The requested resource does not exist"

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            ErrorResponseBuilder.response_with_status(404).with_error_message(error_message).build(),
        )

        output = read_stream("ticket_audits", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any(error_message in msg for msg in error_logs), f"Expected error message '{error_message}' in logs"

    @HttpMocker()
    def test_given_504_error_when_read_ticket_audits_then_fail_with_error_log(self, http_mocker):
        """Test that 504 gateway timeout errors cause the stream to fail with proper error logging.

        Per playbook: FAIL error handlers must assert both error code AND error message.
        Per manifest.yaml, ticket_audits has:
        - request_parameters: sort_by=created_at, sort_order=desc
        - page_size_option.field_name: "limit" with page_size: 200
        """
        api_token_authenticator = self._get_authenticator(self._config)
        error_message = "Gateway Timeout - The server did not respond in time"

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            ErrorResponseBuilder.response_with_status(504).with_error_message(error_message).build(),
        )

        output = read_stream("ticket_audits", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("504" in msg for msg in error_logs), "Expected 504 error code in logs"
        assert any(error_message in msg for msg in error_logs), f"Expected error message '{error_message}' in logs"


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketAuditsDataFeed(TestCase):
    """Test data feed behavior for ticket_audits stream.

    Per manifest.yaml, ticket_audits has is_data_feed: true which means:
    - Pagination should stop when old records are detected
    - If Page 1 contains records older than state, Page 2 should not be fetched
    - Client-side filtering applies even if API returns all records
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
    def test_given_data_feed_with_old_records_when_read_then_stop_pagination(self, http_mocker):
        """Test that pagination stops when old records are detected (is_data_feed: true behavior).

        When is_data_feed is true and records older than state are detected on page 1,
        page 2 should not be fetched because the stream assumes data is sorted by cursor.

        Per playbook: This test proves pagination stops by:
        1. Page 1 includes a before_url signaling there's more data
        2. Page 1 contains a record older than state (triggering is_data_feed stop condition)
        3. Page 2 is NOT mocked - if the connector tries to fetch it, the test fails
        """
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        old_cursor_value = datetime_to_string(state_cursor_value.subtract(timedelta(days=5)))
        new_cursor_value = datetime_to_string(state_cursor_value.add(timedelta(days=1)))
        page_2_url = "https://d3v-airbyte.zendesk.com/api/v2/ticket_audits?cursor=page2"

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_audits_endpoint(api_token_authenticator)
            .with_query_param("sort_by", "created_at")
            .with_query_param("sort_order", "desc")
            .with_query_param("limit", 200)
            .build(),
            TicketAuditsResponseBuilder.ticket_audits_response()
            .with_record(TicketAuditsRecordBuilder.ticket_audits_record().with_id(1).with_field(FieldPath("created_at"), new_cursor_value))
            .with_record(TicketAuditsRecordBuilder.ticket_audits_record().with_id(2).with_field(FieldPath("created_at"), old_cursor_value))
            .with_before_url(page_2_url)
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_audits", {"created_at": datetime_to_string(state_cursor_value)}).build()

        output = read_stream("ticket_audits", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1
