# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import Level, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import TicketMetricEventsRecordBuilder, TicketMetricEventsResponseBuilder
from .utils import datetime_to_string, extract_cursor_value_from_state, read_stream, string_to_datetime


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"
# The stream filters records older than the start date client-side, so records must carry a cursor value in the window.
_IN_WINDOW_TIME = datetime_to_string(_START_DATE.add(timedelta(days=1)))


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsStreamFullRefresh(TestCase):
    """Test ticket_metric_events stream which is an incremental stream."""

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
    def test_given_one_page_when_read_ticket_metric_events_then_return_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(TicketMetricEventsRecordBuilder.ticket_metric_events_record().with_field(FieldPath("time"), _IN_WINDOW_TIME))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.full_refresh, self._config)

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_ticket_metric_events_then_return_all_records(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        first_page_request = (
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build()
        )

        base_url = "https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_metric_events"

        http_mocker.get(
            first_page_request,
            TicketMetricEventsResponseBuilder.ticket_metric_events_response(base_url, _A_CURSOR)
            .with_record(
                TicketMetricEventsRecordBuilder.ticket_metric_events_record().with_id(1).with_field(FieldPath("time"), _IN_WINDOW_TIME)
            )
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(api_token_authenticator).with_cursor(_A_CURSOR).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(
                TicketMetricEventsRecordBuilder.ticket_metric_events_record().with_id(2).with_field(FieldPath("time"), _IN_WINDOW_TIME)
            )
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.full_refresh, self._config)

        assert len(output.records) == 2
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1 in record_ids
        assert 2 in record_ids


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsStreamIncremental(TestCase):
    """Test ticket_metric_events stream incremental sync."""

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
    def test_given_no_state_when_read_ticket_metric_events_then_return_records_and_emit_state(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        start_date = string_to_datetime(self._config["start_date"])
        cursor_value = datetime_to_string(start_date.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(api_token_authenticator)
            .with_start_time(self._config["start_date"])
            .with_any_query_params()
            .build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(TicketMetricEventsRecordBuilder.ticket_metric_events_record().with_field(FieldPath("time"), cursor_value))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_metric_events"

    @HttpMocker()
    def test_given_state_when_read_ticket_metric_events_then_use_state_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)
        state_cursor_value = _START_DATE.add(timedelta(days=30))
        new_cursor_value = datetime_to_string(state_cursor_value.add(timedelta(days=1)))

        http_mocker.get(
            ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(api_token_authenticator)
            .with_start_time(datetime_to_string(state_cursor_value))
            .with_any_query_params()
            .build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(TicketMetricEventsRecordBuilder.ticket_metric_events_record().with_field(FieldPath("time"), new_cursor_value))
            .build(),
        )

        state = StateBuilder().with_stream_state("ticket_metric_events", {"time": datetime_to_string(state_cursor_value)}).build()

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_metric_events"


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricEventsClientSideFiltering(TestCase):
    """
    Zendesk selects export rows by the ticket's generated_timestamp, and archiving a ticket re-stamps its whole
    event history, so a page can carry events far older than the requested start_time. The stream drops records
    older than the cursor (`is_client_side_incremental`) without changing the requests it makes.
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

    def _endpoint(self):
        config = self._config
        return ZendeskSupportRequestBuilder.ticket_metric_events_endpoint(
            ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])
        )

    @staticmethod
    def _record(record_id: int, time):
        return TicketMetricEventsRecordBuilder.ticket_metric_events_record().with_id(record_id).with_field(FieldPath("time"), time)

    @staticmethod
    def _state(cursor_value: str):
        return StateBuilder().with_stream_state("ticket_metric_events", {"time": cursor_value}).build()

    @staticmethod
    def _emitted_cursor(output) -> int:
        return int(extract_cursor_value_from_state(output.most_recent_state.stream_state.__dict__, "time"))

    @HttpMocker()
    def test_given_state_when_page_has_older_equal_and_newer_records_then_emit_only_equal_and_newer(self, http_mocker):
        state_cursor = string_to_datetime(self._config["start_date"]).add(timedelta(days=30))
        newer = state_cursor.add(timedelta(hours=1))
        http_mocker.get(
            self._endpoint().with_start_time(state_cursor).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(self._record(1, datetime_to_string(state_cursor.subtract(timedelta(days=400)))))
            .with_record(self._record(2, datetime_to_string(state_cursor.subtract(timedelta(seconds=1)))))
            .with_record(self._record(3, datetime_to_string(state_cursor)))
            .with_record(self._record(4, datetime_to_string(newer)))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config, self._state(datetime_to_string(state_cursor)))

        assert [record.record.data["id"] for record in output.records] == [3, 4]
        assert self._emitted_cursor(output) == int(newer.timestamp())

    @HttpMocker()
    def test_given_state_when_every_record_is_older_then_emit_nothing_and_keep_state(self, http_mocker):
        state_cursor = string_to_datetime(self._config["start_date"]).add(timedelta(days=30))
        http_mocker.get(
            self._endpoint().with_start_time(state_cursor).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(self._record(1, datetime_to_string(state_cursor.subtract(timedelta(days=400)))))
            .with_record(self._record(2, datetime_to_string(state_cursor.subtract(timedelta(days=1)))))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config, self._state(datetime_to_string(state_cursor)))

        assert len(output.records) == 0
        assert self._emitted_cursor(output) == int(state_cursor.timestamp())

    @HttpMocker()
    def test_given_no_state_when_records_are_older_than_start_date_then_drop_them(self, http_mocker):
        start = string_to_datetime(self._config["start_date"])
        http_mocker.get(
            self._endpoint().with_start_time(self._config["start_date"]).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(self._record(1, datetime_to_string(start.subtract(timedelta(days=1)))))
            .with_record(self._record(2, datetime_to_string(start)))
            .with_record(self._record(3, datetime_to_string(start.add(timedelta(days=1)))))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config)

        assert [record.record.data["id"] for record in output.records] == [2, 3]
        assert self._emitted_cursor(output) == int(start.add(timedelta(days=1)).timestamp())

    @HttpMocker()
    def test_given_older_records_on_first_page_when_paginating_then_still_request_next_page(self, http_mocker):
        state_cursor = string_to_datetime(self._config["start_date"]).add(timedelta(days=30))
        base_url = "https://d3v-airbyte.zendesk.com/api/v2/incremental/ticket_metric_events"
        http_mocker.get(
            self._endpoint().with_start_time(state_cursor).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response(base_url, _A_CURSOR)
            .with_record(self._record(1, datetime_to_string(state_cursor.subtract(timedelta(days=400)))))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            self._endpoint().with_cursor(_A_CURSOR).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(self._record(2, datetime_to_string(state_cursor.add(timedelta(hours=1)))))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config, self._state(datetime_to_string(state_cursor)))

        assert [record.record.data["id"] for record in output.records] == [2]

    @HttpMocker()
    def test_given_record_without_parseable_cursor_value_then_emit_it_and_do_not_move_state(self, http_mocker):
        # The CDK keeps a record whose cursor value is missing or unparseable (ConcurrentCursor.should_be_synced
        # returns True on ValueError) and logs a warning once per stream.
        state_cursor = string_to_datetime(self._config["start_date"]).add(timedelta(days=30))
        http_mocker.get(
            self._endpoint().with_start_time(state_cursor).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(self._record(1, None))
            .with_record(self._record(2, "not-a-timestamp"))
            .with_record(self._record(3, datetime_to_string(state_cursor.subtract(timedelta(days=1)))))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config, self._state(datetime_to_string(state_cursor)))

        assert [record.record.data["id"] for record in output.records] == [1, 2]
        assert self._emitted_cursor(output) == int(state_cursor.timestamp())
        assert any(
            "Could not find cursor field `time`" in message.log.message for message in output.logs if message.log.level == Level.WARN
        )

    @HttpMocker()
    def test_given_record_later_than_now_then_drop_it_and_do_not_move_state_past_now(self, http_mocker):
        # The CDK filter is bounded above by the cursor's end (now). Such a record is not checkpointed either, so the
        # next sync's start_time does not move into the future (which the export rejects with a 400).
        state_cursor = string_to_datetime(self._config["start_date"]).add(timedelta(days=30))
        newer = state_cursor.add(timedelta(hours=1))
        http_mocker.get(
            self._endpoint().with_start_time(state_cursor).build(),
            TicketMetricEventsResponseBuilder.ticket_metric_events_response()
            .with_record(self._record(1, datetime_to_string(newer)))
            .with_record(self._record(2, datetime_to_string(_NOW.add(timedelta(days=1)))))
            .build(),
        )

        output = read_stream("ticket_metric_events", SyncMode.incremental, self._config, self._state(datetime_to_string(state_cursor)))

        assert [record.record.data["id"] for record in output.records] == [1]
        assert self._emitted_cursor(output) == int(newer.timestamp())
