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
_STREAM_NAME = "users_groups_detailed"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestUsersGroupsDetailedStream(TestCase):
    """
    Tests for the Jira 'users_groups_detailed' stream.

    This is a substream that depends on users as parent.
    Endpoint: /rest/api/3/user
    Primary key: accountId
    Request parameters: accountId, expand=groups,applicationRoles
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_users(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with detailed info for multiple users.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock users endpoint (parent stream) - uses selector_base (root array) with OffsetIncrement pagination
        users = [
            {"accountId": "user1", "displayName": "User 1", "emailAddress": "user1@example.com"},
            {"accountId": "user2", "displayName": "User 2", "emailAddress": "user2@example.com"},
        ]

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN).with_any_query_params().build(),
            HttpResponse(body=json.dumps(users), status_code=200),
        )

        # Mock user details for user 1
        user1_details = {
            "accountId": "user1",
            "displayName": "User 1",
            "emailAddress": "user1@example.com",
            "groups": {"items": [{"name": "jira-users"}]},
            "applicationRoles": {"items": [{"key": "jira-software"}]},
        }

        # Mock user details for user 2
        user2_details = {
            "accountId": "user2",
            "displayName": "User 2",
            "emailAddress": "user2@example.com",
            "groups": {"items": [{"name": "jira-admins"}]},
            "applicationRoles": {"items": []},
        }

        http_mocker.get(
            JiraRequestBuilder.users_groups_detailed_endpoint(_DOMAIN)
            .with_query_param("accountId", "user1")
            .with_query_param("expand", "groups,applicationRoles")
            .build(),
            HttpResponse(body=json.dumps(user1_details), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.users_groups_detailed_endpoint(_DOMAIN)
            .with_query_param("accountId", "user2")
            .with_query_param("expand", "groups,applicationRoles")
            .build(),
            HttpResponse(body=json.dumps(user2_details), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        account_ids = [r.record.data["accountId"] for r in output.records]
        assert "user1" in account_ids
        assert "user2" in account_ids

    @HttpMocker()
    def test_user_with_groups(self, http_mocker: HttpMocker):
        """
        Test that user groups are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        users = [
            {"accountId": "user1", "displayName": "User 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.users_endpoint(_DOMAIN).with_any_query_params().build(),
            HttpResponse(body=json.dumps(users), status_code=200),
        )

        user_details = {
            "accountId": "user1",
            "displayName": "User 1",
            "groups": {"items": [{"name": "jira-users"}, {"name": "developers"}]},
            "applicationRoles": {"items": [{"key": "jira-software"}]},
        }

        http_mocker.get(
            JiraRequestBuilder.users_groups_detailed_endpoint(_DOMAIN)
            .with_query_param("accountId", "user1")
            .with_query_param("expand", "groups,applicationRoles")
            .build(),
            HttpResponse(body=json.dumps(user_details), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["accountId"] == "user1"
        assert "groups" in record
        assert len(record["groups"]["items"]) == 2

    @HttpMocker()
    def test_empty_users(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty users gracefully.
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
