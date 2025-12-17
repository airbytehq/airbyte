# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import AccountAttributesRecordBuilder, AccountAttributesResponseBuilder, ErrorResponseBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestAccountAttributesStreamFullRefresh(TestCase):
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

    def _base_account_attributes_request(self, authenticator):
        return ZendeskSupportRequestBuilder.account_attributes_endpoint(authenticator).with_per_page(100)

    @HttpMocker()
    def test_given_one_page_when_read_account_attributes_then_return_records(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_account_attributes_request(api_token_authenticator).build(),
            AccountAttributesResponseBuilder.account_attributes_response()
            .with_record(AccountAttributesRecordBuilder.account_attributes_record())
            .build(),
        )

        output = read_stream("account_attributes", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_account_attributes_then_return_all_records(self, http_mocker):
        """Test pagination for account_attributes stream.

        The account_attributes stream uses the base retriever paginator with:
        - cursor_value: response.get("next_page", {})
        - stop_condition: last_page_size == 0
        - page_size_option: per_page
        - page_token_option: RequestPath (uses full next_page URL as request path)
        """
        api_token_authenticator = self.get_authenticator(self._config)

        # Build the next page request (must be different from page 1)
        next_page_http_request = self._base_account_attributes_request(api_token_authenticator).with_query_param("page", "2").build()

        # Page 1: has records and provides next_page URL
        http_mocker.get(
            self._base_account_attributes_request(api_token_authenticator).build(),
            AccountAttributesResponseBuilder.account_attributes_response(next_page_http_request)
            .with_record(AccountAttributesRecordBuilder.account_attributes_record())
            .with_pagination()
            .build(),
        )

        # Page 2: has records (stop_condition is last_page_size == 0)
        http_mocker.get(
            next_page_http_request,
            AccountAttributesResponseBuilder.account_attributes_response()
            .with_record(AccountAttributesRecordBuilder.account_attributes_record().with_id("second-attr-id"))
            .build(),
        )

        output = read_stream("account_attributes", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_403_error_when_read_account_attributes_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_account_attributes_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("account_attributes", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Error 403" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_account_attributes_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_account_attributes_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("account_attributes", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any("Error 404" in msg for msg in error_logs), "Expected error message in logs"
