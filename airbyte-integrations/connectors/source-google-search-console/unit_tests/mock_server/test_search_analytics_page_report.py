# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the search_analytics_page_report stream.

The search_analytics_page_report stream is an incremental stream that:
- Uses POST requests to /webmasters/v3/sites/{site_url}/searchAnalytics/query
- Partitions by site_urls from config AND search_types (web, news, image, video, googleNews)
- Uses dimensions: ["date", "country", "device", "page"]
- Uses DatetimeBasedCursor with P3D step for incremental sync
- Has pagination via startRow/rowLimit in request body
"""

import json
import re
from typing import Any, Dict, List
from unittest import TestCase
from unittest.mock import patch

import requests_mock as rm
from freezegun import freeze_time
from mock_server.config import ConfigBuilder
from mock_server.response_builder import create_oauth_response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_STREAM_NAME = "search_analytics_page_report"
_SEARCH_TYPES = ["web", "news", "image", "video", "googleNews"]


def _build_search_analytics_response(rows: list) -> dict:
    """Build a response body for the searchAnalytics endpoint."""
    return {"rows": rows}


def _build_search_analytics_row(
    date: str,
    country: str,
    device: str,
    page: str,
    clicks: int = 100,
    impressions: int = 1000,
    ctr: float = 0.1,
    position: float = 5.0,
) -> dict:
    """Build a single search analytics row with date, country, device, and page dimensions."""
    return {
        "keys": [date, country, device, page],
        "clicks": clicks,
        "impressions": impressions,
        "ctr": ctr,
        "position": position,
    }


def _oauth_request() -> HttpRequest:
    """Build a mock OAuth token request."""
    return HttpRequest(
        url="https://oauth2.googleapis.com/token",
        body="grant_type=refresh_token&client_id=test_client_id&client_secret=test_client_secret&refresh_token=test_refresh_token",
    )


@freeze_time("2024-01-04T00:00:00Z")
class TestSearchAnalyticsPageReportStream(TestCase):
    """Tests for the search_analytics_page_report stream.

    This stream partitions by site_urls AND search_types (5 types).
    Uses dimensions: ["date", "country", "device", "page"] for the API request.
    """

    def _read_stream(self, config: dict, state: list = None, sync_mode: SyncMode = SyncMode.full_refresh) -> list:
        """Helper to read the stream and return output."""
        source = get_source(config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
        return read(source, config, catalog, state=state)

    @HttpMocker()
    def test_full_refresh_single_site(self, http_mocker: HttpMocker) -> None:
        """Test full refresh with a single site URL."""
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        captured_bodies: List[Dict[str, Any]] = []

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            body = json.loads(request.body)
            captured_bodies.append(body)

            # Return data only for "web" search type
            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row(
                                "2024-01-01", "usa", "DESKTOP", "https://example.com/page1", clicks=100, impressions=1000
                            ),
                            _build_search_analytics_row(
                                "2024-01-01", "gbr", "MOBILE", "https://example.com/page2", clicks=50, impressions=500
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

        # Verify we captured requests for all 5 search types
        captured_search_types = {body.get("type") for body in captured_bodies}
        assert captured_search_types == set(_SEARCH_TYPES), f"Expected {_SEARCH_TYPES}, got {captured_search_types}"

        # Verify dimensions in request body
        for body in captured_bodies:
            assert body.get("dimensions") == [
                "date",
                "country",
                "device",
                "page",
            ], f"Expected dimensions ['date', 'country', 'device', 'page'], got {body.get('dimensions')}"

        # Should have 2 records (from web search type)
        assert len(records) == 2

        # Verify record fields include page
        record_pages = {r.record.data["page"] for r in records}
        assert "https://example.com/page1" in record_pages
        assert "https://example.com/page2" in record_pages

        # Verify transformations added site_url and search_type
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert record.record.data["search_type"] == "web"
            assert "date" in record.record.data
            assert "country" in record.record.data
            assert "device" in record.record.data
            assert "page" in record.record.data

    @patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep", lambda x: None)
    @HttpMocker()
    def test_error_handler_rate_limited(self, http_mocker: HttpMocker) -> None:
        """Test RATE_LIMITED error handler for 429 errors.

        The error handler should retry on 429 errors with "Search Analytics QPS quota exceeded" message.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        request_count = 0

        def rate_limited_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Return 429 error first, then success on retry."""
            nonlocal request_count
            request_count += 1

            # Return rate limit error for first few requests, then success
            if request_count <= 5:
                context.status_code = 429
                return json.dumps({"error": {"message": "Search Analytics QPS quota exceeded"}})

            body = json.loads(request.body)
            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row(
                                "2024-01-01", "usa", "DESKTOP", "https://example.com/page1", clicks=100, impressions=1000
                            )
                        ]
                    )
                )
            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=rate_limited_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Verify retry behavior occurred - request_count > 5 means retries happened after rate limits
        assert request_count > 5, f"Expected retries after rate limit, but only {request_count} requests made"

        # Verify no ERROR logs (rate limiting should be handled gracefully with retries)
        error_logs = [log for log in output.logs if hasattr(log, "log") and log.log.level == "ERROR"]
        assert len(error_logs) == 0, "Expected no ERROR logs for rate limited requests - RATE_LIMITED handler should retry gracefully"

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with no prior state (first sync).

        This simulates the first sync where no state is passed in.
        The connector should fetch all data from start_date and emit a state message.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)
            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row(
                                "2024-01-01", "usa", "DESKTOP", "https://example.com/page1", clicks=100, impressions=1000
                            ),
                            _build_search_analytics_row(
                                "2024-01-02", "gbr", "MOBILE", "https://example.com/page2", clicks=150, impressions=1500
                            ),
                        ]
                    )
                )
            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )

        output = self._read_stream(config, state=None, sync_mode=SyncMode.incremental)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Should have 2 records from web search type
        assert len(records) == 2

        # Verify state message was emitted
        state_messages = output.state_messages
        assert len(state_messages) > 0, "Expected state message to be emitted after first sync"

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with prior state (second sync).

        This simulates a subsequent sync where state is passed in.
        The connector should fetch data starting from the state cursor value.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-05").build()

        # Build state with prior cursor value
        prior_state = (
            StateBuilder()
            .with_stream_state(
                _STREAM_NAME,
                {
                    "states": [
                        {
                            "partition": {"site_url": "https://example.com/", "search_type": "web"},
                            "cursor": {"date": "2024-01-02"},
                        }
                    ]
                },
            )
            .build()
        )

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)
            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row(
                                "2024-01-03", "usa", "DESKTOP", "https://example.com/page3", clicks=200, impressions=2000
                            ),
                            _build_search_analytics_row(
                                "2024-01-04", "deu", "TABLET", "https://example.com/page4", clicks=250, impressions=2500
                            ),
                        ]
                    )
                )
            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )

        output = self._read_stream(config, state=prior_state, sync_mode=SyncMode.incremental)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Should have 2 records from web search type (after state cursor)
        assert len(records) == 2

        # Verify state message was emitted with updated cursor
        state_messages = output.state_messages
        assert len(state_messages) > 0, "Expected state message to be emitted"
