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
_STREAM_NAME = "project_components"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectComponentsStream(TestCase):
    """
    Tests for the Jira 'project_components' stream.

    This is a substream that depends on projects as parent.
    Endpoint: /rest/api/3/project/{project_key}/component
    Extract field: values
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_projects(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with components from multiple projects.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock projects endpoint (parent stream)
        projects = [
            {"id": "10000", "key": "PROJ1", "name": "Project 1"},
            {"id": "10001", "key": "PROJ2", "name": "Project 2"},
        ]

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(projects)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock project components for project 1
        project1_components = [
            {"id": "10100", "name": "Backend", "description": "Backend component"},
            {"id": "10101", "name": "Frontend", "description": "Frontend component"},
        ]

        # Mock project components for project 2
        project2_components = [
            {"id": "10200", "name": "API", "description": "API component"},
        ]

        http_mocker.get(
            JiraRequestBuilder.project_components_endpoint(_DOMAIN, "PROJ1").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(project1_components)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )
        http_mocker.get(
            JiraRequestBuilder.project_components_endpoint(_DOMAIN, "PROJ2").with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(project2_components)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        component_ids = [r.record.data["id"] for r in output.records]
        assert "10100" in component_ids
        assert "10101" in component_ids
        assert "10200" in component_ids

    @HttpMocker()
    def test_pagination_within_project(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly within a project.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        projects = [
            {"id": "10000", "key": "PROJ1", "name": "Project 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(projects)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Page 1
        page1_components = [
            {"id": "10100", "name": "Component 1"},
            {"id": "10101", "name": "Component 2"},
        ]

        # Page 2
        page2_components = [
            {"id": "10102", "name": "Component 3"},
        ]

        http_mocker.get(
            JiraRequestBuilder.project_components_endpoint(_DOMAIN, "PROJ1").with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_components)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_components)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        component_ids = [r.record.data["id"] for r in output.records]
        assert "10100" in component_ids
        assert "10101" in component_ids
        assert "10102" in component_ids

    @HttpMocker()
    def test_empty_projects(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty projects gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
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

    @HttpMocker()
    def test_project_with_no_components(self, http_mocker: HttpMocker):
        """
        Test that connector handles projects with no components gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        projects = [
            {"id": "10000", "key": "PROJ1", "name": "Project 1"},
        ]

        http_mocker.get(
            JiraRequestBuilder.projects_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(projects)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        http_mocker.get(
            JiraRequestBuilder.project_components_endpoint(_DOMAIN, "PROJ1").with_any_query_params().build(),
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
