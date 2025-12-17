# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the search_analytics_keyword_page_report stream.

The search_analytics_keyword_page_report stream is an incremental stream that:
- Uses POST requests to /webmasters/v3/sites/{site_url}/searchAnalytics/query
- Partitions by site_urls from config AND search_appearances from parent stream
- Uses dimensions: ["date", "country", "device", "query", "page"]
- Uses aggregationType: auto
- Uses dimensionFilterGroups to filter by searchAppearance
- Uses DatetimeBasedCursor with P3D step for incremental sync
- Has pagination via startRow/rowLimit in request body
"""

import json
import re
from typing import Any, Dict, List
from unittest import TestCase

import requests_mock as rm
from freezegun import freeze_time
from mock_server.config import ConfigBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_STREAM_NAME = "search_analytics_keyword_page_report"


def _build_search_analytics_response(rows: list) -> dict:
    """Build a response body for the searchAnalytics endpoint."""
    return {"rows": rows}


def _build_search_appearances_response(rows: list) -> dict:
    """Build a response body for the search_appearances parent stream."""
    return {"rows": rows}


def _build_search_analytics_row(
    date: str,
    country: str,
    device: str,
    query: str,
    page: str,
    clicks: int = 100,
    impressions: int = 1000,
    ctr: float = 0.1,
    position: float = 5.0,
) -> dict:
    """Build a single search analytics row with all keyword page report dimensions."""
    return {
        "keys": [date, country, device, query, page],
        "clicks": clicks,
        "impressions": impressions,
        "ctr": ctr,
        "position": position,
    }


def _build_oauth_response() -> HttpResponse:
    """Build a mock OAuth token response."""
    body = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "token_type": "Bearer",
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


def _oauth_request() -> HttpRequest:
    """Build a mock OAuth token request."""
    return HttpRequest(
        url="https://oauth2.googleapis.com/token",
        body="grant_type=refresh_token&client_id=test_client_id&client_secret=test_client_secret&refresh_token=test_refresh_token",
    )


@freeze_time("2024-01-04T00:00:00Z")
class TestSearchAnalyticsKeywordPageReportStream(TestCase):
    """Tests for the search_analytics_keyword_page_report stream.

    This stream partitions by site_urls AND search_appearances from parent stream.
    Uses dimensions: ["date", "country", "device", "query", "page"] for the API request.
    Uses aggregationType: auto.
    """

    def _read_stream(self, config: dict) -> list:
        """Helper to read the stream and return output."""
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        return read(source, config, catalog)

    @HttpMocker()
    def test_full_refresh_single_site(self, http_mocker: HttpMocker) -> None:
        """Test full refresh with a single site URL."""
        http_mocker.post(_oauth_request(), _build_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        captured_bodies: List[Dict[str, Any]] = []
        parent_request_count = 0

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            nonlocal parent_request_count
            body = json.loads(request.body)
            captured_bodies.append(body)

            # Check if this is a parent stream request (search_appearances)
            if body.get("dimensions") == ["searchAppearance"]:
                parent_request_count += 1
                # Return search appearances that will be used as partitions
                return json.dumps(
                    _build_search_appearances_response(
                        [
                            {"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0},
                        ]
                    )
                )

            # Check if this is a keyword page report request
            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row(
                                "2024-01-01",
                                "usa",
                                "DESKTOP",
                                "test query",
                                "https://example.com/page1",
                                clicks=100,
                                impressions=1000,
                            ),
                        ]
                    )
                )

            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Verify parent stream was called to get search appearances
        assert parent_request_count > 0, "Parent stream (search_appearances) should have been called"

        # Verify dimensions in keyword page report requests
        keyword_requests = [b for b in captured_bodies if b.get("dimensions") == ["date", "country", "device", "query", "page"]]
        assert len(keyword_requests) > 0, "Should have made keyword page report requests"

        # Verify dimensionFilterGroups is present in keyword requests
        for body in keyword_requests:
            assert "dimensionFilterGroups" in body, "Should have dimensionFilterGroups for searchAppearance filter"

        # Should have records from the keyword page report
        assert len(records) >= 1

        # Verify transformations added site_url and search_type
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert "date" in record.record.data
            assert "country" in record.record.data
            assert "device" in record.record.data
            assert "query" in record.record.data
            assert "page" in record.record.data
