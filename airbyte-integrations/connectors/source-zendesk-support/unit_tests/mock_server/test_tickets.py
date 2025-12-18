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
