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
from mock_server.response_builder import JiraPaginatedResponseBuilder


_NOW = datetime.now(timezone.utc)
_STREAM_NAME = "project_permission_schemes"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectPermissionSchemesStream(TestCase):
    """
    Tests for the Jira 'project_permission_schemes' stream.

    This is a substream that depends on projects as parent.
    Endpoint: /rest/api/3/project/{project_key}/securitylevel
    Extract field: levels
    Primary key: id
    Transformations: AddFields (projectId)
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_projects(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with security levels from multiple projects.
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

        # Mock project security levels for project 1
        project1_levels = {
            "levels": [
                {"id": "10100", "name": "Level 1", "description": "Security level 1"},
                {"id": "10101", "name": "Level 2", "description": "Security level 2"},
            ]
        }

        # Mock project security levels for project 2
        project2_levels = {
            "levels": [
                {"id": "10200", "name": "Level A", "description": "Security level A"},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.project_permission_schemes_endpoint(_DOMAIN, "PROJ1").build(),
            HttpResponse(body=json.dumps(project1_levels), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.project_permission_schemes_endpoint(_DOMAIN, "PROJ2").build(),
            HttpResponse(body=json.dumps(project2_levels), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        level_ids = [r.record.data["id"] for r in output.records]
        assert "10100" in level_ids
        assert "10101" in level_ids
        assert "10200" in level_ids

        # Verify projectId transformation is applied
        for record in output.records:
            assert "projectId" in record.record.data

    @HttpMocker()
    def test_project_id_transformation(self, http_mocker: HttpMocker):
        """
        Test that AddFields transformation correctly adds projectId.
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

        project_levels = {
            "levels": [
                {"id": "10100", "name": "Level 1"},
            ]
        }

        http_mocker.get(
            JiraRequestBuilder.project_permission_schemes_endpoint(_DOMAIN, "PROJ1").build(),
            HttpResponse(body=json.dumps(project_levels), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["projectId"] == "PROJ1"

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
    def test_project_with_no_security_levels(self, http_mocker: HttpMocker):
        """
        Test that connector handles projects with no security levels gracefully.
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
            JiraRequestBuilder.project_permission_schemes_endpoint(_DOMAIN, "PROJ1").build(),
            HttpResponse(body=json.dumps({"levels": []}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
