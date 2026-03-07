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
_STREAM_NAME = "groups"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestGroupsStream(TestCase):
    """
    Tests for the Jira 'groups' stream.

    This is a full refresh stream.
    Endpoint: /rest/api/3/group/bulk
    Extract field: values
    Primary key: groupId
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        group_records = [
            {
                "name": "jira-administrators",
                "groupId": "group-1",
            },
            {
                "name": "jira-software-users",
                "groupId": "group-2",
            },
            {
                "name": "site-admins",
                "groupId": "group-3",
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.groups_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(group_records)
            .with_pagination(start_at=0, max_results=50, total=3, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3

        group_ids = [r.record.data["groupId"] for r in output.records]
        assert "group-1" in group_ids
        assert "group-2" in group_ids
        assert "group-3" in group_ids

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly with multiple pages.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Page 1
        page1_groups = [
            {"name": "group-a", "groupId": "group-1"},
            {"name": "group-b", "groupId": "group-2"},
        ]

        # Page 2
        page2_groups = [
            {"name": "group-c", "groupId": "group-3"},
        ]

        http_mocker.get(
            JiraRequestBuilder.groups_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_groups)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_groups)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        group_ids = [r.record.data["groupId"] for r in output.records]
        assert "group-1" in group_ids
        assert "group-2" in group_ids
        assert "group-3" in group_ids

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.groups_endpoint(_DOMAIN).with_any_query_params().build(),
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
