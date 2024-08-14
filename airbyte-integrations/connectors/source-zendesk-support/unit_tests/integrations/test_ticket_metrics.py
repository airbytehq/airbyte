# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
import pendulum
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import AirbyteStateBlob, SyncMode

from .config import ConfigBuilder
from .helpers import given_tickets, given_tickets_with_state
from .utils import read_stream, string_to_datetime
from .zs_requests import TicketMetricsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import TicketMetricsResponseBuilder
from .zs_responses.records import TicketMetricsRecordBuilder

_NOW = datetime.now(timezone.utc)

@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsIncremental(TestCase):

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(pendulum.now(tz="UTC").subtract(years=2))
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_no_state_and_successful_sync_when_read_then_set_state_to_most_recently_read_record_cursor(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        tickets_records_builder = given_tickets(http_mocker, string_to_datetime(self._config["start_date"]), api_token_authenticator)

        ticket = tickets_records_builder.build()
        ticket_metrics_record_builder = TicketMetricsRecordBuilder.ticket_metrics_record().with_field(
            FieldPath("ticket_id"), ticket["id"]
        ).with_cursor(ticket["generated_timestamp"])

        http_mocker.get(
            TicketMetricsRequestBuilder.ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            TicketMetricsResponseBuilder.ticket_metrics_response().with_record(ticket_metrics_record_builder).build()
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state=None)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert output.most_recent_state.stream_state == AirbyteStateBlob.model_validate({
            "generated_timestamp": ticket["generated_timestamp"]
        })


    @HttpMocker()
    def test_given_state_and_successful_sync_when_read_then_return_record(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        state_cursor_value = pendulum.now(tz="UTC").subtract(days=2).int_timestamp
        state = {"generated_timestamp": state_cursor_value}
        record_cursor_value = pendulum.now(tz="UTC").subtract(days=1)
        tickets_records_builder = given_tickets_with_state(http_mocker, pendulum.from_timestamp(state_cursor_value), record_cursor_value,api_token_authenticator)
        ticket = tickets_records_builder.build()

        ticket_metrics_first_record_builder = TicketMetricsRecordBuilder.ticket_metrics_record().with_field(
            FieldPath("ticket_id"), ticket["id"]
        ).with_cursor(ticket["generated_timestamp"])

        http_mocker.get(
            TicketMetricsRequestBuilder.ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            TicketMetricsResponseBuilder.ticket_metrics_response().with_record(ticket_metrics_first_record_builder).build()
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state=StateBuilder().with_stream_state("ticket_metrics", state).build())

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert output.most_recent_state.stream_state == AirbyteStateBlob.model_validate({
            "generated_timestamp": record_cursor_value.int_timestamp
        })
