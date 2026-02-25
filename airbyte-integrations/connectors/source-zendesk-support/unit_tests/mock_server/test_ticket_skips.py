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
from .response_builder import TicketSkipsRecordBuilder, TicketSkipsResponseBuilder
from .utils import datetime_to_string, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketSkipsStreamFullRefresh(TestCase):
    """Test ticket_skips stream which is a semi-incremental stream."""

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
    def test_given_one_page_when_read_ticket_skips_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = datetime_to_string(start_date.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_skips_endpoint(api_token_authenticator)
            .with_query_param("sort_order", "desc")
            .with_page_size(100)
            .build(),
            TicketSkipsResponseBuilder.ticket_skips_response()
            .with_record(TicketSkipsRecordBuilder.ticket_skips_record().with_field(FieldPath("updated_at"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_skips", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketSkipsStreamIncremental(TestCase):
    """Test ticket_skips stream incremental sync (semi-incremental behavior)."""

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
    def test_given_no_state_when_read_ticket_skips_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = datetime_to_string(start_date.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_skips_endpoint(api_token_authenticator)
            .with_query_param("sort_order", "desc")
            .with_page_size(100)
            .build(),
            TicketSkipsResponseBuilder.ticket_skips_response()
            .with_record(TicketSkipsRecordBuilder.ticket_skips_record().with_field(FieldPath("updated_at"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_skips", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_skips"

    @HttpMocker()
    def test_given_state_when_read_ticket_skips_then_filter_records_by_state(self, http_mocker):
        """Semi-incremental streams filter records client-side based on state."""
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        old_cursor_value = datetime_to_string(state_cursor_value.subtract(timedelta(days=1)))
        new_cursor_value = datetime_to_string(state_cursor_value.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_skips_endpoint(api_token_authenticator)
            .with_query_param("sort_order", "desc")
            .with_page_size(100)
            .build(),
            TicketSkipsResponseBuilder.ticket_skips_response()
            .with_record(TicketSkipsRecordBuilder.ticket_skips_record().with_id(1).with_field(FieldPath("updated_at"), old_cursor_value))
            .with_record(TicketSkipsRecordBuilder.ticket_skips_record().with_id(2).with_field(FieldPath("updated_at"), new_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_skips", {"updated_at": datetime_to_string(state_cursor_value)}).build()

        output = read_stream("ticket_skips", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 2
        assert output.most_recent_state is not None
