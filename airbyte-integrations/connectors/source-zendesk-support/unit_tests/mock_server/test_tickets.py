# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import (
    TicketsRecordBuilder,
    TicketsResponseBuilder,
    TicketsSearchRecordBuilder,
    TicketsSearchResponseBuilder,
)
from .utils import read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"


def _next_page_url(after_cursor: str) -> str:
    """`links.next` as Zendesk builds it: the original query plus `page[after]`."""
    return f"https://d3v-airbyte.zendesk.com/api/v2/tickets?page%5Bafter%5D={after_cursor}&page%5Bsize%5D=100&sort=-updated_at"


def _tickets_config():
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
    return TicketsRecordBuilder.tickets_record().with_id(ticket_id).with_cursor(updated_at)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsStreamFullRefresh(TestCase):
    """`tickets` reads `GET /tickets?sort=-updated_at&page[size]=100` (newest first) and stops paginating
    once the last ticket of a page is older than the slice start."""

    @HttpMocker()
    def test_given_one_page_when_read_tickets_then_return_records(self, http_mocker):
        config = _tickets_config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(_authenticator(config)).build(),
            TicketsResponseBuilder.tickets_response().with_record(_ticket(1, int(_START_DATE.timestamp()) + 10)).build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, config)

        assert len(output.records) == 1
        record = output.records[0].record.data
        # `fields` is not returned by the ticket list; the stream copies `custom_fields` into it.
        assert record["fields"] == record["custom_fields"]
        assert record["generated_timestamp"] == int(_START_DATE.timestamp()) + 10

    @HttpMocker()
    def test_given_two_pages_when_read_tickets_then_follow_links_next(self, http_mocker):
        """A page whose last ticket is still inside the window does not end pagination."""
        config = _tickets_config()
        authenticator = _authenticator(config)
        start = int(_START_DATE.timestamp())

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(authenticator).build(),
            TicketsResponseBuilder.tickets_response(_next_page_url(_A_CURSOR))
            .with_record(_ticket(1, start + 200))
            .with_record(_ticket(2, start + 100))
            .with_pagination()
            .build(),
        )
        # `links.next` is requested as-is (RequestPath); the CDK drops the query parameters it already carries.
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(authenticator).with_after_cursor(_A_CURSOR).build(),
            TicketsResponseBuilder.tickets_response().with_record(_ticket(3, start + 50)).build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [1, 2, 3]

    @HttpMocker()
    def test_given_last_ticket_of_page_older_than_start_date_when_read_then_stop_paginating(self, http_mocker):
        """The stop condition reads the page, not the filtered records: the page says `has_more`, but its
        last ticket is already older than `start_date`, so the next page is never requested. The old ticket
        itself is filtered out client-side."""
        config = _tickets_config()
        start = int(_START_DATE.timestamp())
        first_page = ZendeskSupportRequestBuilder.tickets_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketsResponseBuilder.tickets_response(_next_page_url(_A_CURSOR))
            .with_record(_ticket(1, start + 10))
            .with_record(_ticket(2, start - 10))
            .with_pagination()
            .build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1]
        http_mocker.assert_number_of_calls(first_page, 1)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsStreamIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_tickets_then_emit_updated_at_state(self, http_mocker):
        config = _tickets_config()
        cursor_value = int(_START_DATE.timestamp()) + 10

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(_authenticator(config)).build(),
            TicketsResponseBuilder.tickets_response().with_record(_ticket(1, cursor_value)).build(),
        )

        output = read_stream("tickets", SyncMode.incremental, config)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "tickets"
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(cursor_value)}

    @HttpMocker()
    def test_given_state_when_read_tickets_then_apply_lookback_and_drop_older_tickets(self, http_mocker):
        """Tickets updated within the one-hour lookback are re-read; older ones are dropped and end pagination."""
        config = _tickets_config()
        state_cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        first_page = ZendeskSupportRequestBuilder.tickets_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketsResponseBuilder.tickets_response(_next_page_url(_A_CURSOR))
            .with_record(_ticket(1, state_cursor + 86400))
            .with_record(_ticket(2, state_cursor - 1800))
            .with_record(_ticket(3, state_cursor - 7200))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("tickets", {"updated_at": str(state_cursor)}).build()
        output = read_stream("tickets", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(state_cursor + 86400)}
        http_mocker.assert_number_of_calls(first_page, 1)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsStreamStateMigration(TestCase):
    """End-to-end coverage for TicketsStateMigration: `generated_timestamp` state from 5.x is rewound onto
    the `updated_at` cursor rather than skipped."""

    @HttpMocker()
    def test_given_generated_timestamp_state_when_read_then_rewind_onto_updated_at(self, http_mocker):
        """Migration rewinds by one hour and the cursor's lookback adds another, so a ticket updated up to
        two hours before the saved `generated_timestamp` is re-read; an older one is dropped."""
        config = _tickets_config()
        legacy_cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        first_page = ZendeskSupportRequestBuilder.tickets_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketsResponseBuilder.tickets_response(_next_page_url(_A_CURSOR))
            .with_record(_ticket(1, legacy_cursor + 60))
            .with_record(_ticket(2, legacy_cursor - 7200 + 60))
            .with_record(_ticket(3, legacy_cursor - 7200 - 60))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("tickets", {"generated_timestamp": str(legacy_cursor)}).build()
        output = read_stream("tickets", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(legacy_cursor + 60)}
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_given_updated_at_state_when_read_then_state_is_not_rewound_by_the_migration(self, http_mocker):
        """State that already carries `updated_at` (written by 5.2.x or by 6.0.0) is left alone: only the
        one-hour lookback applies, not the extra migration rewind."""
        config = _tickets_config()
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())
        first_page = ZendeskSupportRequestBuilder.tickets_endpoint(_authenticator(config)).build()

        http_mocker.get(
            first_page,
            TicketsResponseBuilder.tickets_response(_next_page_url(_A_CURSOR))
            .with_record(_ticket(1, cursor - 3600 - 60))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("tickets", {"updated_at": str(cursor)}).build()
        output = read_stream("tickets", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert len(output.records) == 0
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(cursor)}
        http_mocker.assert_number_of_calls(first_page, 1)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsSearchStream(TestCase):
    """The opt-in tickets_search stream keeps the Export Search Results API behavior
    (path search/export, records under `results`, cursor-based pagination)."""

    @property
    def _config(self):
        # Use a narrow date range (< 30 days) so the DatetimeBasedCursor (step P30D) produces a single partition.
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_NOW.subtract(timedelta(days=25)))
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_tickets_search_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_search_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketsSearchResponseBuilder.tickets_search_response().with_record(TicketsSearchRecordBuilder.tickets_search_record()).build(),
        )

        output = read_stream("tickets_search", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_lookback_window_when_read_tickets_search_then_rescan_from_before_the_cursor(self, http_mocker):
        """`ticket_search_lookback_days` re-scans a trailing window before the saved cursor.

        The query lower bound must be the state cursor minus the configured number of days, so a lookback of 7
        days against a cursor of NOW-10d starts the scan at NOW-17d.
        """
        config = (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_NOW.subtract(timedelta(days=25)))
            .build()
        )
        config["ticket_search_lookback_days"] = 7
        api_token_authenticator = self._get_authenticator(config)

        cursor_value = _NOW.subtract(timedelta(days=10))
        expected_lower_bound = cursor_value.subtract(timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
        expected_query = f"updated_at>={expected_lower_bound} updated_at<={_NOW.strftime('%Y-%m-%dT%H:%M:%SZ')}"

        # Exact query matcher: if the lookback window is not applied, this request does not match and
        # HttpMocker fails the test.
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_search_endpoint(api_token_authenticator)
            .with_page_size(100)
            .with_query_param("query", expected_query)
            .with_query_param("filter[type]", "ticket")
            .build(),
            TicketsSearchResponseBuilder.tickets_search_response().with_record(TicketsSearchRecordBuilder.tickets_search_record()).build(),
        )

        state = StateBuilder().with_stream_state("tickets_search", {"updated_at": str(int(cursor_value.timestamp()))}).build()
        output = read_stream("tickets_search", SyncMode.incremental, config, state)

        assert len(output.records) == 1


