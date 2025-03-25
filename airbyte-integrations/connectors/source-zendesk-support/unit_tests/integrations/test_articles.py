# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
import pendulum

from airbyte_cdk.models import AirbyteStateBlob, SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .utils import datetime_to_string, read_stream
from .zs_requests.articles_request_builder import ArticlesRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses.articles_response_builder import ArticlesResponseBuilder
from .zs_responses.records.articles_records_builder import ArticlesRecordBuilder


_NOW = datetime.now(timezone.utc)
_START_DATE = pendulum.now(tz="UTC").subtract(years=2)


@freezegun.freeze_time(_NOW.isoformat())
class TestArticlesStream(TestCase):
    def _config(self) -> ConfigBuilder:
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(pendulum.now(tz="UTC").subtract(years=2))
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        http_mocker.get(
            ArticlesRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE).build(),
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
            ArticlesRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE.add(days=10)).build()
        )
        http_mocker.get(
            ArticlesRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE).build(),
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
        most_recent_cursor_value = _START_DATE.add(days=2)
        http_mocker.get(
            ArticlesRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(_START_DATE).build(),
            ArticlesResponseBuilder.response()
            .with_record(ArticlesRecordBuilder.record().with_cursor(datetime_to_string(most_recent_cursor_value)))
            .build(),
        )

        output = read_stream("articles", SyncMode.full_refresh, config)

        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(most_recent_cursor_value.int_timestamp)}

    @HttpMocker()
    def test_given_input_state_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        state_cursor_value = _START_DATE.add(days=2)
        http_mocker.get(
            ArticlesRequestBuilder.articles_endpoint(api_token_authenticator).with_start_time(state_cursor_value).build(),
            ArticlesResponseBuilder.response().with_record(ArticlesRecordBuilder.record()).build(),
        )

        output = read_stream(
            "articles",
            SyncMode.full_refresh,
            config,
            StateBuilder().with_stream_state("articles", {"updated_at": datetime_to_string(state_cursor_value)}).build(),
        )

        assert len(output.records) == 1
