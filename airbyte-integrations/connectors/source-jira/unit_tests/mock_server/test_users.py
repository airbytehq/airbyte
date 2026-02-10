# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "users"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestUsersStream(TestCase):
    """
    Tests for the Jira 'users' stream.

    This is a full refresh stream with offset-based pagination.
    Endpoint: /rest/api/3/users/search
    Uses OffsetIncrement pagination with page_size=50
    Uses selector_base (extracts from root array)
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches users in a single page.

        When fewer than page_size (50) records are returned, pagination stops.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        user_records = [
            {
                "accountId": "user1",
                "accountType": "atlassian",
                "displayName": "User One",
                "emailAddress": "user1@example.com",
                "self": f"https://{_DOMAIN}/rest/api/3/user?accountId=user1",
            },
            {
                "accountId": "user2",
                "accountType": "atlassian",
                "displayName": "User Two",
                "emailAddress": "user2@example.com",
                "self": f"https://{_DOMAIN}/rest/api/3/user?accountId=user2",
            },
        ]

        # Single request returns users - pagination stops when fewer than page_size returned
        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN).with_any_query_params().build(),
            HttpResponse(body=json.dumps(user_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["accountId"] == "user1"
        assert output.records[0].record.data["displayName"] == "User One"
        assert output.records[1].record.data["accountId"] == "user2"

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that connector correctly handles offset-based pagination.

        Uses OffsetIncrement pagination with page_size=50.
        Pagination stops when fewer than page_size records are returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Page 1: 50 users (full page, triggers next request)
        page1_users = [{"accountId": f"user{i}", "displayName": f"User {i}"} for i in range(1, 51)]
        # Page 2: 10 users (less than page_size, stops pagination)
        page2_users = [{"accountId": f"user{i}", "displayName": f"User {i}"} for i in range(51, 61)]

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                HttpResponse(body=json.dumps(page1_users), status_code=200),
                HttpResponse(body=json.dumps(page2_users), status_code=200),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 60
        # Verify first and last users
        assert output.records[0].record.data["accountId"] == "user1"
        assert output.records[59].record.data["accountId"] == "user60"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN).with_any_query_params().build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that connector ignores 400 errors per the error handler.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN).with_any_query_params().build(),
            HttpResponse(
                body=json.dumps({"errorMessages": ["Bad request"]}),
                status_code=400,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
