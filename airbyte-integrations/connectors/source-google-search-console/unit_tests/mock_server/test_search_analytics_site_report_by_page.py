# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the search_analytics_site_report_by_page stream.

The search_analytics_site_report_by_page stream is an incremental stream that:
- Uses POST requests to /webmasters/v3/sites/{site_url}/searchAnalytics/query
- Partitions by site_urls from config AND search_types (web, news, image, video, googleNews)
- Uses dimensions: ["date", "country", "device"]
- Uses aggregationType: byPage
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
from mock_server.response_builder import create_oauth_response

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


_STREAM_NAME = "search_analytics_site_report_by_page"
_SEARCH_TYPES = ["web", "news", "image", "video", "googleNews"]


def _build_search_analytics_response(rows: list) -> dict:
    """Build a response body for the searchAnalytics endpoint."""
    return {"rows": rows}


def _build_search_analytics_row(
    date: str,
    country: str,
    device: str,
    clicks: int = 100,
    impressions: int = 1000,
    ctr: float = 0.1,
    position: float = 5.0,
) -> dict:
    """Build a single search analytics row with date, country, and device dimensions."""
    return {
        "keys": [date, country, device],
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
class TestSearchAnalyticsSiteReportByPageStream(TestCase):
    """Tests for the search_analytics_site_report_by_page stream.

    This stream partitions by site_urls AND search_types (5 types).
    Uses dimensions: ["date", "country", "device"] for the API request.
    Uses aggregationType: byPage.
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
                            _build_search_analytics_row("2024-01-01", "usa", "DESKTOP", clicks=100, impressions=1000),
                            _build_search_analytics_row("2024-01-01", "gbr", "MOBILE", clicks=50, impressions=500),
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
            ], f"Expected dimensions ['date', 'country', 'device'], got {body.get('dimensions')}"

        # Verify aggregationType is byPage
        for body in captured_bodies:
            assert body.get("aggregationType") == "byPage", f"Expected aggregationType 'byPage', got {body.get('aggregationType')}"

        # Should have 2 records (from web search type)
        assert len(records) == 2

        # Verify transformations added site_url and search_type
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert record.record.data["search_type"] == "web"
            assert "date" in record.record.data
            assert "country" in record.record.data
            assert "device" in record.record.data

    @HttpMocker()
    def test_error_handler_ignore_permission_error(self, http_mocker: HttpMocker) -> None:
        """Test IGNORE error handler for 403 permission errors.

        The error handler should ignore 403 errors with "User does not have sufficient permission" message.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        def permission_error_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            """Return 403 permission error for all requests."""
            context.status_code = 403
            return json.dumps({"error": {"message": "User does not have sufficient permission"}})

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=permission_error_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Should have 0 records due to permission error being ignored
        assert len(records) == 0

        # Verify no ERROR logs (permission error should be ignored gracefully)
        error_logs = [log for log in output.logs if hasattr(log, "log") and log.log.level == "ERROR"]
        assert len(error_logs) == 0, "Expected no ERROR logs for ignored permission errors"

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
                            _build_search_analytics_row("2024-01-01", "usa", "DESKTOP", clicks=100, impressions=1000),
                            _build_search_analytics_row("2024-01-02", "gbr", "MOBILE", clicks=150, impressions=1500),
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
                            _build_search_analytics_row("2024-01-03", "usa", "DESKTOP", clicks=200, impressions=2000),
                            _build_search_analytics_row("2024-01-04", "deu", "TABLET", clicks=250, impressions=2500),
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
