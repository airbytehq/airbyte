# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now, ab_datetime_parse

from .config import ConfigBuilder
from .helpers import given_tickets_with_state
from .utils import read_stream
from .zs_requests import TicketMetricsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import TicketMetricsResponseBuilder
from .zs_responses.records import TicketMetricsRecordBuilder


_NOW = ab_datetime_now()
_TWO_YEARS_AGO_DATETIME = _NOW.subtract(timedelta(weeks=104))


@freezegun.freeze_time(_NOW.isoformat())
class TestTicketMetricsIncremental(TestCase):
    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(_TWO_YEARS_AGO_DATETIME)
            .build()
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_no_state_and_successful_sync_when_read_then_set_state_to_most_recently_read_record_cursor(self, http_mocker):
        record_updated_at: str = ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        api_token_authenticator = self._get_authenticator(self._config)
        ticket_metrics_record_builder = TicketMetricsRecordBuilder.stateless_ticket_metrics_record().with_cursor(record_updated_at)

        http_mocker.get(
            TicketMetricsRequestBuilder.stateless_ticket_metrics_endpoint(api_token_authenticator).with_page_size(100).build(),
            TicketMetricsResponseBuilder.stateless_ticket_metrics_response().with_record(ticket_metrics_record_builder).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert output.most_recent_state.stream_state.__dict__ == {
            "_ab_updated_at": str(int(ab_datetime_parse(record_updated_at).timestamp()))
        }

    @HttpMocker()
    def test_given_state_when_read_then_migrate_state_to_per_partition(self, http_mocker):
        api_token_authenticator = self._get_authenticator(self._config)

        state_cursor_value = int(ab_datetime_now().subtract(timedelta(days=2)).timestamp())
        state = StateBuilder().with_stream_state("ticket_metrics", state={"_ab_updated_at": state_cursor_value}).build()
        parent_cursor_value = ab_datetime_now().subtract(timedelta(days=2))
        tickets_records_builder = given_tickets_with_state(
            http_mocker, ab_datetime_parse(state_cursor_value), parent_cursor_value, api_token_authenticator
        )
        ticket = tickets_records_builder.build()

        child_cursor_value = ab_datetime_now().subtract(timedelta(days=1))
        ticket_metrics_first_record_builder = (
            TicketMetricsRecordBuilder.stateful_ticket_metrics_record()
            .with_field(FieldPath("ticket_id"), ticket["id"])
            .with_cursor(int(child_cursor_value.timestamp()))
        )

        http_mocker.get(
            TicketMetricsRequestBuilder.stateful_ticket_metrics_endpoint(api_token_authenticator, ticket["id"]).build(),
            TicketMetricsResponseBuilder.stateful_ticket_metrics_response().with_record(ticket_metrics_first_record_builder).build(),
        )

        output = read_stream("ticket_metrics", SyncMode.incremental, self._config, state)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "ticket_metrics"
        assert output.most_recent_state.stream_state.__dict__ == {
            "lookback_window": 0,
            "parent_state": {"tickets": {"generated_timestamp": int(parent_cursor_value.timestamp())}},
            "state": {"_ab_updated_at": str(int(child_cursor_value.timestamp()))},
            "states": [
                {
                    "cursor": {"_ab_updated_at": str(int(child_cursor_value.timestamp()))},
                    "partition": {"parent_slice": {}, "ticket_id": 35436},
                }
            ],
            "use_global_cursor": False,
        }
