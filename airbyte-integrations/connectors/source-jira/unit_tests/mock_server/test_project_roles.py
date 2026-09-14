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
_STREAM_NAME = "project_roles"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestProjectRolesStream(TestCase):
    """
    Tests for the Jira 'project_roles' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/role
    Primary key: id
    Uses selector_base (root array response)
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all project roles.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        roles = [
            {
                "id": 10000,
                "name": "Administrators",
                "description": "A project role that represents administrators in a project",
                "self": f"https://{_DOMAIN}/rest/api/3/project/10000/role/10000",
            },
            {
                "id": 10001,
                "name": "Developers",
                "description": "A project role that represents developers in a project",
                "self": f"https://{_DOMAIN}/rest/api/3/project/10000/role/10001",
            },
            {
                "id": 10002,
                "name": "Users",
                "description": "A project role that represents users in a project",
                "self": f"https://{_DOMAIN}/rest/api/3/project/10000/role/10002",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.project_roles_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(roles), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        role_ids = [r.record.data["id"] for r in output.records]
        assert 10000 in role_ids
        assert 10001 in role_ids
        assert 10002 in role_ids

    @HttpMocker()
    def test_role_properties(self, http_mocker: HttpMocker):
        """
        Test that role properties are correctly extracted.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        roles = [
            {
                "id": 10000,
                "name": "Administrators",
                "description": "Admin role",
                "self": f"https://{_DOMAIN}/rest/api/3/project/10000/role/10000",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.project_roles_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(roles), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 10000
        assert record["name"] == "Administrators"
        assert record["description"] == "Admin role"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.project_roles_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
