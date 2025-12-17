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
from .response_builder import TicketCommentsRecordBuilder, TicketCommentsResponseBuilder
from .utils import datetime_to_string, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamFullRefresh(TestCase):
    """Test ticket_comments stream which uses incremental/ticket_events.json endpoint with custom extractor."""

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
    def test_given_one_page_when_read_ticket_comments_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_query_param("include", "comment_events")
            .build(),
            TicketCommentsResponseBuilder.ticket_comments_response()
            .with_record(TicketCommentsRecordBuilder.ticket_comments_record())
            .build(),
        )

        output = read_stream("ticket_comments", SyncMode.full_refresh, self._config)

        assert len(output.records) >= 1


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketCommentsStreamIncremental(TestCase):
    """Test ticket_comments stream incremental sync."""

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
    def test_given_no_state_when_read_ticket_comments_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        cursor_value = 1723660897

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_query_param("include", "comment_events")
            .build(),
            TicketCommentsResponseBuilder.ticket_comments_response()
            .with_record(TicketCommentsRecordBuilder.ticket_comments_record())
            .build(),
        )

        output = read_stream("ticket_comments", SyncMode.incremental, self._config)

        assert len(output.records) >= 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_comments"

    @HttpMocker()
    def test_given_state_when_read_ticket_comments_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_comments_endpoint(api_token_authenticator)
            .with_start_time(state_cursor_value)
            .with_query_param("include", "comment_events")
            .build(),
            TicketCommentsResponseBuilder.ticket_comments_response()
            .with_record(TicketCommentsRecordBuilder.ticket_comments_record())
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_comments", {"timestamp": str(int(state_cursor_value.timestamp()))}).build()

        output = read_stream("ticket_comments", SyncMode.incremental, self._config, state)

        assert len(output.records) >= 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_comments"
