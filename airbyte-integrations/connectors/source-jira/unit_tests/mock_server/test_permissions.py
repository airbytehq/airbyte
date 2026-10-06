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
_STREAM_NAME = "permissions"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestPermissionsStream(TestCase):
    """
    Tests for the Jira 'permissions' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/permissions
    Extract field: permissions.*
    Primary key: key
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all permissions.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        permissions_response = {
            "permissions": {
                "BROWSE_PROJECTS": {
                    "key": "BROWSE_PROJECTS",
                    "name": "Browse Projects",
                    "type": "PROJECT",
                    "description": "Ability to browse projects and the issues within them.",
                },
                "CREATE_ISSUES": {
                    "key": "CREATE_ISSUES",
                    "name": "Create Issues",
                    "type": "PROJECT",
                    "description": "Ability to create issues.",
                },
                "ADMINISTER_PROJECTS": {
                    "key": "ADMINISTER_PROJECTS",
                    "name": "Administer Projects",
                    "type": "PROJECT",
                    "description": "Ability to administer a project in Jira.",
                },
            }
        }

        http_mocker.get(
            JiraRequestBuilder.permissions_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(permissions_response), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        permission_keys = [r.record.data["key"] for r in output.records]
        assert "BROWSE_PROJECTS" in permission_keys
        assert "CREATE_ISSUES" in permission_keys
        assert "ADMINISTER_PROJECTS" in permission_keys

    @HttpMocker()
    def test_permission_properties(self, http_mocker: HttpMocker):
        """
        Test that permission properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        permissions_response = {
            "permissions": {
                "EDIT_ISSUES": {
                    "key": "EDIT_ISSUES",
                    "name": "Edit Issues",
                    "type": "PROJECT",
                    "description": "Ability to edit issues.",
                },
            }
        }

        http_mocker.get(
            JiraRequestBuilder.permissions_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps(permissions_response), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["key"] == "EDIT_ISSUES"
        assert record["name"] == "Edit Issues"
        assert record["type"] == "PROJECT"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.permissions_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"permissions": {}}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
