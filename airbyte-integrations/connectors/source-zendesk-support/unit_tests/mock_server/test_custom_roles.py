# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import CustomRolesRecordBuilder, CustomRolesResponseBuilder, ErrorResponseBuilder
from .utils import get_log_messages_by_log_level, read_stream


@freezegun.freeze_time("2025-11-01")
class TestCustomRolesStreamFullRefresh(TestCase):
    """
    Tests for custom_roles stream.
    This stream uses CursorPagination with next_page (not links_next_paginator).
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

    def _base_custom_roles_request(self, authenticator):
        return ZendeskSupportRequestBuilder.custom_roles_endpoint(authenticator)

    @HttpMocker()
    def test_given_one_page_when_read_custom_roles_then_return_records_and_emit_state(self, http_mocker):
        """Test reading custom_roles with a single page of results.
        Per playbook: validate a resulting state message is emitted for incremental streams.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        # Create a record with updated_at timestamp after start_date so it passes the date filter
        recent_date = ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        test_record = CustomRolesRecordBuilder.custom_roles_record().with_field(FieldPath("updated_at"), recent_date)

        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).with_any_query_params().build(),
            CustomRolesResponseBuilder.custom_roles_response().with_record(test_record).build(),
        )

        output = read_stream("custom_roles", SyncMode.incremental, self._config)
        assert len(output.records) == 1
        # Per playbook: validate state message is emitted for incremental streams
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "custom_roles"
        assert "updated_at" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_next_page_when_read_then_paginate(self, http_mocker):
        """Test that pagination fetches records from 2 pages and stops when last_page_size == 0.

        This test covers pagination behavior for streams using next_page URL pagination.
        The custom_roles stream uses next_page URL from response (not query params).
        """
        api_token_authenticator = self.get_authenticator(self._config)

        # Build the next page request - custom_roles uses full URL in next_page response field
        # The paginator uses RequestPath, so the next_page URL replaces the entire path
        next_page_url = f"https://d3v-airbyte.zendesk.com/api/v2/custom_roles?page=2"
        next_page_http_request = (
            ZendeskSupportRequestBuilder.custom_roles_endpoint(api_token_authenticator)
            .with_custom_url(next_page_url)
            .build()
        )

        # Create records with updated_at timestamps after start_date so they pass the date filter
        recent_date = ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        record1 = CustomRolesRecordBuilder.custom_roles_record().with_id(1001).with_field(FieldPath("updated_at"), recent_date)
        record2 = CustomRolesRecordBuilder.custom_roles_record().with_id(1002).with_field(FieldPath("updated_at"), recent_date)

        # Create record for page 2
        record3 = CustomRolesRecordBuilder.custom_roles_record().with_id(1003).with_field(FieldPath("updated_at"), recent_date)

        # Page 1: has records and provides next_page URL
        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).with_any_query_params().build(),
            CustomRolesResponseBuilder.custom_roles_response(next_page_http_request)
            .with_record(record1)
            .with_record(record2)
            .with_pagination()
            .build(),
        )

        # Page 2: has one more record
        http_mocker.get(
            next_page_http_request,
            CustomRolesResponseBuilder.custom_roles_response().with_record(record3).build(),
        )

        output = read_stream("custom_roles", SyncMode.full_refresh, self._config)

        # Verify all 3 records from both pages are returned
        assert len(output.records) == 3
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1001 in record_ids
        assert 1002 in record_ids
        assert 1003 in record_ids

    @HttpMocker()
    def test_given_403_error_when_read_custom_roles_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("custom_roles", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Error 403" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_custom_roles_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("custom_roles", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any("Error 404" in msg for msg in error_logs), "Expected error message in logs"