# Fixed deterministic datetimes for the multi-partition tickets_search tests.
# Using exact ISO strings avoids sub-second precision issues from ab_datetime_now().
# The 45-day range (> 30 days) ensures DatetimeBasedCursor with step P30D creates 2 partitions.
_FIXED_NOW_ISO = "2026-03-10T12:00:00Z"
_FIXED_START_ISO = "2026-01-24T12:00:00Z"  # 45 days before _FIXED_NOW_ISO

# Pre-computed partition boundaries with P30D step and PT1S cursor_granularity:
# DatetimeBasedCursor computes: slice_end = min(start + step - granularity, end_datetime)
#   Partition 1: [2026-01-24T12:00:00Z, 2026-02-23T11:59:59Z]  (start + 30d - 1s)
#   Partition 2: [2026-02-23T12:00:00Z, 2026-03-10T12:00:00Z]  (prev_end + 1s, now)
_P1_QUERY = "updated_at>=2026-01-24T12:00:00Z updated_at<=2026-02-23T11:59:59Z"
_P2_QUERY = "updated_at>=2026-02-23T12:00:00Z updated_at<=2026-03-10T12:00:00Z"


@freezegun.freeze_time(_FIXED_NOW_ISO)
class TestTicketsSearchStreamQueryParameters(TestCase):
    """Test that the tickets_search stream sends correct query parameters to the Export Search Results API.

    Uses a 45-day date range (> 30 days) to produce multiple partitions with the P30D step,
    and verifies:
    1. Each request includes filter[type]=ticket
    2. Each request's query parameter contains correct updated_at date range boundaries in ISO format
    3. The correct number of partition requests are made (2 for a 45-day range with P30D step)
    4. Partition boundaries use [inclusive_start, inclusive_end] semantics with no gaps
    """

    @property
    def _config(self):
        return ConfigBuilder().with_basic_auth_credentials("user@example.com", "password").with_subdomain("d3v-airbyte").build()

    def _build_config_with_start_date(self):
        """Build config with start_date set directly (bypassing AirbyteDateTime conversion)."""
        config = self._config
        config["start_date"] = _FIXED_START_ISO
        return config

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_when_read_tickets_search_then_partitions_produce_correct_query_params(self, http_mocker):
        """Verify multi-partition reads send correct query and filter[type] parameters.

        By using specific query parameter matchers (not with_any_query_params), the test
        will fail if the connector sends malformed queries, wrong date boundaries, or
        omits filter[type]=ticket. If any request doesn't match a registered mock,
        HttpMocker raises an error.
        """
        config = self._build_config_with_start_date()
        api_token_authenticator = self._get_authenticator(config)

        # Mock partition 1 with exact query parameters
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_search_endpoint(api_token_authenticator)
            .with_page_size(100)
            .with_query_param("query", _P1_QUERY)
            .with_query_param("filter[type]", "ticket")
            .build(),
            TicketsSearchResponseBuilder.tickets_search_response()
            .with_record(
                TicketsSearchRecordBuilder.tickets_search_record().with_id(1).with_field(FieldPath("updated_at"), "2026-02-01T10:00:00Z")
            )
            .build(),
        )

        # Mock partition 2 with exact query parameters
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_search_endpoint(api_token_authenticator)
            .with_page_size(100)
            .with_query_param("query", _P2_QUERY)
            .with_query_param("filter[type]", "ticket")
            .build(),
            TicketsSearchResponseBuilder.tickets_search_response()
            .with_record(
                TicketsSearchRecordBuilder.tickets_search_record().with_id(2).with_field(FieldPath("updated_at"), "2026-03-05T10:00:00Z")
            )
            .build(),
        )

        output = read_stream("tickets_search", SyncMode.full_refresh, config)

        # Verify records from both partitions were returned
        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1 in record_ids
        assert 2 in record_ids
