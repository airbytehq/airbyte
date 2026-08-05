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


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsStreamFullRefresh(TestCase):
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
    def test_given_one_page_when_read_tickets_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record()).build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_tickets_then_return_all_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        first_page_request = (
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build()
        )

        # Build the base URL for cursor-based pagination
        # Note: EndOfStreamPaginationStrategy appends ?cursor={cursor} to this URL
        # Must match the path used by tickets_endpoint: incremental/tickets/cursor.json
        base_url = "https://d3v-airbyte.zendesk.com/api/v2/incremental/tickets/cursor.json"

        http_mocker.get(
            first_page_request,
            TicketsResponseBuilder.tickets_response(base_url, _A_CURSOR)
            .with_record(TicketsRecordBuilder.tickets_record().with_id(1))
            .with_pagination()
            .build(),
        )
        # The connector uses RequestPath pagination, meaning it uses the full URL from after_url
        # The after_url only includes the cursor, not per_page
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_cursor(_A_CURSOR).build(),
            TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record().with_id(2)).build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1 in record_ids
        assert 2 in record_ids


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsStreamIncremental(TestCase):
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
    def test_given_no_state_when_read_tickets_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        cursor_value = 1723660897

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(self._config["start_date"]).build(),
            TicketsResponseBuilder.tickets_response()
            .with_record(TicketsRecordBuilder.tickets_record().with_field(FieldPath("generated_timestamp"), cursor_value))
            .build(),
        )

        output = read_stream("tickets", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "tickets"
        assert "generated_timestamp" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_state_when_read_tickets_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        new_cursor_value = int(state_cursor_value.add(timedelta(days=1)).timestamp())

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(state_cursor_value).build(),
            TicketsResponseBuilder.tickets_response()
            .with_record(TicketsRecordBuilder.tickets_record().with_field(FieldPath("generated_timestamp"), new_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("tickets", {"generated_timestamp": str(int(state_cursor_value.timestamp()))}).build()

        output = read_stream("tickets", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "tickets"


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


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketsStreamStateMigration(TestCase):
    """End-to-end coverage for TicketsStateMigration.

    v5.2.0 shipped a migration that converted state in the opposite direction, so it matters that the
    reverse migration is actually wired into the stream and not merely unit-tested in isolation.
    """

    # 2026-03-01T00:00:00Z -- keep in sync with components.TicketsStateMigration.BACKFILL_FLOOR
    _BACKFILL_FLOOR = 1772323200

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
    def test_given_legacy_updated_at_state_when_read_then_clamp_cursor_to_backfill_floor(self, http_mocker):
        """A cursor left behind by 5.2.0-5.4.x is rewound to the floor so the backfill re-reads the window.

        The exact `start_time` matcher is the assertion: if the migration does not run, or clamps to the
        wrong value, the outgoing request does not match this mock and HttpMocker fails the test.
        """
        api_token_authenticator = self._get_authenticator(self._config)
        record_cursor = self._BACKFILL_FLOOR + 10

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(self._BACKFILL_FLOOR).build(),
            TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record().with_cursor(record_cursor)).build(),
        )

        # A cursor well past the floor, as written by the Export Search Results versions.
        legacy_cursor = str(int(_NOW.subtract(timedelta(days=3)).timestamp()))
        state = StateBuilder().with_stream_state("tickets", {"updated_at": legacy_cursor}).build()

        output = read_stream("tickets", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        # State is re-keyed onto generated_timestamp, so the next sync resumes on the new cursor field.
        assert output.most_recent_state.stream_state.__dict__ == {"generated_timestamp": str(record_cursor)}

    @HttpMocker()
    def test_given_already_migrated_state_when_read_then_cursor_is_not_clamped_again(self, http_mocker):
        """The migration is one-shot: generated_timestamp state must be left alone.

        Without this, every sync would rewind to the floor and re-run the backfill forever.
        """
        api_token_authenticator = self._get_authenticator(self._config)
        cursor = int(_NOW.subtract(timedelta(days=3)).timestamp())

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_start_time(cursor).build(),
            TicketsResponseBuilder.tickets_response().build(),
        )

        state = StateBuilder().with_stream_state("tickets", {"generated_timestamp": str(cursor)}).build()
        output = read_stream("tickets", SyncMode.incremental, self._config, state)

        assert len(output.records) == 0
