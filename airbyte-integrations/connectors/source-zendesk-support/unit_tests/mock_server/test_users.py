# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import UserIdentitiesRecordBuilder, UsersRecordBuilder, UsersResponseBuilder
from .utils import datetime_to_string, read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "a_cursor"


def _config():
    return (
        ConfigBuilder()
        .with_basic_auth_credentials("user@example.com", "password")
        .with_subdomain("d3v-airbyte")
        .with_start_date(_START_DATE)
        .build()
    )


def _authenticator(config):
    return ApiTokenAuthenticator(email=config["credentials"]["email"], password=config["credentials"]["api_token"])


def _at(moment: AirbyteDateTime, **delta) -> str:
    return datetime_to_string(moment.add(timedelta(**delta)) if delta else moment)


def _user(user_id: int, updated_at: str) -> UsersRecordBuilder:
    return UsersRecordBuilder.users_record().with_id(user_id).with_cursor(updated_at)


def _next_page_url(after_cursor: str, include: str = "") -> str:
    """`links.next` as Zendesk builds it: the original query plus `page[after]`."""
    include = f"include={include}&" if include else ""
    return f"https://d3v-airbyte.zendesk.com/api/v2/users?{include}page%5Bafter%5D={after_cursor}&page%5Bsize%5D=100&sort=-updated_at"


@freezegun.freeze_time(_NOW.isoformat())
class TestUsersStream(TestCase):
    """`users` reads `GET /users?sort=-updated_at&page[size]=100` (newest first) and stops paginating once
    the last user of a page is older than the slice start."""

    @HttpMocker()
    def test_given_one_page_when_read_then_return_records(self, http_mocker):
        config = _config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.users_endpoint(_authenticator(config)).build(),
            UsersResponseBuilder.users_response().with_record(_user(1, _at(_START_DATE, days=2))).build(),
        )

        output = read_stream("users", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [1]

    @HttpMocker()
    def test_given_two_pages_when_read_then_follow_links_next(self, http_mocker):
        config = _config()
        authenticator = _authenticator(config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.users_endpoint(authenticator).build(),
            UsersResponseBuilder.users_response(_next_page_url(_A_CURSOR))
            .with_record(_user(1, _at(_START_DATE, days=3)))
            .with_record(_user(2, _at(_START_DATE, days=2)))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.users_endpoint(authenticator).with_after_cursor(_A_CURSOR).build(),
            UsersResponseBuilder.users_response().with_record(_user(3, _at(_START_DATE, days=1))).build(),
        )

        output = read_stream("users", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [1, 2, 3]

    @HttpMocker()
    def test_given_last_user_of_page_older_than_start_date_when_read_then_stop_paginating(self, http_mocker):
        config = _config()
        first_page = ZendeskSupportRequestBuilder.users_endpoint(_authenticator(config)).build()
        http_mocker.get(
            first_page,
            UsersResponseBuilder.users_response(_next_page_url(_A_CURSOR))
            .with_record(_user(1, _at(_START_DATE, days=1)))
            .with_record(_user(2, _at(_START_DATE, days=-1)))
            .with_pagination()
            .build(),
        )

        output = read_stream("users", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1]
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_when_read_then_set_state_value_to_most_recent_cursor_value(self, http_mocker):
        config = _config()
        most_recent = _START_DATE.add(timedelta(days=2))
        http_mocker.get(
            ZendeskSupportRequestBuilder.users_endpoint(_authenticator(config)).build(),
            UsersResponseBuilder.users_response()
            .with_record(_user(1, datetime_to_string(most_recent)))
            .with_record(_user(2, _at(_START_DATE, days=1)))
            .build(),
        )

        output = read_stream("users", SyncMode.incremental, config)

        assert len(output.records) == 2
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(int(most_recent.timestamp()))}

    @HttpMocker()
    def test_given_state_when_read_then_apply_lookback_and_drop_older_users(self, http_mocker):
        """State keeps the 5.x shape (`updated_at` as a unix timestamp string), so no migration is involved.
        Users updated within the one-hour lookback are re-read; older ones are dropped and end pagination."""
        config = _config()
        state_cursor = _NOW.subtract(timedelta(days=3))
        first_page = ZendeskSupportRequestBuilder.users_endpoint(_authenticator(config)).build()
        http_mocker.get(
            first_page,
            UsersResponseBuilder.users_response(_next_page_url(_A_CURSOR))
            .with_record(_user(1, _at(state_cursor, days=1)))
            .with_record(_user(2, _at(state_cursor, minutes=-30)))
            .with_record(_user(3, _at(state_cursor, hours=-2)))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("users", {"updated_at": str(int(state_cursor.timestamp()))}).build()
        output = read_stream("users", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(int(state_cursor.add(timedelta(days=1)).timestamp()))}
        http_mocker.assert_number_of_calls(first_page, 1)
