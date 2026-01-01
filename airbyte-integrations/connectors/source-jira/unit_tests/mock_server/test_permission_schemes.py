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
_STREAM_NAME = "permission_schemes"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestPermissionSchemesStream(TestCase):
    """
    Tests for the Jira 'permission_schemes' stream.

    This is a full refresh stream without pagination (uses retriever_no_pagination).
    Endpoint: /rest/api/3/permissionscheme
    Extract field: permissionSchemes
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all permission schemes.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        permission_scheme_records = [
            {
                "id": 10000,
                "name": "Default Permission Scheme",
                "description": "Default permission scheme for the project.",
                "self": f"https://{_DOMAIN}/rest/api/3/permissionscheme/10000",
            },
            {
                "id": 10001,
                "name": "Custom Permission Scheme",
                "description": "Custom permission scheme.",
                "self": f"https://{_DOMAIN}/rest/api/3/permissionscheme/10001",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.permission_schemes_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"permissionSchemes": permission_scheme_records}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        scheme_ids = [r.record.data["id"] for r in output.records]
        assert 10000 in scheme_ids
        assert 10001 in scheme_ids

    @HttpMocker()
    def test_scheme_properties(self, http_mocker: HttpMocker):
        """
        Test that permission scheme properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        permission_scheme_records = [
            {
                "id": 10002,
                "name": "Admin Permission Scheme",
                "description": "Permission scheme for administrators.",
                "self": f"https://{_DOMAIN}/rest/api/3/permissionscheme/10002",
                "scope": {"type": "PROJECT"},
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.permission_schemes_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"permissionSchemes": permission_scheme_records}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["id"] == 10002
        assert record["name"] == "Admin Permission Scheme"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.permission_schemes_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"permissionSchemes": []}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
