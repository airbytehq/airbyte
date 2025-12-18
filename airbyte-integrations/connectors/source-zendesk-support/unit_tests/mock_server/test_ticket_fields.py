# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TicketFieldsRecordBuilder, TicketFieldsResponseBuilder
from .utils import datetime_to_string, get_log_messages_by_log_level, read_stream


class TestTicketFieldsStreamFullRefresh(TestCase):
    """Test ticket_fields stream which is a semi-incremental stream."""

    @property
    def _config(self):
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(ab_datetime_now().subtract(timedelta(weeks=104)))
            .build()
        )

    @staticmethod
    def get_authenticator(config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    def _base_ticket_fields_request(self, authenticator):
        return ZendeskSupportRequestBuilder.ticket_fields_endpoint(authenticator).with_page_size(100)

    @HttpMocker()
    def test_given_one_page_when_read_ticket_fields_then_return_records_and_emit_state(self, http_mocker):
        """Test reading ticket_fields with a single page of results.
        Per playbook: validate a resulting state message is emitted for incremental streams.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_ticket_fields_request(api_token_authenticator).build(),
            TicketFieldsResponseBuilder.ticket_fields_response()
            .with_record(
                TicketFieldsRecordBuilder.ticket_fields_record().with_cursor(
                    ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
                )
            )
            .build(),
        )

        output = read_stream("ticket_fields", SyncMode.incremental, self._config)
        assert len(output.records) == 1
        # Per playbook: validate state message is emitted for incremental streams
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "ticket_fields"
        assert "updated_at" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_two_pages_when_read_ticket_fields_then_return_all_records(self, http_mocker):
        """Test pagination for ticket_fields stream."""
        api_token_authenticator = self.get_authenticator(self._config)

        next_page_http_request = self._base_ticket_fields_request(api_token_authenticator).with_after_cursor("after-cursor").build()

        http_mocker.get(
            self._base_ticket_fields_request(api_token_authenticator).build(),
            TicketFieldsResponseBuilder.ticket_fields_response(next_page_http_request)
            .with_record(
                TicketFieldsRecordBuilder.ticket_fields_record()
                .with_id(1001)
                .with_cursor(ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
            )
            .with_pagination()
            .build(),
        )

        http_mocker.get(
            next_page_http_request,
            TicketFieldsResponseBuilder.ticket_fields_response()
            .with_record(
                TicketFieldsRecordBuilder.ticket_fields_record()
                .with_id(1002)
                .with_cursor(ab_datetime_now().subtract(timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"))
            )
            .build(),
        )

        output = read_stream("ticket_fields", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_state_when_read_ticket_fields_then_filter_records(self, http_mocker):
        """Test semi-incremental filtering with state."""
        api_token_authenticator = self.get_authenticator(self._config)

        old_record = (
            TicketFieldsRecordBuilder.ticket_fields_record()
            .with_id(1001)
            .with_cursor(ab_datetime_now().subtract(timedelta(weeks=103)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )
        new_record = (
            TicketFieldsRecordBuilder.ticket_fields_record()
            .with_id(1002)
            .with_cursor(ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )

        http_mocker.get(
            self._base_ticket_fields_request(api_token_authenticator).build(),
            TicketFieldsResponseBuilder.ticket_fields_response().with_record(old_record).with_record(new_record).build(),
        )

        state_value = {"updated_at": datetime_to_string(ab_datetime_now().subtract(timedelta(weeks=102)))}
        state = StateBuilder().with_stream_state("ticket_fields", state_value).build()

        output = read_stream("ticket_fields", SyncMode.full_refresh, self._config, state=state)
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == 1002

    @HttpMocker()
    def test_given_403_error_when_read_ticket_fields_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_ticket_fields_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("ticket_fields", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Error 403" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_ticket_fields_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_ticket_fields_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("ticket_fields", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any("Error 404" in msg for msg in error_logs), "Expected error message in logs"
