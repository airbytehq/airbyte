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
from .response_builder import TicketEventsRecordBuilder, TicketEventsResponseBuilder
from .utils import extract_cursor_value_from_state, read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"


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
    def test_given_one_page_when_read_ticket_events_then_return_raw_ticket_event_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_include("comment_events")
            .build(),
            TicketEventsResponseBuilder.ticket_events_response().with_record(TicketEventsRecordBuilder.ticket_events_record()).build(),
        )

        output = read_stream("ticket_events", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 35436
        assert record["event_type"] == "Audit"
        assert record["ticket_id"] == 47
        assert [child_event["event_type"] for child_event in record["child_events"]] == ["Comment", "Notification"]

    @HttpMocker()
    def test_given_two_pages_when_read_ticket_events_then_return_all_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        base_url = "https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_events.json"

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_include("comment_events")
            .build(),
            TicketEventsResponseBuilder.ticket_events_response(base_url, _A_CURSOR)
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_id(1))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_cursor(_A_CURSOR)
            .with_include("comment_events")
            .build(),
            TicketEventsResponseBuilder.ticket_events_response()
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_id(2))
            .build(),
        )

        output = read_stream("ticket_events", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        assert {record.record.data["id"] for record in output.records} == {1, 2}


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
    def test_given_state_when_read_ticket_events_then_use_timestamp_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = int(_START_DATE.add(timedelta(days=30)).timestamp())
        next_cursor_value = state_cursor_value + 3600

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_events_endpoint(api_token_authenticator)
            .with_start_time(state_cursor_value)
            .with_include("comment_events")
            .build(),
            TicketEventsResponseBuilder.ticket_events_response()
            .with_record(TicketEventsRecordBuilder.ticket_events_record().with_field(FieldPath("timestamp"), next_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_events", {"timestamp": str(state_cursor_value)}).build()

        output = read_stream("ticket_events", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_events"
        assert extract_cursor_value_from_state(output.most_recent_state.stream_state.__dict__, "timestamp") == str(next_cursor_value)
