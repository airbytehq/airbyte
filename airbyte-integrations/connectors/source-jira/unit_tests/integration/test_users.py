# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from integration.config import ConfigBuilder
from integration.request_builder import JiraRequestBuilder
from integration.response_builder import JiraListResponseBuilder, JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "users"
_DOMAIN = "test.atlassian.net"
_EMAIL = "test@example.com"
_API_TOKEN = "test_api_token"


@freezegun.freeze_time(_NOW.isoformat())
class TestUsersStream(TestCase):
    """
    Tests for the Jira 'users' stream.

    The users stream uses OffsetIncrement pagination with page_size 50.
    It returns a list of users without pagination metadata wrapper.
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches one page of users.

        Given: A configured Jira connector
        When: Running a full refresh sync for the users stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraListResponseBuilder.build(
                [
                    {
                        "accountId": "user-001",
                        "accountType": "atlassian",
                        "displayName": "John Doe",
                        "emailAddress": "john@example.com",
                        "active": True,
                    },
                    {
                        "accountId": "user-002",
                        "accountType": "atlassian",
                        "displayName": "Jane Smith",
                        "emailAddress": "jane@example.com",
                        "active": True,
                    },
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["accountId"] == "user-001"
        assert output.records[0].record.data["displayName"] == "John Doe"
        assert output.records[1].record.data["accountId"] == "user-002"
        assert output.records[1].record.data["displayName"] == "Jane Smith"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector fetches all pages when pagination is present.

        The users stream uses OffsetIncrement pagination. When the response contains
        fewer records than the page_size (50), pagination stops.

        Given: An API that returns multiple pages of users
        When: Running a full refresh sync
        Then: The connector should follow pagination and return all records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        # Use a list of responses to simulate pagination - responses are returned in order
        # First page returns 50 records (full page), second page returns fewer (last page)
        first_page_users = [{"accountId": f"user-{i:03d}", "displayName": f"User {i}"} for i in range(50)]
        second_page_users = [{"accountId": "user-050", "displayName": "User 50"}]

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            [
                JiraListResponseBuilder.build(first_page_users),
                JiraListResponseBuilder.build(second_page_users),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 51
        assert output.records[0].record.data["accountId"] == "user-000"
        assert output.records[50].record.data["accountId"] == "user-050"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.

        Given: An API that returns no users
        When: Running a full refresh sync
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_domain(_DOMAIN).with_email(_EMAIL).with_api_token(_API_TOKEN).build()

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN, _EMAIL, _API_TOKEN)
            .with_any_query_params()
            .build(),
            JiraListResponseBuilder.empty(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
