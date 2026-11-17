# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse

from .config import ConfigBuilder
from .helpers import given_tickets, given_tickets_with_state
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    ErrorResponseBuilder,
    SideConversationsRecordBuilder,
    SideConversationsResponseBuilder,
    TicketsRecordBuilder,
    TicketsResponseBuilder,
)
from .utils import datetime_to_string, read_stream, string_to_datetime


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
    def test_given_6_0_state_newer_than_the_records_when_read_incremental_then_the_changed_ticket_re_emits_them(self, http_mocker):
        """A ticket updated while the parent walk runs is first listed by the next sync, whose cursor is already past the
        side conversations the ticket gained in between. The filter is bounded by `start_date` only, so they are emitted."""
        api_token_authenticator = self._get_authenticator(self._config)
        previous = int(_NOW.subtract(timedelta(hours=2)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                "side_conversations",
                {
                    "use_global_cursor": True,
                    "state": {"updated_at": datetime_to_string(_NOW.subtract(timedelta(hours=2)))},
                    "lookback_window": 0,
                    "parent_state": {"tickets": {"updated_at": str(previous)}},
                },
            )
            .build()
        )
        ticket_updated_at = ab_datetime_parse(previous + 600)
        ticket = given_tickets_with_state(http_mocker, ticket_updated_at, ticket_updated_at, api_token_authenticator).build()
        record = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("older-than-the-cursor")
            .with_field(FieldPath("updated_at"), datetime_to_string(_NOW.subtract(timedelta(hours=12))))
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(record).build(),
        )

        output = read_stream("side_conversations", SyncMode.incremental, self._config, state)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == ["older-than-the-cursor"]

    @HttpMocker()
    def test_given_5_x_parent_state_when_read_incremental_then_parent_cursor_is_migrated_onto_updated_at(self, http_mocker):
        """`parent_state` written by 5.x carries the parent's old `generated_timestamp` cursor. The tickets
        state migration also runs on it: rewound by one hour onto `updated_at`, so a ticket updated shortly
        before the saved cursor is read again."""
        api_token_authenticator = self._get_authenticator(self._config)
        previous = int(_NOW.subtract(timedelta(days=3)).timestamp())
        state = (
            StateBuilder()
            .with_stream_state(
                "side_conversations",
                {
                    "use_global_cursor": True,
                    "state": {"updated_at": datetime_to_string(_NOW.subtract(timedelta(days=3)))},
                    "lookback_window": 0,
                    "parent_state": {"tickets": {"generated_timestamp": str(previous)}},
                },
            )
            .build()
        )
        ticket_updated_at = ab_datetime_parse(previous - 1800)
        ticket = given_tickets_with_state(http_mocker, ticket_updated_at, ticket_updated_at, api_token_authenticator).build()
        record = (
            SideConversationsRecordBuilder.side_conversations_record()
            .with_id("recent-record")
            .with_field(FieldPath("updated_at"), datetime_to_string(_NOW.subtract(timedelta(days=1))))
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(record).build(),
        )

        output = read_stream("side_conversations", SyncMode.incremental, self._config, state)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == ["recent-record"]
        state_dict = output.most_recent_state.stream_state.__dict__
        # The parent cursor moves on to the re-read ticket, which is newer than the migrated value.
        assert state_dict["parent_state"]["tickets"] == {"updated_at": str(previous - 1800)}

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

    Access to side conversations is granted per ticket, not per stream: the feature requires the
    Collaboration add-on, and access can be further restricted by brand and by group. Zendesk
    therefore refuses individual tickets while the rest of the stream reads normally, so every
    refusal must skip that ticket rather than fail the sync.

    All filters key on the status code. Permission denials from Zendesk's collaboration-api arrive
    as a 403 with an empty `text/html` body, so a filter keyed on the response body cannot match.
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
    def test_given_403_with_empty_html_body_when_read_then_ignore_and_continue(self, http_mocker):
        """A permission denial with an empty `text/html` body must not fail the sync.

        This is the shape Zendesk's collaboration-api actually returns. It is the reason the filter
        cannot key on the response body: there is no body to match against.
        """
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(403).with_empty_html_body().build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_403_when_read_then_ignore_and_continue(self, http_mocker):
        """A permission denial carrying Zendesk's JSON error envelope must also be skipped."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(403).with_error_message("You do not have access to this resource").build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_404_when_read_then_ignore_and_continue(self, http_mocker):
        """A deleted ticket is reachable through the tickets incremental export but its side
        conversations are not, so a 404 must be skipped rather than fail the sync."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        tickets_record_builder = given_tickets(http_mocker, start_date, api_token_authenticator)
        ticket = tickets_record_builder.build()

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, ticket["id"]).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert len(output.records) == 0
        assert len(output.errors) == 0

    @HttpMocker()
    def test_given_one_ticket_denied_when_read_then_other_tickets_still_sync(self, http_mocker):
        """The refusal is per ticket, so a denied ticket must not cost us the readable ones."""
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])

        denied_ticket = TicketsRecordBuilder.tickets_record().with_id(1).with_cursor(int(start_date.timestamp()))
        readable_ticket = TicketsRecordBuilder.tickets_record().with_id(2).with_cursor(int(start_date.timestamp()))
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).build(),
            TicketsResponseBuilder.tickets_response().with_record(denied_ticket).with_record(readable_ticket).build(),
        )

        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, 1).with_per_page(100).build(),
            ErrorResponseBuilder.response_with_status(403).with_empty_html_body().build(),
        )
        side_conv_record = SideConversationsRecordBuilder.side_conversations_record().with_field(
            FieldPath("updated_at"), datetime_to_string(start_date.add(timedelta(days=1)))
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.side_conversations_endpoint(api_token_authenticator, 2).with_per_page(100).build(),
            SideConversationsResponseBuilder.side_conversations_response().with_record(side_conv_record).build(),
        )

        output = read_stream("side_conversations", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1
        assert len(output.errors) == 0
