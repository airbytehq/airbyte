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
_STREAM_NAME = "issue_link_types"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestIssueLinkTypesStream(TestCase):
    """
    Tests for the Jira 'issue_link_types' stream.

    This is a full refresh stream without pagination.
    Endpoint: /rest/api/3/issueLinkType
    Extract field: issueLinkTypes
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh(self, http_mocker: HttpMocker):
        """
        Test full refresh sync returns all issue link types.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        link_type_records = [
            {
                "id": "10000",
                "name": "Blocks",
                "inward": "is blocked by",
                "outward": "blocks",
                "self": f"https://{_DOMAIN}/rest/api/3/issueLinkType/10000",
            },
            {
                "id": "10001",
                "name": "Cloners",
                "inward": "is cloned by",
                "outward": "clones",
                "self": f"https://{_DOMAIN}/rest/api/3/issueLinkType/10001",
            },
            {
                "id": "10002",
                "name": "Duplicate",
                "inward": "is duplicated by",
                "outward": "duplicates",
                "self": f"https://{_DOMAIN}/rest/api/3/issueLinkType/10002",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_link_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"issueLinkTypes": link_type_records}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        link_type_ids = [r.record.data["id"] for r in output.records]
        assert "10000" in link_type_ids
        assert "10001" in link_type_ids
        assert "10002" in link_type_ids

    @HttpMocker()
    def test_link_type_properties(self, http_mocker: HttpMocker):
        """
        Test that link type properties are correctly returned.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        link_type_records = [
            {
                "id": "10000",
                "name": "Blocks",
                "inward": "is blocked by",
                "outward": "blocks",
                "self": f"https://{_DOMAIN}/rest/api/3/issueLinkType/10000",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.issue_link_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"issueLinkTypes": link_type_records}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["name"] == "Blocks"
        assert record["inward"] == "is blocked by"
        assert record["outward"] == "blocks"

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.issue_link_types_endpoint(_DOMAIN).build(),
            HttpResponse(body=json.dumps({"issueLinkTypes": []}), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
