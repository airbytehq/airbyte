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
    Tests for the Jira `workflows` stream.

    This is a full refresh stream with pagination.
    Endpoint: `/rest/api/3/workflows/search`
    Extract field: `values`
    Primary key: `[id]` (top-level UUID string on the new endpoint).
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """Full refresh sync with a single page of results."""
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        workflow_records = [
            {
                "id": "385bb764-dfb6-89a7-2e43-a25bdd0cbaf4",
                "name": "Default Workflow",
                "description": "Default workflow for the project.",
                "transitions": [],
                "statuses": [],
            },
            {
                "id": "9b1c1234-abcd-ef00-1234-56789abcdef0",
                "name": "Bug Workflow",
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

        ids = [r.record.data["id"] for r in output.records]
        assert "385bb764-dfb6-89a7-2e43-a25bdd0cbaf4" in ids
        assert "9b1c1234-abcd-ef00-1234-56789abcdef0" in ids

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """Pagination works correctly with multiple pages."""
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        page1_workflows = [
            {"id": "id-1", "name": "Workflow 1"},
            {"id": "id-2", "name": "Workflow 2"},
        ]
        page2_workflows = [
            {"id": "id-3", "name": "Workflow 3"},
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
        ids = {r.record.data["id"] for r in output.records}
        assert ids == {"id-1", "id-2", "id-3"}

    @HttpMocker()
    def test_top_level_id_and_name_pass_through(self, http_mocker: HttpMocker):
        """
        The replacement endpoint returns `id` (a UUID string) and `name` at
        the top level of each record. Verify that both fields reach the
        destination record unmodified.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        workflow_records = [
            {
                "id": "test-uuid-0001",
                "name": "Test Workflow Name",
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
        assert record["id"] == "test-uuid-0001"
        assert record["name"] == "Test Workflow Name"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """Empty results are handled gracefully."""
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
