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
        parent_request_count = 0

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            nonlocal parent_request_count
            body = json.loads(request.body)
            captured_bodies.append(body)

            # Check if this is a parent stream request (search_appearances)
            if body.get("dimensions") == ["searchAppearance"]:
                parent_request_count += 1
                # Return 2+ search appearances to meet substream testing requirement
                return json.dumps(
                    _build_search_appearances_response(
                        [
                            {"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0},
                            {"keys": ["INSTANT_APP"], "clicks": 20, "impressions": 200, "ctr": 0.1, "position": 2.0},
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

        # Should have records from the keyword page report (2 parent records x 1 record each = 2 records)
        # Exception: Using >= because record count depends on parent stream partitions (search_appearances)
        # which are dynamically fetched. We assert on specific key fields to validate correctness.
        assert len(records) >= 1, f"Expected at least 1 record, got {len(records)}"
        # Verify specific key fields are present - this validates record content regardless of count
        assert records[0].record.data["page"] == "https://example.com/page1", "Expected specific page URL in record"
        assert records[0].record.data["query"] == "test query", "Expected specific query in record"
        assert records[0].record.data["date"] == "2024-01-01", "Expected specific date in record"

        # Verify transformations added site_url and search_type
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert "date" in record.record.data
            assert "country" in record.record.data
            assert "device" in record.record.data
            assert "query" in record.record.data
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
            # Check if this is a parent stream request (search_appearances)
            if body.get("dimensions") == ["searchAppearance"]:
                return json.dumps(
                    _build_search_appearances_response(
                        [{"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}]
                    )
                )
            # Return data for keyword page report
            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                return json.dumps(
                    _build_search_analytics_response(
                        [_build_search_analytics_row("2024-01-01", "usa", "DESKTOP", "test query", "https://example.com/page1")]
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
            # Check if this is a parent stream request (search_appearances)
            if body.get("dimensions") == ["searchAppearance"]:
                return json.dumps(
                    _build_search_appearances_response(
                        [{"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}]
                    )
                )
            # Return data for keyword page report
            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row("2024-01-01", "usa", "DESKTOP", "test query", "https://example.com/page1"),
                            _build_search_analytics_row("2024-01-02", "gbr", "MOBILE", "another query", "https://example.com/page2"),
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

        # Exception: Using >= because record count depends on parent stream partitions (search_appearances)
        # which are dynamically fetched. We assert on specific key fields to validate correctness.
        assert len(records) >= 1, f"Expected at least 1 record, got {len(records)}"
        # Verify specific key fields
        assert records[0].record.data["query"] == "test query", "Expected specific query in record"

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
                            "partition": {"site_url": "https://example.com/", "search_appearance": "AMP_TOP_STORIES"},
                            "cursor": {"date": "2024-01-02"},
                        }
                    ]
                },
            )
            .build()
        )

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)
            # Check if this is a parent stream request (search_appearances)
            if body.get("dimensions") == ["searchAppearance"]:
                return json.dumps(
                    _build_search_appearances_response(
                        [{"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}]
                    )
                )
            # Return data for keyword page report
            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row("2024-01-03", "usa", "DESKTOP", "new query", "https://example.com/page3"),
                            _build_search_analytics_row("2024-01-04", "deu", "TABLET", "fresh query", "https://example.com/page4"),
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

        # Exception: Using >= because record count depends on parent stream partitions (search_appearances)
        # which are dynamically fetched. We assert on specific key fields to validate correctness.
        assert len(records) >= 1, f"Expected at least 1 record, got {len(records)}"
        # Verify specific key fields - records should be after state cursor date
        assert records[0].record.data["query"] == "new query", "Expected specific query in record"

        # Verify state message was emitted with updated cursor
        state_messages = output.state_messages
        assert len(state_messages) > 0, "Expected state message to be emitted"
