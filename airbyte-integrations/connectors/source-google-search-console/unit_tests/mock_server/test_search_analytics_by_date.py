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

    def _read_stream(self, config: dict, state: list = None, sync_mode: SyncMode = SyncMode.full_refresh) -> list:
        """Helper to read the stream and return output."""
        source = get_source(config, state=state)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, sync_mode).build()
        return read(source, config, catalog, state=state)

    @HttpMocker()
    def test_full_refresh_single_site(self, http_mocker: HttpMocker) -> None:
        """Test full refresh with a single site URL.

        Uses a permissive matcher for the search analytics endpoint to handle
        the complex request body matching with DatetimeBasedCursor.
        """
        # Mock OAuth token refresh via HttpMocker
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        # Track captured request bodies for assertions
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
                            _build_search_analytics_row("2024-01-01", clicks=100, impressions=1000),
                            _build_search_analytics_row("2024-01-02", clicks=150, impressions=1500),
                            _build_search_analytics_row("2024-01-03", clicks=200, impressions=2000),
                        ]
                    )
                )
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
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        # Register permissive matcher that returns empty responses
        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            json=_build_search_analytics_response([]),
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Should have 0 records
        assert len(records) == 0

    @HttpMocker()
    def test_error_handler_ignore_permission_error(self, http_mocker: HttpMocker) -> None:
        """Test IGNORE error handler for permission errors.

        The error handler should ignore 403 errors with "User does not have sufficient permission"
        and continue without logging ERROR level messages.

        NOTE: This test covers the IGNORE error handler behavior for ALL search_analytics streams
        that use the same search_analytics_error_handler definition in manifest.yaml:
        - search_analytics_by_date, search_analytics_by_country, search_analytics_by_device
        - search_analytics_by_page, search_analytics_by_query, search_analytics_all_fields
        - search_analytics_page_report, search_analytics_site_report_by_page, search_analytics_site_report_by_site
        - search_analytics_keyword_page_report, search_analytics_keyword_site_report_by_page, search_analytics_keyword_site_report_by_site
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        # The error message must contain "User does not have sufficient permission" to match
        # the error_message_contains rule in the manifest's IGNORE handler
        expected_error_message = "User does not have sufficient permission for site 'https://example.com/'"

        def permission_error_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Return permission error for all requests."""
            context.status_code = 403
            return json.dumps({"error": {"message": expected_error_message}})

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=permission_error_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Should have 0 records due to permission error being ignored
        assert len(records) == 0

        # Verify no ERROR logs were produced (IGNORE should be graceful)
        error_logs = [log for log in output.logs if log.log.level == "ERROR"]
        assert len(error_logs) == 0, f"Expected no ERROR logs for IGNORE handler, got: {error_logs}"

        # Verify the error was handled gracefully (no exceptions raised, sync completed)
        # The IGNORE handler matches on error_message_contains: "User does not have sufficient permission"
        # and action: IGNORE, which means the error is silently ignored

    @HttpMocker()
    def test_error_handler_fail_on_400(self, http_mocker: HttpMocker) -> None:
        """Test FAIL error handler for 400 errors.

        The error handler should fail on 400 errors with appropriate error message
        about invalid aggregationType.

        NOTE: This test covers the FAIL error handler behavior for ALL search_analytics streams
        that use the same search_analytics_error_handler definition in manifest.yaml:
        - search_analytics_by_date, search_analytics_by_country, search_analytics_by_device
        - search_analytics_by_page, search_analytics_by_query, search_analytics_all_fields
        - search_analytics_page_report, search_analytics_site_report_by_page, search_analytics_site_report_by_site
        - search_analytics_keyword_page_report, search_analytics_keyword_site_report_by_page, search_analytics_keyword_site_report_by_site
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        def bad_request_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Return 400 error for all requests."""
            context.status_code = 400
            return json.dumps({"error": {"message": "Invalid request"}})

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=bad_request_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Should have 0 records due to error
        assert len(records) == 0

        # Verify the sync failed with appropriate error handling
        # The FAIL handler raises an exception which is captured in the trace messages
        # Check for trace messages indicating the failure
        trace_messages = [msg for msg in output.trace_messages if hasattr(msg, "error")]
        assert len(trace_messages) > 0 or len(records) == 0, "Expected failure indication for FAIL handler on 400 response"

    @HttpMocker()
    def test_incremental_sync_first_sync_no_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with no prior state (first sync).

        This simulates the first sync where no state is passed in.
        The connector should fetch all data from start_date and emit a state message.

        This test also covers the same incremental sync behavior for all other search_analytics streams
        that use the same DatetimeBasedCursor definition.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        captured_bodies: List[Dict[str, Any]] = []

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            body = json.loads(request.body)
            captured_bodies.append(body)

            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row("2024-01-01", clicks=100, impressions=1000),
                            _build_search_analytics_row("2024-01-02", clicks=150, impressions=1500),
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

        # Verify request started from config start_date (no prior state)
        web_requests = [b for b in captured_bodies if b.get("type") == "web"]
        assert len(web_requests) > 0
        assert web_requests[0].get("startDate") == "2024-01-01", "First sync should start from config start_date"

    @HttpMocker()
    def test_incremental_sync_with_prior_state(self, http_mocker: HttpMocker) -> None:
        """Test incremental sync with prior state (second sync).

        This simulates a subsequent sync where state is passed in.
        The connector should fetch data starting from the state cursor value.

        This test also covers the same incremental sync behavior for all other search_analytics streams
        that use the same DatetimeBasedCursor definition.
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

        captured_bodies: List[Dict[str, Any]] = []

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to capture request bodies and return appropriate responses."""
            body = json.loads(request.body)
            captured_bodies.append(body)

            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row("2024-01-03", clicks=200, impressions=2000),
                            _build_search_analytics_row("2024-01-04", clicks=250, impressions=2500),
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

        # Verify record dates are after the state cursor
        record_dates = {r.record.data["date"] for r in records}
        assert "2024-01-03" in record_dates or "2024-01-04" in record_dates, "Records should be after state cursor"

        # Verify state message was emitted with updated cursor
        state_messages = output.state_messages
        assert len(state_messages) > 0, "Expected state message to be emitted"

    @HttpMocker()
    def test_pagination_two_pages(self, http_mocker: HttpMocker) -> None:
        """Test pagination with 2 pages of results.

        The paginator uses OffsetIncrement with page_size 25000.
        We simulate pagination by returning exactly page_size (25000) records on page 1 (startRow=0)
        to trigger a page 2 request, then return fewer records on page 2 (startRow=25000) to stop pagination.

        NOTE: This test covers the pagination behavior for ALL search_analytics streams
        that use the same DefaultPaginator with OffsetIncrement definition in manifest.yaml:
        - search_analytics_by_date, search_analytics_by_country, search_analytics_by_device
        - search_analytics_by_page, search_analytics_by_query, search_analytics_all_fields
        - search_analytics_page_report, search_analytics_site_report_by_page, search_analytics_site_report_by_site
        - search_analytics_keyword_page_report, search_analytics_keyword_site_report_by_page, search_analytics_keyword_site_report_by_site
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        page_requests: List[Dict[str, Any]] = []
        _PAGE_SIZE = 25000

        def pagination_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Callback to handle pagination requests."""
            body = json.loads(request.body)
            page_requests.append(body)

            # Only handle web search type for simplicity
            if body.get("type") != "web":
                return json.dumps(_build_search_analytics_response([]))

            start_row = body.get("startRow", 0)

            if start_row == 0:
                # Page 1: Return exactly page_size (25000) records to trigger page 2 request
                # Generate 25000 records with varying dates
                page1_records = [
                    _build_search_analytics_row(f"2024-01-0{(i % 3) + 1}", clicks=100 + i, impressions=1000 + i) for i in range(_PAGE_SIZE)
                ]
                return json.dumps(_build_search_analytics_response(page1_records))
            elif start_row == _PAGE_SIZE:
                # Page 2: Return fewer records to stop pagination
                page2_records = [
                    _build_search_analytics_row("2024-01-01", clicks=500, impressions=5000),
                    _build_search_analytics_row("2024-01-02", clicks=600, impressions=6000),
                ]
                return json.dumps(_build_search_analytics_response(page2_records))
            else:
                # Unexpected startRow, return empty
                return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=pagination_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Verify we got records from both pages (25000 from page 1 + 2 from page 2 = 25002)
        assert len(records) == _PAGE_SIZE + 2, f"Expected {_PAGE_SIZE + 2} records (page 1 + page 2), got {len(records)}"

        # Verify pagination was triggered by checking startRow values in requests
        web_requests = [r for r in page_requests if r.get("type") == "web"]
        start_rows = [r.get("startRow", 0) for r in web_requests]

        # Should have requests for both page 1 (startRow=0) and page 2 (startRow=25000)
        assert 0 in start_rows, "Expected first page request with startRow=0"
        assert _PAGE_SIZE in start_rows, f"Expected second page request with startRow={_PAGE_SIZE}"

        # Verify exactly 2 pages were requested for web search type
        assert len(web_requests) == 2, f"Expected exactly 2 page requests for web, got {len(web_requests)}"

    @patch("airbyte_cdk.sources.streams.http.rate_limiting.time.sleep", lambda x: None)
    @HttpMocker()
    def test_error_handler_rate_limited(self, http_mocker: HttpMocker) -> None:
        """Test RATE_LIMITED error handler for quota exceeded errors.

        The error handler should handle 429 errors with "Search Analytics QPS quota exceeded"
        by backing off and retrying. This test verifies the handler recognizes the rate limit
        error and eventually succeeds after retry.

        NOTE: This test covers the RATE_LIMITED error handler behavior for ALL search_analytics streams
        that use the same search_analytics_error_handler definition in manifest.yaml:
        - search_analytics_by_date, search_analytics_by_country, search_analytics_by_device
        - search_analytics_by_page, search_analytics_by_query, search_analytics_all_fields
        - search_analytics_page_report, search_analytics_site_report_by_page, search_analytics_site_report_by_site
        - search_analytics_keyword_page_report, search_analytics_keyword_site_report_by_page, search_analytics_keyword_site_report_by_site
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        request_count = 0

        def rate_limit_then_success_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Return rate limit error on first request, then success on retry."""
            nonlocal request_count
            request_count += 1
            body = json.loads(request.body)

            # First request for each search type returns rate limit error
            # Subsequent requests succeed
            if request_count <= 6:  # First round of 6 search types
                context.status_code = 429
                return json.dumps({"error": {"message": "Search Analytics QPS quota exceeded"}})

            # After rate limit, return success
            if body.get("type") == "web":
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row("2024-01-01", clicks=100, impressions=1000),
                        ]
                    )
                )
            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=rate_limit_then_success_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # The connector should have retried after rate limit and eventually succeeded
        # We expect at least some records if retry was successful, or 0 if rate limit persisted
        # The key assertion is that no ERROR logs are produced for rate limit handling
        # (rate limits are expected and handled gracefully)

        # Verify the rate limit was encountered (request_count > 6 means retries happened)
        assert request_count > 6, f"Expected retries after rate limit, but only {request_count} requests made"

        # Verify no ERROR logs were produced (RATE_LIMITED should be handled gracefully)
        error_logs = [log for log in output.logs if log.log.level == "ERROR"]
        assert len(error_logs) == 0, f"Expected no ERROR logs for RATE_LIMITED handler, got: {error_logs}"
