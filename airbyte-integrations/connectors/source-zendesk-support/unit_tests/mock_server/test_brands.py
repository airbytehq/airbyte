# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .utils import read_stream
from .zs_requests import BrandsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import BrandsResponseBuilder, ErrorResponseBuilder
from .zs_responses.records import BrandsRecordBuilder


_NOW = ab_datetime_now()


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
    def get_authenticator(config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    def _base_brands_request(self, authenticator):
        return BrandsRequestBuilder.brands_endpoint(authenticator).with_page_size(100)

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

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            BrandsResponseBuilder.brands_response(self._base_brands_request(api_token_authenticator).build())
            .with_record(BrandsRecordBuilder.brands_record())
            .with_pagination()
            .build(),
        )

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).with_after_cursor("after-cursor").build(),
            BrandsResponseBuilder.brands_response().with_record(BrandsRecordBuilder.brands_record().with_id(67890)).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_403_error_when_read_brands_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_given_404_error_when_read_brands_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_brands_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("brands", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
