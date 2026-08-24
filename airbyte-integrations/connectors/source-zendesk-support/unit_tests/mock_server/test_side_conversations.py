# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .helpers import given_tickets
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ErrorResponseBuilder,
    SideConversationsRecordBuilder,
    SideConversationsResponseBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
from .utils import datetime_to_string, get_log_messages_by_log_level, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestSideConversationsStreamFullRefresh(TestCase):
    """Test side_conversations stream which is a substream of tickets."""

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
    def test_given_one_page_when_read_side_conversations_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        side_conv_record = SideConversationsRecordBuilder.side_conversations_record().with_field(
            FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1)))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(side_conv_record).build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_multiple_side_conversations_when_read_then_return_all_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        side_conv_record_1 = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("aaaa-1111")
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )
        side_conv_record_2 = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("bbbb-2222")
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=2))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response()
            .with_record(side_conv_record_1)
            .with_record(side_conv_record_2)
            .build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert "aaaa-1111" in record_ids
        assert "bbbb-2222" in record_ids


@freezegun.freeze_time(_NOW.isoformat())
class TestSideConversationsStreamIncremental(TestCase):
    """Test side_conversations stream semi-incremental behavior (client-side filtering)."""

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
    def test_given_records_older_than_start_date_when_read_incremental_then_filter_them_out(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        old_record = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("old-record")
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.subtract(timedelta(days=10))))
        )
        new_record = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("new-record")
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(old_record).with_record(new_record).build(),
        )

        output = read_stream("side_conversations", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "new-record"

    @HttpMocker()
    def test_given_millisecond_timestamps_when_read_incremental_then_cursor_is_parsed_correctly(self, http_mocker):
        """Test that records with millisecond-precision timestamps (e.g. 2025-01-25T18:06:33.677Z)
        are correctly parsed by the cursor and not silently skipped."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        # Use millisecond-precision timestamp format matching real Zendesk API responses
        millis_timestamp = start_date.add(timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%S.677Z")
        record_with_millis = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("millis-record")
            .with_field(FieldPath("updated_at"), millis_timestamp)
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(record_with_millis).build(),
        )

        output = read_stream("side_conversations", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == "millis-record"


@freezegun.freeze_time(_NOW.isoformat())
class TestSideConversationsErrorHandling(TestCase):
    """Test error handling for side_conversations stream.

    The side_conversations stream has an IGNORE error handler for 422 responses,
    since some tickets return 422 Unprocessable Entity when they don't support
    side conversations.
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
    def test_given_422_error_when_read_then_ignore_and_continue(self, http_mocker):
        """Test that 422 errors are gracefully ignored without failing the sync."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        # Mock 422 error response for the side conversations endpoint
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(422).with_error_message("Unknown").build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        # Verify no records returned (error was ignored, not retried endlessly)
        assert len(output.records) == 0

    @HttpMocker()
    def test_given_403_for_one_ticket_when_read_then_skip_partition_and_continue(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        generated_timestamp = int(start_date.timestamp())
        inaccessible_ticket = TicketsRecordBuilder.tickets_record().with_id(1001).with_cursor(generated_timestamp)
        accessible_ticket = TicketsRecordBuilder.tickets_record().with_id(1002).with_cursor(generated_timestamp + 1)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(generated_timestamp).build(),
            TicketsResponseBuilder.tickets_response().with_record(inaccessible_ticket).with_record(accessible_ticket).build(),
        )
        valid_record = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("valid-after-403")
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, 1001).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, 1002).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(valid_record).build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert [record.record.data["id"] for record in output.records] == ["valid-after-403"]

    @HttpMocker()
    def test_given_404_for_one_ticket_when_read_then_skip_partition_and_continue(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        generated_timestamp = int(start_date.timestamp())
        deleted_ticket = TicketsRecordBuilder.tickets_record().with_id(2001).with_cursor(generated_timestamp)
        accessible_ticket = TicketsRecordBuilder.tickets_record().with_id(2002).with_cursor(generated_timestamp + 1)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(generated_timestamp).build(),
            TicketsResponseBuilder.tickets_response().with_record(deleted_ticket).with_record(accessible_ticket).build(),
        )
        valid_record = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("valid-after-404")
            .with_field(FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1))))
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, 2001).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, 2002).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(valid_record).build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert [record.record.data["id"] for record in output.records] == ["valid-after-404"]

    @HttpMocker()
    def test_given_401_for_one_ticket_when_read_then_fail_stream(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        ticket = given_tickets(http_mocker, start_date, api_token_authenticator).build()
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(401).build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("401" in message for message in error_logs)
