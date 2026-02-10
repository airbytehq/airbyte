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
_STREAM_NAME = "application_roles"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestApplicationRolesStream(TestCase):
    """
    Tests for the Jira 'application_roles' stream.

    This is a simple full refresh stream without pagination.
    It uses selector_base (extracts from root array) and no pagination.
    """

    @HttpMocker()
    def test_full_refresh_single_record(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches application roles.

        Given: A configured Jira connector
        When: Running a full refresh sync for the application_roles stream
        Then: The connector should make the correct API request and return all records
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.application_roles_endpoint(_DOMAIN).build(),
            HttpResponse(
                body=json.dumps(
                    [
                        {
                            "key": "jira-software",
                            "groups": ["jira-software-users", "administrators"],
                            "name": "Jira Software",
                            "defaultGroups": ["jira-software-users"],
                            "selectedByDefault": False,
                            "defined": True,
                            "numberOfSeats": 100,
                            "remainingSeats": 61,
                            "userCount": 14,
                            "userCountDescription": "users",
                            "hasUnlimitedSeats": False,
                            "platform": False,
                        }
                    ]
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["key"] == "jira-software"
        assert record["name"] == "Jira Software"
        assert record["numberOfSeats"] == 100
        assert record["userCount"] == 14

    @HttpMocker()
    def test_full_refresh_multiple_records(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches multiple application roles.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.application_roles_endpoint(_DOMAIN).build(),
            HttpResponse(
                body=json.dumps(
                    [
                        {
                            "key": "jira-software",
                            "groups": ["jira-software-users"],
                            "name": "Jira Software",
                            "defaultGroups": ["jira-software-users"],
                            "selectedByDefault": False,
                            "defined": True,
                            "numberOfSeats": 100,
                            "remainingSeats": 61,
                            "userCount": 14,
                            "userCountDescription": "users",
                            "hasUnlimitedSeats": False,
                            "platform": False,
                        },
                        {
                            "key": "jira-core",
                            "groups": ["jira-core-users"],
                            "name": "Jira Core",
                            "defaultGroups": ["jira-core-users"],
                            "selectedByDefault": True,
                            "defined": True,
                            "numberOfSeats": 50,
                            "remainingSeats": 30,
                            "userCount": 20,
                            "userCountDescription": "users",
                            "hasUnlimitedSeats": False,
                            "platform": True,
                        },
                    ]
                ),
                status_code=200,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["key"] == "jira-software"
        assert output.records[1].record.data["key"] == "jira-core"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.application_roles_endpoint(_DOMAIN).build(),
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
        Test that connector ignores 400 errors per the default error handler.

        The manifest configures 400 errors with action: IGNORE, which means the connector
        silently ignores bad request errors and continues the sync with 0 records.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.application_roles_endpoint(_DOMAIN).build(),
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
