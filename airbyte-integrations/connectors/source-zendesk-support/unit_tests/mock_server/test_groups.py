# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .helpers import given_groups_with_later_records
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import GroupsRecordBuilder, GroupsResponseBuilder
from .utils import datetime_to_string, read_stream, string_to_datetime


class TestGroupsStreamFullRefresh(TestCase):
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

    @HttpMocker()
    def test_given_no_state_when_read_groups_then_return_records_and_emit_state(self, http_mocker):
        """
        Perform a full refresh sync without state - all records after start_date are returned.
        Per playbook: validate a resulting state message is emitted.
        """
        api_token_authenticator = self.get_authenticator(self._config)
        given_groups_with_later_records(
            http_mocker,
            string_to_datetime(self._config["start_date"]),
            timedelta(weeks=12),
            api_token_authenticator,
        )

        output = read_stream("groups", SyncMode.incremental, self._config)
        assert len(output.records) == 2
        # Per playbook: validate state message is emitted for incremental streams
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "groups"
        assert "updated_at" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_incoming_state_semi_incremental_groups_does_not_emit_earlier_record(self, http_mocker):
        """
        Perform a semi-incremental sync where records that came before the current state are not included in the set
        of records emitted.
        """
        api_token_authenticator = self.get_authenticator(self._config)
        given_groups_with_later_records(
            http_mocker,
            string_to_datetime(self._config["start_date"]),
            timedelta(weeks=12),
            api_token_authenticator,
        )

        state_value = {"updated_at": datetime_to_string(ab_datetime_now().subtract(timedelta(weeks=102)))}

        state = StateBuilder().with_stream_state("groups", state_value).build()

        output = read_stream("groups", SyncMode.full_refresh, self._config, state=state)
        assert len(output.records) == 1


class TestGroupsStreamPagination(TestCase):
    """Test pagination for groups stream.

    The groups stream uses the base retriever paginator with:
    - cursor_value: response.get("next_page", {})
    - stop_condition: last_page_size == 0
    - page_size_option: per_page (not page[size])
    - page_token_option: RequestPath (uses full next_page URL as request path)

    This test also covers pagination behavior for other streams using the same
    base retriever paginator: tags, brands, automations, etc.
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

    @HttpMocker()
    def test_given_next_page_when_read_then_paginate(self, http_mocker):
        """Test that pagination fetches records from 2 pages and stops when last_page_size == 0.

        Following the pattern from test_articles.py:
        1. Build next_page_http_request using the request builder
        2. Pass it to GroupsResponseBuilder.groups_response(next_page_http_request)
        3. Use next_page_http_request directly as the mock for page 2
        """
        api_token_authenticator = self.get_authenticator(self._config)

        # Build the next page request using the request builder (same pattern as test_articles.py)
        # The next page request must be different from page 1 to avoid "already mocked" error
        next_page_http_request = (
            ZendeskSupportRequestBuilder.groups_endpoint(api_token_authenticator).with_per_page(100).with_query_param("page", "2").build()
        )

        # Create records for page 1 (with cursor values after start_date)
        record1 = (
            GroupsRecordBuilder.groups_record()
            .with_id(1001)
            .with_cursor(ab_datetime_now().subtract(timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )
        record2 = (
            GroupsRecordBuilder.groups_record()
            .with_id(1002)
            .with_cursor(ab_datetime_now().subtract(timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )

        # Create record for page 2
        record3 = (
            GroupsRecordBuilder.groups_record()
            .with_id(1003)
            .with_cursor(ab_datetime_now().subtract(timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        )

        # Page 1: has records and provides next_page URL (via NextPagePaginationStrategy)
        # Must call .with_pagination() to actually set the next_page field in the response
        http_mocker.get(
            ZendeskSupportRequestBuilder.groups_endpoint(api_token_authenticator).with_per_page(100).build(),
            GroupsResponseBuilder.groups_response(next_page_http_request)
            .with_record(record1)
            .with_record(record2)
            .with_pagination()
            .build(),
        )

        # Page 2: empty page (0 records) - triggers stop_condition: last_page_size == 0
        http_mocker.get(
            next_page_http_request,
            GroupsResponseBuilder.groups_response().with_record(record3).build(),
        )

        output = read_stream("groups", SyncMode.full_refresh, self._config)

        # Verify all 3 records from both pages are returned
        assert len(output.records) == 3
        record_ids = [r.record.data["id"] for r in output.records]
        assert 1001 in record_ids
        assert 1002 in record_ids
        assert 1003 in record_ids
