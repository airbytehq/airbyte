# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
import pendulum

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder

from .config import ConfigBuilder
from .utils import datetime_to_string, read_stream
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_requests.users_request_builder import UsersRequestBuilder
from .zs_responses.records.users_records_builder import UsersRecordBuilder
from .zs_responses.users_response_builder import UsersResponseBuilder


_NOW = datetime.now(timezone.utc)
_START_DATE = pendulum.now(tz="UTC").subtract(years=2)
_A_CURSOR = "a_cursor"


@freezegun.freeze_time(_NOW.isoformat())
class TestUserIdentitiesStream(TestCase):
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
            UsersRequestBuilder.endpoint(api_token_authenticator).with_include("identities").with_start_time(_START_DATE).build(),
            UsersResponseBuilder.identities_response()
            .with_record(UsersRecordBuilder.record())
            .with_record(UsersRecordBuilder.record())
            .build(),
        )

        output = read_stream("user_identities", SyncMode.full_refresh, config)

        assert len(output.records) == 2

    @HttpMocker()
    def test_given_next_page_when_read_then_paginate(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        http_mocker.get(
            UsersRequestBuilder.endpoint(api_token_authenticator).with_include("identities").with_start_time(_START_DATE).build(),
            UsersResponseBuilder.identities_response(UsersRequestBuilder.endpoint(api_token_authenticator).build(), _A_CURSOR)
            .with_record(UsersRecordBuilder.record())
            .with_record(UsersRecordBuilder.record())
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            UsersRequestBuilder.endpoint(api_token_authenticator).with_include("identities").with_cursor(_A_CURSOR).build(),
            UsersResponseBuilder.identities_response().with_record(UsersRecordBuilder.record()).build(),
        )

        output = read_stream("user_identities", SyncMode.full_refresh, config)

        assert len(output.records) == 3

    @HttpMocker()
    def test_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        most_recent_cursor_value = _START_DATE.add(days=2)
        http_mocker.get(
            UsersRequestBuilder.endpoint(api_token_authenticator).with_include("identities").with_start_time(_START_DATE).build(),
            UsersResponseBuilder.identities_response()
            .with_record(UsersRecordBuilder.record().with_cursor(datetime_to_string(most_recent_cursor_value)))
            .build(),
        )

        output = read_stream("user_identities", SyncMode.full_refresh, config)

        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(most_recent_cursor_value.int_timestamp)}

    @HttpMocker()
    def test_given_input_state_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = self._config().with_start_date(_START_DATE).build()
        api_token_authenticator = self._get_authenticator(config)
        state_cursor_value = _START_DATE.add(days=2)
        http_mocker.get(
            UsersRequestBuilder.endpoint(api_token_authenticator).with_include("identities").with_start_time(state_cursor_value).build(),
            UsersResponseBuilder.identities_response().with_record(UsersRecordBuilder.record()).build(),
        )

        output = read_stream(
            "user_identities",
            SyncMode.full_refresh,
            config,
            StateBuilder().with_stream_state("user_identities", {"updated_at": datetime_to_string(state_cursor_value)}).build(),
        )

        assert len(output.records) == 1
