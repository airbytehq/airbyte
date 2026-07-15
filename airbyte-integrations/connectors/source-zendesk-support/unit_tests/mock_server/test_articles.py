# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ArticlesRecordBuilder, ArticlesResponseBuilder
from .utils import datetime_to_string, read_stream


_NOW = ab_datetime_now()
_START_DATE = ab_datetime_now().subtract(timedelta(weeks=52))


@freezegun.freeze_time(_NOW.isoformat())
class TestArticlesStream(TestCase):
    def _config(self) -> ConfigBuilder:
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(ab_datetime_now().subtract(timedelta(hours=1)))
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE).build(),
            ArticlesResponseBuilder.response()
            .with_record(ArticlesRecordBuilder.record())
            .with_record(ArticlesRecordBuilder.record())
            .build(),
        )

        output = read_stream("articles", SyncMode.full_refresh, config)

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_next_page_when_read_then_paginate(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        next_page_http_request = (
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator)
            .with_start_time(_START_DATE.add(timedelta(days=10)))
            .build()
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE).build(),
            ArticlesResponseBuilder.response(next_page_http_request)
            .with_record(ArticlesRecordBuilder.record())
            .with_record(ArticlesRecordBuilder.record())
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            next_page_http_request,
            ArticlesResponseBuilder.response().with_record(ArticlesRecordBuilder.record()).build(),
        )

        output = read_stream("articles", SyncMode.full_refresh, config)

        assert len(output.records) == 3

    @HttpMocker()
    def test_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        most_recent_cursor_value = _START_DATE.add(timedelta(days=2))
        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE).build(),
            ArticlesResponseBuilder.response()
            .with_record(ArticlesRecordBuilder.record().with_cursor(datetime_to_string(most_recent_cursor_value)))
            .build(),
        )

        output = read_stream("articles", SyncMode.full_refresh, config)

        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(int(most_recent_cursor_value.timestamp()))}

    @HttpMocker()
    def test_given_input_state_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        state_cursor_value = _START_DATE.add(timedelta(days=2))
        http_mocker.get(
            ZendeskSupportRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(state_cursor_value).build(),
            ArticlesResponseBuilder.response().with_record(ArticlesRecordBuilder.record()).build(),
        )

        output = read_stream(
            "articles",
            SyncMode.full_refresh,
            config,
            StateBuilder().with_stream_state("articles", {"updated_at": datetime_to_string(state_cursor_value)}).build(),
        )

        assert len(output.records) == 1
