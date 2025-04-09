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
from .zs_requests import PostsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_requests.request_authenticators.authenticator import Authenticator
from .zs_responses import PostsResponseBuilder
from .zs_responses.records import PostsRecordBuilder


_NOW = datetime.now(timezone.utc)
_START_DATE = pendulum.now(tz="UTC").subtract(years=2)


@freezegun.freeze_time(_NOW.isoformat())
class TestPostsStream(TestCase):
    def _config(self) -> ConfigBuilder:
        return (
            ConfigBuilder()
            .with_basic_auth_credentials("user@example.com", "password")
            .with_subdomain("d3v-airbyte")
            .with_start_date(pendulum.now(tz="UTC").subtract(years=2))
        )

    def _get_authenticator(self, config):
        return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])

    def _base_posts_request(self, authenticator: Authenticator) -> PostsRequestBuilder:
        return PostsRequestBuilder.posts_endpoint(authenticator).with_page_size(100)

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        http_mocker.get(
            self._base_posts_request(api_token_authenticator).with_start_time(datetime_to_string(_START_DATE)).build(),
            PostsResponseBuilder.posts_response()
            .with_record(PostsRecordBuilder.posts_record())
            .with_record(PostsRecordBuilder.posts_record())
            .build(),
        )

        output = read_stream("posts", SyncMode.full_refresh, config)

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_has_more_when_read_then_paginate(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        http_mocker.get(
            self._base_posts_request(api_token_authenticator).with_start_time(datetime_to_string(_START_DATE)).build(),
            PostsResponseBuilder.posts_response(self._base_posts_request(api_token_authenticator).build())
            .with_record(PostsRecordBuilder.posts_record())
            .with_record(PostsRecordBuilder.posts_record())
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            self._base_posts_request(api_token_authenticator).with_after_cursor("after-cursor").build(),
            PostsResponseBuilder.posts_response().with_record(PostsRecordBuilder.posts_record()).build(),
        )

        output = read_stream("posts", SyncMode.full_refresh, config)

        assert len(output.records) == 3

    @HttpMocker()
    def test_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        most_recent_cursor_value = _START_DATE.add(days=2)
        http_mocker.get(
            PostsRequestBuilder.posts_endpoint(api_token_authenticator)
            .with_start_time(datetime_to_string(_START_DATE))
            .with_page_size(100)
            .build(),
            PostsResponseBuilder.posts_response()
            .with_record(PostsRecordBuilder.posts_record().with_cursor(datetime_to_string(most_recent_cursor_value)))
            .with_record(PostsRecordBuilder.posts_record().with_cursor(datetime_to_string(_START_DATE.add(days=1))))
            .build(),
        )

        output = read_stream("posts", SyncMode.full_refresh, config)

        assert output.most_recent_state.stream_state == AirbyteStateBlob({"updated_at": str(most_recent_cursor_value.int_timestamp)})

    @HttpMocker()
    def test_given_input_state_as_old_format_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        state_cursor_value = datetime_to_string(_START_DATE.add(days=2))
        http_mocker.get(
            PostsRequestBuilder.posts_endpoint(api_token_authenticator).with_start_time(state_cursor_value).with_page_size(100).build(),
            PostsResponseBuilder.posts_response().with_record(PostsRecordBuilder.posts_record()).build(),
        )

        output = read_stream(
            "posts", SyncMode.full_refresh, config, StateBuilder().with_stream_state("posts", {"updated_at": state_cursor_value}).build()
        )

        assert len(output.records) == 1

    @HttpMocker()
    def test_given_input_state_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        state_cursor_value = _START_DATE.add(days=2)
        http_mocker.get(
            PostsRequestBuilder.posts_endpoint(api_token_authenticator)
            .with_start_time(datetime_to_string(state_cursor_value))
            .with_page_size(100)
            .build(),
            PostsResponseBuilder.posts_response().with_record(PostsRecordBuilder.posts_record()).build(),
        )

        output = read_stream(
            "posts",
            SyncMode.full_refresh,
            config,
            StateBuilder().with_stream_state("posts", {"updated_at": str(state_cursor_value.int_timestamp)}).build(),
        )

        assert len(output.records) == 1
