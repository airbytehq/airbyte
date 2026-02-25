# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Tests for the sla_policies stream.

The sla_policies stream uses CursorPagination with next_page URL (RequestPath token option).
This is similar to custom_roles and schedules streams.
Pagination is handled via the next_page field in the response.
"""

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, SlaPoliciesRecordBuilder, SlaPoliciesResponseBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestSlaPoliciesStreamFullRefresh(TestCase):
    """
    Tests for the sla_policies stream full refresh sync.

    The sla_policies stream uses CursorPagination with next_page URL.
    The paginator uses:
    - cursor_value: '{{ response.get("next_page", {}) }}'
    - stop_condition: "{{ last_page_size == 0 }}"
    - page_token_option: type: RequestPath
    """

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

    def _base_sla_policies_request(self, authenticator):
        return ZendeskSupportRequestBuilder.sla_policies_endpoint(authenticator)

    @HttpMocker()
    def test_given_one_page_when_read_sla_policies_then_return_records_and_emit_state(self, http_mocker):
        """Test reading sla_policies with a single page of results.
        Per playbook: validate a resulting state message is emitted for incremental streams.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_sla_policies_request(api_token_authenticator).build(),
            SlaPoliciesResponseBuilder.sla_policies_response().with_record(SlaPoliciesRecordBuilder.sla_policies_record()).build(),
        )

        output = read_stream("sla_policies", SyncMode.incremental, self._config)
        assert len(output.records) == 1
        # Per playbook: validate state message is emitted for incremental streams
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "sla_policies"
        assert "updated_at" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_next_page_when_read_then_paginate(self, http_mocker):
        """Test that pagination fetches records from 2 pages and stops when last_page_size == 0.

        This test covers pagination behavior for streams using next_page URL pagination.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        # Build the next page request using the request builder
        next_page_http_request = (
            ZendeskSupportRequestBuilder.sla_policies_endpoint(api_token_authenticator).with_query_param("page", "2").build()
        )

        # Create records for page 1
        record1 = SlaPoliciesRecordBuilder.sla_policies_record().with_id(1001)
        record2 = SlaPoliciesRecordBuilder.sla_policies_record().with_id(1002)

        # Create record for page 2
        record3 = SlaPoliciesRecordBuilder.sla_policies_record().with_id(1003)

        # Page 1: has records and provides next_page URL
        http_mocker.get(
            self._base_sla_policies_request(api_token_authenticator).build(),
            SlaPoliciesResponseBuilder.sla_policies_response(next_page_http_request)
            .with_record(record1)
            .with_record(record2)
            .with_pagination()
            .build(),
        )

        # Page 2: has one more record
        http_mocker.get(
            next_page_http_request,
            SlaPoliciesResponseBuilder.sla_policies_response().with_record(record3).build(),
        )

        output = read_stream("sla_policies", SyncMode.full_refresh, self._config)

        # Verify all 3 records from both pages are returned
        assert len(output.records) == 3
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1001 in record_ids
        assert 1002 in record_ids
        assert 1003 in record_ids

    @HttpMocker()
    def test_given_403_error_when_read_sla_policies_then_fail(self, http_mocker):
        """Test that 403 errors are handled correctly."""
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_sla_policies_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("sla_policies", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Error 403" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_sla_policies_then_fail(self, http_mocker):
        """Test that 404 errors are handled correctly."""
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_sla_policies_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("sla_policies", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any("Error 404" in msg for msg in error_logs), "Expected error message in logs"
