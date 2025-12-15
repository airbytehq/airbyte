# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .utils import read_stream
from .zs_requests import TagsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import ErrorResponseBuilder, TagsResponseBuilder
from .zs_responses.records import TagsRecordBuilder


_NOW = ab_datetime_now()


class TestTagsStreamFullRefresh(TestCase):
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

    def _base_tags_request(self, authenticator):
        return TagsRequestBuilder.tags_endpoint(authenticator).with_page_size(100)

    @HttpMocker()
    def test_given_one_page_when_read_tags_then_return_records(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_tags_request(api_token_authenticator).build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record()).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, self._config)
        assert len(output.records) == 1

    @HttpMocker()
    def test_given_two_pages_when_read_tags_then_return_all_records(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_tags_request(api_token_authenticator).build(),
            TagsResponseBuilder.tags_response(self._base_tags_request(api_token_authenticator).build())
            .with_record(TagsRecordBuilder.tags_record())
            .with_pagination()
            .build(),
        )

        http_mocker.get(
            self._base_tags_request(api_token_authenticator).with_after_cursor("after-cursor").build(),
            TagsResponseBuilder.tags_response().with_record(TagsRecordBuilder.tags_record().with_name("second-tag")).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, self._config)
        assert len(output.records) == 2

    @HttpMocker()
    def test_given_403_error_when_read_tags_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_tags_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(403).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0

    @HttpMocker()
    def test_given_404_error_when_read_tags_then_fail(self, http_mocker):
        api_token_authenticator = self.get_authenticator(self._config)

        http_mocker.get(
            self._base_tags_request(api_token_authenticator).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("tags", SyncMode.full_refresh, self._config, expecting_exception=True)
        assert len(output.records) == 0
