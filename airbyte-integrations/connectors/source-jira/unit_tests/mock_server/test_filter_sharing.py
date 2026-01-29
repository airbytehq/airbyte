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
_STREAM_NAME = "filter_sharing"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestFilterSharingStream(TestCase):
    """
    Tests for the Jira 'filter_sharing' stream.

    This is a substream of filters.
    Endpoint: /rest/api/3/filter/{filter_id}/permission
    Uses SubstreamPartitionRouter with filters as parent
    Has transformation: AddFields for filterId
    """

    @HttpMocker()
    def test_full_refresh_with_parent_filters(self, http_mocker: HttpMocker):
        """
        Test that connector correctly fetches filter sharing permissions from multiple parent filters.

        Per playbook: "All substreams should be tested against at least two parent records"
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock parent filters endpoint
        filter_records = [
            {"id": "10001", "name": "Filter 1", "self": f"https://{_DOMAIN}/rest/api/3/filter/10001"},
            {"id": "10002", "name": "Filter 2", "self": f"https://{_DOMAIN}/rest/api/3/filter/10002"},
        ]
        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(filter_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        # Mock filter sharing permissions for filter 10001
        filter1_permissions = [
            {"id": 1, "type": "user", "user": {"accountId": "user1"}},
            {"id": 2, "type": "group", "group": {"name": "developers"}},
        ]
        http_mocker.get(
            JiraRequestBuilder.filter_sharing_endpoint(_DOMAIN, "10001").build(),
            HttpResponse(body=json.dumps(filter1_permissions), status_code=200),
        )

        # Mock filter sharing permissions for filter 10002
        filter2_permissions = [
            {"id": 3, "type": "project", "project": {"id": "10001"}},
        ]
        http_mocker.get(
            JiraRequestBuilder.filter_sharing_endpoint(_DOMAIN, "10002").build(),
            HttpResponse(body=json.dumps(filter2_permissions), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        # Verify transformation: filterId should be added
        filter_ids = [r.record.data.get("filterId") for r in output.records]
        assert "10001" in filter_ids
        assert "10002" in filter_ids

    @HttpMocker()
    def test_empty_parent_filters(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty parent filters gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_any_query_params().build(),
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
    def test_filter_without_sharing_permissions(self, http_mocker: HttpMocker):
        """
        Test that connector handles filters without sharing permissions.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock parent filters endpoint
        filter_records = [
            {"id": "10001", "name": "Filter 1", "self": f"https://{_DOMAIN}/rest/api/3/filter/10001"},
        ]
        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(filter_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock empty permissions for filter 10001
        http_mocker.get(
            JiraRequestBuilder.filter_sharing_endpoint(_DOMAIN, "10001").build(),
            HttpResponse(body=json.dumps([]), status_code=200),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0

    @HttpMocker()
    def test_error_400_ignored(self, http_mocker: HttpMocker):
        """
        Test that connector ignores 400 errors per the error handler.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Mock parent filters endpoint
        filter_records = [
            {"id": "10001", "name": "Filter 1", "self": f"https://{_DOMAIN}/rest/api/3/filter/10001"},
        ]
        http_mocker.get(
            JiraRequestBuilder.filters_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(filter_records)
            .with_pagination(start_at=0, max_results=50, total=1, is_last=True)
            .build(),
        )

        # Mock 400 error for filter sharing
        http_mocker.get(
            JiraRequestBuilder.filter_sharing_endpoint(_DOMAIN, "10001").build(),
            HttpResponse(
                body=json.dumps({"errorMessages": ["Bad request"]}),
                status_code=400,
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog, expecting_exception=False)

        assert len(output.records) == 0
        assert not any(log.log.level == "ERROR" for log in output.logs)
