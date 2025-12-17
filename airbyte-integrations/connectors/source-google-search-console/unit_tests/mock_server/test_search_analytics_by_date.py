# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the search_analytics_by_date stream.

The search_analytics_by_date stream is an incremental stream that:
- Uses POST requests to /webmasters/v3/sites/{site_url}/searchAnalytics/query
- Partitions by site_urls from config AND search_types (web, news, image, video, discover, googleNews)
- Uses DatetimeBasedCursor with P3D step for incremental sync
- Has pagination via startRow/rowLimit in request body
- Has error handlers for RATE_LIMITED, IGNORE (permission errors), FAIL (400 errors)
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


_STREAM_NAME = "search_analytics_by_date"
# search_analytics_by_date uses these 6 search types (from manifest)
_SEARCH_TYPES = ["web", "news", "image", "video", "discover", "googleNews"]


def _build_search_analytics_response(rows: list) -> dict:
    """Build a response body for the searchAnalytics endpoint."""
    return {"rows": rows}


def _build_search_analytics_row(date: str, clicks: int = 100, impressions: int = 1000, ctr: float = 0.1, position: float = 5.0) -> dict:
    """Build a single search analytics row."""
    return {
        "keys": [date],
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
class TestSearchAnalyticsByDateStream(TestCase):
    """Tests for the search_analytics_by_date stream.
    
    This stream partitions by site_urls AND search_types (6 types: web, news, image, video, discover, googleNews).
    We test with a single site URL and use a permissive matcher to handle the complex request body matching.
    """

    def _read_stream(self, config: dict) -> list:
        """Helper to read the stream and return output."""
        source = get_source(config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        return read(source, config, catalog)

    @HttpMocker()
    def test_full_refresh_single_site(self, http_mocker: HttpMocker) -> None:
        """Test full refresh with a single site URL.
        
        Uses a permissive matcher for the search analytics endpoint to handle
        the complex request body matching with DatetimeBasedCursor.
        """
        # Mock OAuth token refresh via HttpMocker
        http_mocker.post(_oauth_request(), _build_oauth_response())
        
        config = (
            ConfigBuilder()
            .with_site_urls(["https://example.com/"])
            .with_start_date("2024-01-01")
            .with_end_date("2024-01-03")
            .build()
        )
        
        # Track captured request bodies for assertions
        captured_bodies: List[Dict[str, Any]] = []
        
        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            body = json.loads(request.body)
            captured_bodies.append(body)
            
            # Return data only for "web" search type
            if body.get("type") == "web":
                return json.dumps(_build_search_analytics_response([
                    _build_search_analytics_row("2024-01-01", clicks=100, impressions=1000),
                    _build_search_analytics_row("2024-01-02", clicks=150, impressions=1500),
                    _build_search_analytics_row("2024-01-03", clicks=200, impressions=2000),
                ]))
            return json.dumps(_build_search_analytics_response([]))
        
        # Register permissive matcher for search analytics endpoint via underlying requests_mock
        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )
        
        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]
        
        # Verify we captured requests for all 6 search types
        captured_search_types = {body.get("type") for body in captured_bodies}
        assert captured_search_types == set(_SEARCH_TYPES), f"Expected {_SEARCH_TYPES}, got {captured_search_types}"
        
        # Should have 3 records (from web search type)
        assert len(records) == 3
        
        # Verify record fields
        record_dates = {r.record.data["date"] for r in records}
        assert record_dates == {"2024-01-01", "2024-01-02", "2024-01-03"}
        
        # Verify transformations added site_url and search_type
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert record.record.data["search_type"] == "web"

    @HttpMocker()
    def test_full_refresh_empty_response(self, http_mocker: HttpMocker) -> None:
        """Test full refresh when API returns no data for any search type."""
        # Mock OAuth token refresh via HttpMocker
        http_mocker.post(_oauth_request(), _build_oauth_response())
        
        config = (
            ConfigBuilder()
            .with_site_urls(["https://example.com/"])
            .with_start_date("2024-01-01")
            .with_end_date("2024-01-03")
            .build()
        )
        
        # Register permissive matcher that returns empty responses
        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            json=_build_search_analytics_response([]),
        )
        
        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]
        
        # Should have 0 records
        assert len(records) == 0
