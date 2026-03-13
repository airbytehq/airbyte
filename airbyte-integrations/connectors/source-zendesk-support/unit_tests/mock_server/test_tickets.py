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
from .response_builder import TicketsRecordBuilder, TicketsResponseBuilder
from .utils import read_stream


_NOW = ab_datetime_now()
# Use a narrow date range (< 30 days) to ensure only 1 partition with P30D step
_START_DATE = _NOW.subtract(timedelta(days=25))


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
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record()).build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_tickets_then_return_all_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        # Build a dummy next-page request to make the first response signal has_more=true.
        # CursorBasedPaginationStrategy sets has_more based on whether next_page_url is provided.
        next_page_request = ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_after_cursor("after-cursor").build()

        # Combine both page responses into a single mock as a list so they are consumed
        # sequentially. Using separate http_mocker.get() calls with with_any_query_params()
        # causes an infinite loop because it matches all requests including the second page.
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_any_query_params().build(),
            [
                TicketsResponseBuilder.tickets_response(next_page_request)
                .with_record(TicketsRecordBuilder.tickets_record().with_id(1))
                .with_pagination()
                .build(),
                TicketsResponseBuilder.tickets_response().with_record(TicketsRecordBuilder.tickets_record().with_id(2)).build(),
            ],
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
        record_updated_at = "2024-08-14T20:21:37Z"

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketsResponseBuilder.tickets_response()
            .with_record(TicketsRecordBuilder.tickets_record().with_field(FieldPath("updated_at"), record_updated_at))
            .build(),
        )

        output = read_stream("tickets", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "tickets"
        assert "updated_at" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_state_when_read_tickets_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        # Use a recent state cursor (within 30 days of NOW) to ensure 1 partition
        state_cursor_value = _NOW.subtract(timedelta(days=5))
        new_updated_at = state_cursor_value.add(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator).with_any_query_params().build(),
            TicketsResponseBuilder.tickets_response()
            .with_record(TicketsRecordBuilder.tickets_record().with_field(FieldPath("updated_at"), new_updated_at))
            .build(),
        )

        state = StateBuilder().with_stream_state("tickets", {"updated_at": str(int(state_cursor_value.timestamp()))}).build()

        output = read_stream("tickets", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "tickets"


# Fixed deterministic datetimes for multi-partition tests.
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
class TestTicketsStreamQueryParameters(TestCase):
    """Test that the tickets stream sends correct query parameters to the Export Search Results API.

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
    def test_when_read_tickets_then_partitions_produce_correct_query_params(self, http_mocker):
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
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator)
            .with_page_size(100)
            .with_query_param("query", _P1_QUERY)
            .with_query_param("filter[type]", "ticket")
            .build(),
            TicketsResponseBuilder.tickets_response()
            .with_record(TicketsRecordBuilder.tickets_record().with_id(1).with_field(FieldPath("updated_at"), "2026-02-01T10:00:00Z"))
            .build(),
        )

        # Mock partition 2 with exact query parameters
        http_mocker.get(
            ZendeskSupportRequestBuilder.tickets_endpoint(api_token_authenticator)
            .with_page_size(100)
            .with_query_param("query", _P2_QUERY)
            .with_query_param("filter[type]", "ticket")
            .build(),
            TicketsResponseBuilder.tickets_response()
            .with_record(TicketsRecordBuilder.tickets_record().with_id(2).with_field(FieldPath("updated_at"), "2026-03-05T10:00:00Z"))
            .build(),
        )

        output = read_stream("tickets", SyncMode.full_refresh, config)

        # Verify records from both partitions were returned
        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1 in record_ids
        assert 2 in record_ids
