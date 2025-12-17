# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the search_analytics_all_fields stream.

The search_analytics_all_fields stream is an incremental stream that:
- Uses POST requests to /webmasters/v3/sites/{site_url}/searchAnalytics/query
- Partitions by site_urls from config AND search_types (web, news, image, video)
- Uses dimensions: ["date", "country", "device", "page", "query"]
- Uses DatetimeBasedCursor with P3D step for incremental sync
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


_STREAM_NAME = "search_analytics_all_fields"
# Note: search_analytics_all_fields uses only 4 search types
_SEARCH_TYPES = ["web", "news", "image", "video"]


def _build_search_analytics_response(rows: list) -> dict:
    """Build a response body for the searchAnalytics endpoint."""
    return {"rows": rows}


def _build_search_analytics_row(
    date: str,
    country: str,
    device: str,
    page: str,
    query: str,
    clicks: int = 100,
    impressions: int = 1000,
    ctr: float = 0.1,
    position: float = 5.0,
) -> dict:
    """Build a single search analytics row with all dimensions."""
    return {
        "keys": [date, country, device, page, query],
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
class TestSearchAnalyticsAllFieldsStream(TestCase):
    """Tests for the search_analytics_all_fields stream.
    
    This stream partitions by site_urls AND search_types (4 types).
    Uses dimensions: ["date", "country", "device", "page", "query"] for the API request.
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
        
        config = (
            ConfigBuilder()
            .with_site_urls(["https://example.com/"])
            .with_start_date("2024-01-01")
            .with_end_date("2024-01-03")
            .build()
        )
        
        captured_bodies: List[Dict[str, Any]] = []
        
        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            body = json.loads(request.body)
            captured_bodies.append(body)
            
            # Return data only for "web" search type
            if body.get("type") == "web":
                return json.dumps(_build_search_analytics_response([
                    _build_search_analytics_row(
                        "2024-01-01",
                        "usa",
                        "DESKTOP",
                        "https://example.com/page1",
                        "example query",
                        clicks=100,
                        impressions=1000,
                    ),
                    _build_search_analytics_row(
                        "2024-01-01",
                        "gbr",
                        "MOBILE",
                        "https://example.com/page2",
                        "another query",
                        clicks=80,
                        impressions=800,
                    ),
                    _build_search_analytics_row(
                        "2024-01-02",
                        "usa",
                        "DESKTOP",
                        "https://example.com/page1",
                        "example query",
                        clicks=150,
                        impressions=1500,
                    ),
                ]))
            return json.dumps(_build_search_analytics_response([]))
        
        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )
        
        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]
        
        # Verify we captured requests for all 4 search types
        captured_search_types = {body.get("type") for body in captured_bodies}
        assert captured_search_types == set(_SEARCH_TYPES), f"Expected {_SEARCH_TYPES}, got {captured_search_types}"
        
        # Verify dimensions in request body
        expected_dimensions = ["date", "country", "device", "page", "query"]
        for body in captured_bodies:
            assert body.get("dimensions") == expected_dimensions, f"Expected dimensions {expected_dimensions}, got {body.get('dimensions')}"
        
        # Should have 3 records (from web search type)
        assert len(records) == 3
        
        # Verify all fields are present in records
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert record.record.data["search_type"] == "web"
            assert "date" in record.record.data
            assert "country" in record.record.data
            assert "device" in record.record.data
            assert "page" in record.record.data
            assert "query" in record.record.data
            assert "clicks" in record.record.data
            assert "impressions" in record.record.data
