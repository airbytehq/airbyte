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
_STREAM_NAME = "project_email"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectEmailStream(TestCase):
    """
    Tests for the Jira 'project_email' stream.

    This is a substream that depends on projects as parent.
    Endpoint: /rest/api/3/project/{project_id}/email
    Primary key: projectId
    Transformations: AddFields (projectId)
    Error handler: 400/403 IGNORE
    """

    @HttpMocker()
    def test_full_refresh_with_multiple_projects(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with email from multiple projects.
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

        # Mock project email for project 1
        project1_email = {"emailAddress": "project1@example.com", "emailAddressStatus": ["VALID"]}

        # Mock project email for project 2
        project2_email = {"emailAddress": "project2@example.com", "emailAddressStatus": ["VALID"]}

        http_mocker.get(
            JiraRequestBuilder.project_email_endpoint(_DOMAIN, "10000").build(),
            HttpResponse(body=json.dumps(project1_email), status_code=200),
        )
        http_mocker.get(
            JiraRequestBuilder.project_email_endpoint(_DOMAIN, "10001").build(),
            HttpResponse(body=json.dumps(project2_email), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        # Verify projectId transformation is applied
        project_ids = [r.record.data["projectId"] for r in output.records]
        assert "10000" in project_ids
        assert "10001" in project_ids

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

        project_email = {"emailAddress": "project@example.com"}

        http_mocker.get(
            JiraRequestBuilder.project_email_endpoint(_DOMAIN, "10000").build(),
            HttpResponse(body=json.dumps(project_email), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["projectId"] == "10000"
        assert record["emailAddress"] == "project@example.com"

    @HttpMocker()
    def test_error_403_ignored(self, http_mocker: HttpMocker):
        """
        Test that 403 errors are ignored gracefully.
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
            JiraRequestBuilder.project_email_endpoint(_DOMAIN, "10000").build(),
            HttpResponse(body=json.dumps({"errorMessages": ["Forbidden"]}), status_code=403),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)

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
