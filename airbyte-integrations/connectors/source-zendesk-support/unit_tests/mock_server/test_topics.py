# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, TopicsRecordBuilder, TopicsResponseBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestTopicsStreamFullRefresh(TestCase):
    """Test topics stream which uses links_next_paginator (cursor-based pagination)."""

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

    def _base_topics_request(self, authenticator):
        return ZendeskSupportRequestBuilder.topics_endpoint(authenticator).with_page_size(100)

    @HttpMocker()
    def test_given_one_page_when_read_topics_then_return_records_and_emit_state(self, http_mocker):
        """Test reading topics with a single page of results.
        Per playbook: validate a resulting state message is emitted for incremental streams.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_topics_request(api_token_authenticator).build(),
            TopicsResponseBuilder.topics_response().with_record(TopicsRecordBuilder.topics_record()).build(),
        )

        output = read_stream("topics", SyncMode.incremental, self._config)
        assert len(output.records) == 1
        # Per playbook: validate state message is emitted for incremental streams
        assert output.most_recent_state is not None
        assert output.most_recent_state.stream_descriptor.name == "topics"
        assert "updated_at" in output.most_recent_state.stream_state.__dict__

    @HttpMocker()
    def test_given_two_pages_when_read_topics_then_return_all_records(self, http_mocker):
        """Test pagination for topics stream using links.next cursor-based pagination."""
        api_token_authenticator = self.get_authenticator(self._config)

        # Create the next page request first - this URL will be used in links.next
        next_page_http_request = self._base_topics_request(api_token_authenticator).with_after_cursor("after-cursor").build()

        http_mocker.get(
            self._base_topics_request(api_token_authenticator).build(),
            TopicsResponseBuilder.topics_response(next_page_http_request)
            .with_record(TopicsRecordBuilder.topics_record())
            .with_pagination()
            .build(),
        )

        http_mocker.get(
            next_page_http_request,
            TopicsResponseBuilder.topics_response().with_record(TopicsRecordBuilder.topics_record().with_id(67890)).build(),
        )

        output = read_stream("topics", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_403_error_when_read_topics_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_topics_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("topics", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Error 403" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_topics_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_topics_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("topics", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any("Error 404" in msg for msg in error_logs), "Expected error message in logs"
