# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase

import freezegun
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import JiraRequestBuilder
from mock_server.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "workflows"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestWorkflowsStream(TestCase):
    """
    Tests for the Jira 'workflows' stream.

    This is a full refresh stream with pagination.
    Endpoint: /rest/api/3/workflow/search
    Extract field: values
    Primary key: [entityId, name]
    Transformations: AddFields (entityId, name from id.entityId and id.name)
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        workflow_records = [
            {
                "id": {"entityId": "entity-1", "name": "Default Workflow"},
                "description": "Default workflow for the project.",
                "transitions": [],
                "statuses": [],
            },
            {
                "id": {"entityId": "entity-2", "name": "Bug Workflow"},
                "description": "Workflow for bug issues.",
                "transitions": [],
                "statuses": [],
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.workflows_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(workflow_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        # Check that AddFields transformation added entityId and name at root level
        entity_ids = [r.record.data["entityId"] for r in output.records]
        assert "entity-1" in entity_ids
        assert "entity-2" in entity_ids

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly with multiple pages.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Page 1
        page1_workflows = [
            {"id": {"entityId": "entity-1", "name": "Workflow 1"}},
            {"id": {"entityId": "entity-2", "name": "Workflow 2"}},
        ]

        # Page 2
        page2_workflows = [
            {"id": {"entityId": "entity-3", "name": "Workflow 3"}},
        ]

        http_mocker.get(
            JiraRequestBuilder.workflows_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_workflows)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_workflows)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        entity_ids = [r.record.data["entityId"] for r in output.records]
        assert "entity-1" in entity_ids
        assert "entity-2" in entity_ids
        assert "entity-3" in entity_ids

    @HttpMocker()
    def test_transformation_adds_fields(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds entityId and name at root level.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        workflow_records = [
            {
                "id": {"entityId": "test-entity-id", "name": "Test Workflow Name"},
                "description": "Test workflow",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.workflows_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(workflow_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        # Verify AddFields transformation added these at root level
        assert record["entityId"] == "test-entity-id"
        assert record["name"] == "Test Workflow Name"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.workflows_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records([])
            .with_pagination(start_at=0, max_results=50, total=0, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
