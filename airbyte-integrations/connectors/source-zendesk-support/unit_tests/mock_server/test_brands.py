# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import BrandsRecordBuilder, BrandsResponseBuilder, ErrorResponseBuilder
from .utils import get_log_messages_by_log_level, read_stream


class TestBrandsStreamFullRefresh(TestCase):
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
    def _brands_response_without_cursor_pagination():
        """Build a response that mimics Zendesk returning offset-pagination format
        (no 'links' or 'meta' keys) when results fit on a single page.

        This is the scenario that caused the UndefinedError crash before the fix:
        https://github.com/airbytehq/oncall/issues/11916
        """
        return HttpResponse(
            body=json.dumps(
                {
                    "brands": [
                        {
                            "id": 12345,
                            "url": "https://company.zendesk.com/api/v2/brands/12345.json",
                            "name": "My Brand",
                            "brand_url": "https://mybrand.zendesk.com",
                            "subdomain": "mybrand",
                            "host_mapping": None,
                            "has_help_center": True,
                            "help_center_state": "enabled",
                            "active": True,
                            "default": True,
                            "is_deleted": False,
                            "logo": None,
                            "ticket_form_ids": [],
                            "signature_template": "{{agent.signature}}",
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                        }
                    ],
                    "count": 1,
                    "next_page": None,
                    "previous_page": None,
                }
            ),
            status_code=200,
        )

    @staticmethod
    def get_authenticator(config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    def _base_brands_request(self, authenticator):
        return ZendeskSupportRequestBuilder.brands_endpoint(authenticator).with_page_size(100)

    @HttpMocker()
    def test_given_one_page_when_read_brands_then_return_records(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            BrandsResponseBuilder.brands_response().with_record(BrandsRecordBuilder.brands_record()).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_brands_then_return_all_records(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        # Create the next page request first - this URL will be used in links.next
        next_page_http_request = self._base_brands_request(api_token_authenticator).with_after_cursor("after-cursor").build()

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            BrandsResponseBuilder.brands_response(next_page_http_request)
            .with_record(BrandsRecordBuilder.brands_record())
            .with_pagination()
            .build(),
        )

        http_mocker.get(
            next_page_http_request,
            BrandsResponseBuilder.brands_response().with_record(BrandsRecordBuilder.brands_record().with_id(67890)).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_403_error_when_read_brands_then_fail(self, http_mocker):
        """Test that 403 errors cause the stream to fail with proper error logging.

        Per playbook: FAIL error handlers must assert both error code AND error message.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Error 403" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_brands_then_fail(self, http_mocker):
        """Test that 404 errors cause the stream to fail with proper error logging.

        Per playbook: FAIL error handlers must assert both error code AND error message.
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
        # Assert error code and message per playbook requirement
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
        assert any("Error 404" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_response_without_cursor_pagination_keys_when_read_brands_then_return_records(self, http_mocker):
        """Test that the connector handles responses missing 'links' and 'meta' keys.

        Zendesk may return offset-pagination format (no cursor pagination keys) for
        some endpoints or when results fit on a single page. Before the fix, the
        links_next_paginator crashed with jinja2.exceptions.UndefinedError because
        it used unsafe dict access: response['links']['next'].

        See: https://github.com/airbytehq/oncall/issues/11916
        """
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            self._brands_response_without_cursor_pagination(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1
