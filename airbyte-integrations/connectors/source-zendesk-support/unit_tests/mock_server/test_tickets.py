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
