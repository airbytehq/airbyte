# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun
import pytest

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse

from .config import ConfigBuilder
from .helpers import given_tickets_with_state
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketMetricsRecordBuilder, TicketMetricsResponseBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
_TWO_YEARS_AGO_DATETIME = _NOW.subtract(timedelta(weeks=104))


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

        state_cursor_value = int(ab_datetime_now().subtract(timedelta(days=2)).timestamp())
        state = StateBuilder().with_stream_state("ticket_metrics", state={"_ab_updated_at": state_cursor_value}).build()
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
        # Note: The stateful ticket_metrics stream uses the parent's generated_timestamp as the cursor
        # (see manifest.yaml transformation: record['generated_timestamp'] if 'generated_timestamp' in record else stream_slice.extra_fields['generated_timestamp'])
        # So the cursor value is the parent's timestamp, not the child's updated_at
        # Flexible assertion: generated_timestamp can be int or string depending on environment
        state_dict = output.most_recent_state.stream_state.__dict__
        expected_timestamp = int(parent_cursor_value.timestamp())

        assert state_dict["lookback_window"] == 0
        assert state_dict["use_global_cursor"] == False
        assert "_ab_updated_at" in state_dict["state"]
        assert len(state_dict["states"]) == 1

        # Check parent_state timestamp (can be int or string)
        actual_generated_ts = state_dict["parent_state"]["tickets"]["generated_timestamp"]
        assert actual_generated_ts == expected_timestamp or actual_generated_ts == str(
            expected_timestamp
        ), f"Expected {expected_timestamp} or '{expected_timestamp}', got {actual_generated_ts}"


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
