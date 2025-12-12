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
_STREAM_NAME = "project_categories"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectCategoriesStream(TestCase):
    """
    Tests for the Jira 'project_categories' stream.

    This is a simple full refresh stream without pagination.
    Endpoint: /rest/api/3/projectCategory
    Uses selector_base (extracts from root array)
    Error handler: 400 AND 403 errors are IGNORED
    """

    @HttpMocker()
    def test_full_refresh_single_record(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches project categories.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        category_records = [
            {
                "id": "10001",
                "name": "Development",
                "description": "Development projects",
                "self": f"https://{_DOMAIN}/rest/api/3/projectCategory/10001",
            },
            {
                "id": "10002",
                "name": "Marketing",
                "description": "Marketing projects",
                "self": f"https://{_DOMAIN}/rest/api/3/projectCategory/10002",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.project_categories_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(category_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        assert output.records[0].record.data["id"] == "10001"
        assert output.records[0].record.data["name"] == "Development"
        assert output.records[1].record.data["id"] == "10002"
        assert output.records[1].record.data["name"] == "Marketing"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.project_categories_endpoint(_DOMAIN).build(),
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

        The manifest configures 400 errors with action: IGNORE.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.project_categories_endpoint(_DOMAIN).build(),
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

    @HttpMocker()
    def test_error_403_ignored(self, http_mocker: HttpMocker):
        """
        Test that connector ignores 403 errors per the error handler.

        The manifest configures 403 errors with action: IGNORE.
        This is important because some users may not have permission to view project categories.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.project_categories_endpoint(_DOMAIN).build(),
            HttpResponse(
                body=json.dumps({"errorMessages": ["Forbidden"]}),
                status_code=403,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
