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


def _next_page_url(after_cursor: str) -> str:
    return f"https://d3v-airbyte.zendesk.com/api/v2/users?include=identities&page%5Bafter%5D={after_cursor}&page%5Bsize%5D=100&sort=-updated_at"


def _identity(identity_id: int, user_id: int, updated_at: str) -> UserIdentitiesRecordBuilder:
    return UserIdentitiesRecordBuilder.user_identities_record().with_id(identity_id).with_user_id(user_id).with_cursor(updated_at)


@freezegun.freeze_time(_NOW.isoformat())
class TestUserIdentitiesStream(TestCase):
    """`user_identities` reads the user list with `include=identities`: the records are the sideloaded
    `identities` of each page, while pagination stops on the `users` the page is sorted by."""

    @HttpMocker()
    def test_given_one_page_when_read_then_return_sideloaded_identities(self, http_mocker):
        config = _config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.user_identities_endpoint(_authenticator(config)).build(),
            UsersResponseBuilder.users_response()
            .with_record(_user(1, _at(_START_DATE, days=2)))
            .with_identity(_identity(11, 1, _at(_START_DATE, days=2)))
            .with_identity(_identity(12, 1, _at(_START_DATE, days=1)))
            .build(),
        )

        output = read_stream("user_identities", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [11, 12]

    @HttpMocker()
    def test_given_two_pages_when_read_then_follow_links_next(self, http_mocker):
        config = _config()
        authenticator = _authenticator(config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.user_identities_endpoint(authenticator).build(),
            UsersResponseBuilder.users_response(_next_page_url(_A_CURSOR))
            .with_record(_user(1, _at(_START_DATE, days=2)))
            .with_identity(_identity(11, 1, _at(_START_DATE, days=2)))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.user_identities_endpoint(authenticator).with_after_cursor(_A_CURSOR).build(),
            UsersResponseBuilder.users_response()
            .with_record(_user(2, _at(_START_DATE, days=1)))
            .with_identity(_identity(21, 2, _at(_START_DATE, days=1)))
            .build(),
        )

        output = read_stream("user_identities", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [11, 21]

    @HttpMocker()
    def test_given_last_user_of_page_older_than_start_date_when_read_then_stop_paginating(self, http_mocker):
        """Pagination stops on the users, not on the identities, and the identities of the last page are
        emitted even when their user is already older than the window (no record filter)."""
        config = _config()
        first_page = ZendeskSupportRequestBuilder.user_identities_endpoint(_authenticator(config)).build()
        http_mocker.get(
            first_page,
            UsersResponseBuilder.users_response(_next_page_url(_A_CURSOR))
            .with_record(_user(1, _at(_START_DATE, days=1)))
            .with_record(_user(2, _at(_START_DATE, days=-1)))
            .with_identity(_identity(11, 1, _at(_START_DATE, days=1)))
            .with_identity(_identity(21, 2, _at(_START_DATE, days=-1)))
            .with_pagination()
            .build(),
        )

        output = read_stream("user_identities", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [11, 21]
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_given_state_when_read_then_unchanged_identities_of_updated_users_are_kept(self, http_mocker):
        """An identity's `updated_at` never exceeds its user's. The identities of a user updated after the
        cursor are emitted whether or not they changed themselves, as the export used to do, and state
        is the most recent identity `updated_at`."""
        config = _config()
        state_cursor = _NOW.subtract(timedelta(days=3))
        http_mocker.get(
            ZendeskSupportRequestBuilder.user_identities_endpoint(_authenticator(config)).build(),
            UsersResponseBuilder.users_response()
            .with_record(_user(1, _at(state_cursor, days=1)))
            .with_identity(_identity(11, 1, _at(state_cursor, days=1)))
            .with_identity(_identity(12, 1, _at(state_cursor, days=-30)))
            .build(),
        )

        state = StateBuilder().with_stream_state("user_identities", {"updated_at": str(int(state_cursor.timestamp()))}).build()
        output = read_stream("user_identities", SyncMode.incremental, config, state)

        assert [r.record.data["id"] for r in output.records] == [11, 12]
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(int(state_cursor.add(timedelta(days=1)).timestamp()))}
