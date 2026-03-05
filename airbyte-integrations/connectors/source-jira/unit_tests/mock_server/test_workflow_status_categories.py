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
_STREAM_NAME = "workflow_status_categories"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestWorkflowStatusCategoriesStream(TestCase):
    """
    Tests for the Jira 'workflow_status_categories' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/statuscategory
    Uses selector_base (extracts from root array)
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all workflow status categories.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        category_records = [
            {
                "id": 1,
                "key": "undefined",
                "colorName": "medium-gray",
                "name": "No Category",
            },
            {
                "id": 2,
                "key": "new",
                "colorName": "blue-gray",
                "name": "To Do",
            },
            {
                "id": 3,
                "key": "done",
                "colorName": "green",
                "name": "Done",
            },
            {
                "id": 4,
                "key": "indeterminate",
                "colorName": "yellow",
                "name": "In Progress",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.workflow_status_categories_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(category_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 4

        category_ids = [r.record.data["id"] for r in output.records]
        assert 1 in category_ids
        assert 2 in category_ids
        assert 3 in category_ids
        assert 4 in category_ids

    @HttpMocker()
    def test_category_properties(self, http_mocker: HttpMocker):
        """
        Test that workflow status category properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        category_records = [
            {
                "id": 2,
                "key": "new",
                "colorName": "blue-gray",
                "name": "To Do",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.workflow_status_categories_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(category_records), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 2
        assert record["key"] == "new"
        assert record["colorName"] == "blue-gray"
        assert record["name"] == "To Do"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.workflow_status_categories_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
