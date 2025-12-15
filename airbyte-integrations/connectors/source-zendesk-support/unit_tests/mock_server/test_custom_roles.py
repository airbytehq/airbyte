# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .utils import read_stream
from .zs_requests import CustomRolesRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import CustomRolesResponseBuilder, ErrorResponseBuilder
from .zs_responses.records import CustomRolesRecordBuilder


_NOW = ab_datetime_now()


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
        return CustomRolesRequestBuilder.custom_roles_endpoint(authenticator)

    @HttpMocker()
    def test_given_one_page_when_read_custom_roles_then_return_records(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).build(),
            CustomRolesResponseBuilder.custom_roles_response().with_record(CustomRolesRecordBuilder.custom_roles_record()).build(),
        )

        output = read_stream("custom_roles", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    # Note: Pagination test for custom_roles is skipped because this stream uses CursorPagination
    # with next_page URL (RequestPath token option), which requires different mocking approach.
    # The pagination behavior is covered by other streams using the same pattern.

    @HttpMocker()
    def test_given_403_error_when_read_custom_roles_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("custom_roles", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_given_404_error_when_read_custom_roles_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_custom_roles_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("custom_roles", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
