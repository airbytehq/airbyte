# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketEventsRecordBuilder, TicketEventsResponseBuilder
from .utils import get_log_messages_by_log_level, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"
_PERMISSION_DENIED_BODY = (
    "You do not have access to this page. You do not have permission to access this page. "
    "Please contact the account owner of this help desk for further help."
)


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketEventsStreamFullRefresh(TestCase):
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
    def test_given_one_page_when_read_ticket_events_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build(),
            TicketEventsResponseBuilder.ticket_events_response().with_record(TicketEventsRecordBuilder.ticket_events_record()).build(),
        )

        output = read_stream("ticket_events", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_ticket_events_then_return_all_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        base_url = "https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_events.json"

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build(),
            TicketEventsResponseBuilder.ticket_events_response(base_url, _A_CURSOR)
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_id(1))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator).with_cursor(_A_CURSOR).build(),
            TicketEventsResponseBuilder.ticket_events_response()
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_id(2))
            .build(),
        )

        output = read_stream("ticket_events", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1 in record_ids
        assert 2 in record_ids

    @HttpMocker()
    def test_given_403_permission_denied_when_read_ticket_events_then_fail(self, http_mocker):
        """ticket_events carries Zendesk's core data, so a permission denial must fail instead of reporting an empty sync."""
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build(),
            ErrorResponseBuilder.response_with_status(403).with_error_message(_PERMISSION_DENIED_BODY).build(),
        )

        output = read_stream("ticket_events", SyncMode.full_refresh, self._config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("stream 'ticket_events'" in msg for msg in error_logs), "Expected the failing stream to be named in logs"


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketEventsStreamIncremental(TestCase):
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
    def test_given_no_state_when_read_ticket_events_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = int(start_date.add(timedelta(days=1)).timestamp())

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build(),
            TicketEventsResponseBuilder.ticket_events_response()
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_field(FieldPath("timestamp"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_events", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_events"

    @HttpMocker()
    def test_given_state_when_read_ticket_events_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = int(_START_DATE.add(timedelta(days=30)).timestamp())
        new_cursor_value = state_cursor_value + 86400

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(state_cursor_value)
            .with_any_query_params()
            .build(),
            TicketEventsResponseBuilder.ticket_events_response()
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_field(FieldPath("timestamp"), new_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_events", {"timestamp": state_cursor_value}).build()

        output = read_stream("ticket_events", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_events"
