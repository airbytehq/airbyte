# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import timedelta
from unittest import TestCase

import freezegun

from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_now

from .config import ConfigBuilder
from .request_builder import ApiTokenAuthenticator, ZendeskSupportRequestBuilder
from .response_builder import ErrorResponseBuilder, OrganizationsRecordBuilder, OrganizationsResponseBuilder
from .utils import datetime_to_string, get_log_messages_by_log_level, read_stream


_NOW = ab_datetime_now()
_START_DATE = _NOW.subtract(timedelta(weeks=104))
_A_CURSOR = "MTU3NjYxMzUzOS4wfHw0Njd8"


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


def _organization(organization_id: int, updated_at: str) -> OrganizationsRecordBuilder:
    return OrganizationsRecordBuilder.organizations_record().with_id(organization_id).with_cursor(updated_at)


def _next_page_url(after_cursor: str) -> str:
    """`links.next` as Zendesk builds it: the original query plus `page[after]`."""
    return f"https://d3v-airbyte.zendesk.com/api/v2/organizations?page%5Bafter%5D={after_cursor}&page%5Bsize%5D=100&sort=-updated_at"


@freezegun.freeze_time(_NOW.isoformat())
class TestOrganizationsStreamFullRefresh(TestCase):
    """`organizations` reads `GET /organizations?sort=-updated_at&page[size]=100` (newest first) and stops
    paginating once the last organization of a page is older than the slice start."""

    @HttpMocker()
    def test_given_one_page_when_read_organizations_then_return_records(self, http_mocker):
        config = _config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build(),
            OrganizationsResponseBuilder.organizations_response().with_record(_organization(1, _at(_START_DATE, days=2))).build(),
        )

        output = read_stream("organizations", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [1]

    @HttpMocker()
    def test_given_two_pages_when_read_organizations_then_follow_links_next(self, http_mocker):
        config = _config()
        authenticator = _authenticator(config)
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(authenticator).build(),
            OrganizationsResponseBuilder.organizations_response(_next_page_url(_A_CURSOR))
            .with_record(_organization(1, _at(_START_DATE, days=3)))
            .with_record(_organization(2, _at(_START_DATE, days=2)))
            .with_pagination()
            .build(),
        )
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(authenticator).with_after_cursor(_A_CURSOR).build(),
            OrganizationsResponseBuilder.organizations_response().with_record(_organization(3, _at(_START_DATE, days=1))).build(),
        )

        output = read_stream("organizations", SyncMode.full_refresh, config)

        assert [r.record.data["id"] for r in output.records] == [1, 2, 3]

    @HttpMocker()
    def test_given_last_organization_of_page_older_than_start_date_when_read_then_stop_paginating(self, http_mocker):
        config = _config()
        first_page = ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build()
        http_mocker.get(
            first_page,
            OrganizationsResponseBuilder.organizations_response(_next_page_url(_A_CURSOR))
            .with_record(_organization(1, _at(_START_DATE, days=1)))
            .with_record(_organization(2, _at(_START_DATE, days=-1)))
            .with_pagination()
            .build(),
        )

        output = read_stream("organizations", SyncMode.full_refresh, config)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1]
        http_mocker.assert_number_of_calls(first_page, 1)


@freezegun.freeze_time(_NOW.isoformat())
class TestOrganizationsStreamIncremental(TestCase):
    @HttpMocker()
    def test_given_no_state_when_read_organizations_then_return_records_and_emit_state(self, http_mocker):
        config = _config()
        most_recent = _START_DATE.add(timedelta(days=1))
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build(),
            OrganizationsResponseBuilder.organizations_response().with_record(_organization(1, datetime_to_string(most_recent))).build(),
        )

        output = read_stream("organizations", SyncMode.incremental, config)

        assert len(output.records) == 1
        assert output.most_recent_state.stream_descriptor.name == "organizations"
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(int(most_recent.timestamp()))}

    @HttpMocker()
    def test_given_state_when_read_organizations_then_apply_lookback_and_drop_older_organizations(self, http_mocker):
        """State keeps the 5.x shape (`updated_at` as a unix timestamp string), so no migration is involved."""
        config = _config()
        state_cursor = _NOW.subtract(timedelta(days=3))
        first_page = ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build()
        http_mocker.get(
            first_page,
            OrganizationsResponseBuilder.organizations_response(_next_page_url(_A_CURSOR))
            .with_record(_organization(1, _at(state_cursor, days=1)))
            .with_record(_organization(2, _at(state_cursor, minutes=-30)))
            .with_record(_organization(3, _at(state_cursor, hours=-2)))
            .with_pagination()
            .build(),
        )

        state = StateBuilder().with_stream_state("organizations", {"updated_at": str(int(state_cursor.timestamp()))}).build()
        output = read_stream("organizations", SyncMode.incremental, config, state)

        assert len(output.errors) == 0
        assert [r.record.data["id"] for r in output.records] == [1, 2]
        assert output.most_recent_state.stream_state.__dict__ == {"updated_at": str(int(state_cursor.add(timedelta(days=1)).timestamp()))}
        http_mocker.assert_number_of_calls(first_page, 1)

    @HttpMocker()
    def test_given_403_permission_denied_when_read_organizations_then_ignore_and_skip_stream(self, http_mocker):
        """When Zendesk returns 403 with 'You do not have access', the stream should be skipped."""
        config = _config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build(),
            ErrorResponseBuilder.response_with_status(403)
            .with_error_message(
                "You do not have access to this page. You do not have permission to access this page. Please contact the account owner of this help desk for further help."
            )
            .build(),
        )

        output = read_stream("organizations", SyncMode.incremental, config)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert not any("403" in msg for msg in error_logs), "403 permission-denied should not produce ERROR logs"

    @HttpMocker()
    def test_given_403_other_error_when_read_organizations_then_fail(self, http_mocker):
        """When Zendesk returns 403 without the permission-denied message, the sync should fail."""
        config = _config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build(),
            ErrorResponseBuilder.response_with_status(403).with_error_message("Forbidden").build(),
        )

        output = read_stream("organizations", SyncMode.incremental, config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("403" in msg for msg in error_logs), "Expected 403 error code in logs"
        assert any("Forbidden" in msg for msg in error_logs), "Expected error message in logs"

    @HttpMocker()
    def test_given_404_error_when_read_organizations_then_fail(self, http_mocker):
        """404 errors should still fail the sync."""
        config = _config()
        http_mocker.get(
            ZendeskSupportRequestBuilder.organizations_endpoint(_authenticator(config)).build(),
            ErrorResponseBuilder.response_with_status(404).build(),
        )

        output = read_stream("organizations", SyncMode.incremental, config, expecting_exception=True)

        assert len(output.records) == 0
        error_logs = list(get_log_messages_by_log_level(output.logs, LogLevel.ERROR))
        assert any("404" in msg for msg in error_logs), "Expected 404 error code in logs"
