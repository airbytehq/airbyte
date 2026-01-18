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
_STREAM_NAME = "screen_schemes"
_DOMAIN = "airbyteio.atlassian.net"


@freezegun.freeze_time(_NOW.isoformat())
class TestScreenSchemesStream(TestCase):
    """
    Tests for the Jira 'screen_schemes' stream.

    This is a full refresh stream with pagination.
    Endpoint: /rest/api/3/screenscheme
    Extract field: values
    Primary key: id
    """

    @HttpMocker()
    def test_full_refresh_single_page(self, http_mocker: HttpMocker):
        """
        Test full refresh sync with a single page of results.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        screen_scheme_records = [
            {
                "id": 10000,
                "name": "Default Screen Scheme",
                "description": "Default screen scheme for the project.",
                "screens": {"default": 10000, "create": 10001, "edit": 10002, "view": 10003},
            },
            {
                "id": 10001,
                "name": "Bug Screen Scheme",
                "description": "Screen scheme for bug issues.",
                "screens": {"default": 10004},
            },
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_schemes_endpoint(_DOMAIN).with_any_query_params().build(),
            JiraPaginatedResponseBuilder("values")
            .with_records(screen_scheme_records)
            .with_pagination(start_at=0, max_results=50, total=2, is_last=True)
            .build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2

        scheme_ids = [r.record.data["id"] for r in output.records]
        assert 10000 in scheme_ids
        assert 10001 in scheme_ids

    @HttpMocker()
    def test_pagination_multiple_pages(self, http_mocker: HttpMocker):
        """
        Test that pagination works correctly with multiple pages.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        # Page 1
        page1_schemes = [
            {"id": 10000, "name": "Scheme 1"},
            {"id": 10001, "name": "Scheme 2"},
        ]

        # Page 2
        page2_schemes = [
            {"id": 10002, "name": "Scheme 3"},
        ]

        http_mocker.get(
            JiraRequestBuilder.screen_schemes_endpoint(_DOMAIN).with_any_query_params().build(),
            [
                JiraPaginatedResponseBuilder("values")
                .with_records(page1_schemes)
                .with_pagination(start_at=0, max_results=2, total=3, is_last=False)
                .build(),
                JiraPaginatedResponseBuilder("values")
                .with_records(page2_schemes)
                .with_pagination(start_at=2, max_results=2, total=3, is_last=True)
                .build(),
            ],
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        scheme_ids = [r.record.data["id"] for r in output.records]
        assert 10000 in scheme_ids
        assert 10001 in scheme_ids
        assert 10002 in scheme_ids

    @HttpMocker()
    def test_empty_results(self, http_mocker: HttpMocker):
        """
        Test that connector handles empty results gracefully.
        """
        config = ConfigBuilder().with_domain(_DOMAIN).build()

        http_mocker.get(
            JiraRequestBuilder.screen_schemes_endpoint(_DOMAIN).with_any_query_params().build(),
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
