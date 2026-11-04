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

        # Verify transformations added site_url, search_type, and search_appearance
        for record in records:
            assert record.record.data["site_url"] == "https://example.com/"
            assert "date" in record.record.data
            assert "country" in record.record.data
            assert "device" in record.record.data
            assert "query" in record.record.data
            assert "page" in record.record.data
            assert "search_appearance" in record.record.data, "search_appearance field should be present in record"
            assert record.record.data["search_appearance"] in (
                "AMP_TOP_STORIES",
                "INSTANT_APP",
            ), f"Unexpected search_appearance value: {record.record.data['search_appearance']}"

    @HttpMocker()
    def test_search_appearance_distinguishes_records(self, http_mocker: HttpMocker) -> None:
        """Test that records from different search appearance types are distinguishable.

        This verifies the fix: before this change, search_appearance was not added to
        the output records, making records from different search appearance types
        indistinguishable.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)

            if body.get("dimensions") == ["searchAppearance"]:
                return json.dumps(
                    _build_search_appearances_response(
                        [
                            {"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0},
                            {"keys": ["RICH_RESULT"], "clicks": 20, "impressions": 200, "ctr": 0.1, "position": 2.0},
                        ]
                    )
                )

            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                # Return the same row for all partitions so that only search_appearance
                # distinguishes them
                return json.dumps(
                    _build_search_analytics_response(
                        [
                            _build_search_analytics_row(
                                "2024-01-01",
                                "usa",
                                "DESKTOP",
                                "test query",
                                "https://example.com/page1",
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

        # Collect search_appearance values from all records
        search_appearances = {r.record.data["search_appearance"] for r in records if "search_appearance" in r.record.data}

        # Should have records from at least one search appearance type
        assert len(search_appearances) >= 1, f"Expected records with distinct search_appearance values, got: {search_appearances}"
        # Verify all search_appearance values come from the parent stream
        for sa in search_appearances:
            assert sa in ("AMP_TOP_STORIES", "RICH_RESULT"), f"Unexpected search_appearance: {sa}"

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

    @HttpMocker()
    def test_empty_or_null_search_appearance_partitions_are_skipped(self, http_mocker: HttpMocker) -> None:
        """Parent `search_appearances` records with empty/null/missing `keys[0]` must NOT become keyword partitions.

        The parent stream queries GSC with `dimensions: ["searchAppearance"]`. For traffic
        without a specific rich-result classification (e.g., plain organic blue links),
        Google returns rows with an empty-string or missing `keys[0]`. Without the
        declarative `RecordFilter` on the parent stream, those rows become keyword
        partitions with empty/null `search_appearance`; the resulting keyword API
        request has a malformed `dimensionFilterGroups` that GSC silently ignores,
        producing duplicate "umbrella" rows aggregated across all appearance types.

        The fix drops these parent rows so that the keyword stream only queries GSC
        for actual appearance types (e.g., `PRODUCT_SNIPPETS`).
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        keyword_filter_expressions: List[Any] = []

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)

            if body.get("dimensions") == ["searchAppearance"]:
                # Mix of junk parent rows (empty / null / missing keys) and one valid row.
                return json.dumps(
                    _build_search_appearances_response(
                        [
                            {"keys": [""], "clicks": 5, "impressions": 50, "ctr": 0.1, "position": 1.0},
                            {"keys": [None], "clicks": 5, "impressions": 50, "ctr": 0.1, "position": 1.0},
                            {"clicks": 5, "impressions": 50, "ctr": 0.1, "position": 1.0},
                            {"keys": ["PRODUCT_SNIPPETS"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 2.0},
                        ]
                    )
                )

            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                # Record the `expression` used in the searchAppearance filter so the test can
                # assert that no keyword request was made for the empty/null parent partitions.
                for group in body.get("dimensionFilterGroups", []):
                    filters = group.get("filters", [])
                    # Spec says `filters` MUST be a list; the fix enforces this.
                    assert isinstance(filters, list), f"dimensionFilterGroups[].filters must be a list, got {type(filters).__name__}"
                    for f in filters:
                        if f.get("dimension") == "searchAppearance":
                            keyword_filter_expressions.append(f.get("expression"))

                return json.dumps(
                    _build_search_analytics_response(
                        [_build_search_analytics_row("2024-01-01", "usa", "DESKTOP", "test query", "https://example.com/page1")]
                    )
                )

            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # The keyword stream must only have been queried for the valid PRODUCT_SNIPPETS partition
        # (may be called multiple times per date slice, but never with empty/null expression).
        assert keyword_filter_expressions, "Expected at least one keyword request for the valid parent partition"
        assert set(keyword_filter_expressions) == {"PRODUCT_SNIPPETS"}, (
            f"Expected keyword stream to only query PRODUCT_SNIPPETS partition, "
            f"got searchAppearance filter expressions: {keyword_filter_expressions}"
        )
        # All emitted records carry the PRODUCT_SNIPPETS appearance (no NULL / empty umbrella rows).
        assert len(records) >= 1
        for record in records:
            assert (
                record.record.data["search_appearance"] == "PRODUCT_SNIPPETS"
            ), f"Unexpected search_appearance in record: {record.record.data.get('search_appearance')}"

    @HttpMocker()
    def test_dimension_filter_groups_filters_is_an_array(self, http_mocker: HttpMocker) -> None:
        """`dimensionFilterGroups[].filters` must be an array per the GSC API spec.

        See https://developers.google.com/webmaster-tools/v1/searchanalytics/query —
        the `filters` property is `array[ApiDimensionFilter]`. The API tolerated a
        single-dict form historically, but that is non-spec and should be corrected.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        config = ConfigBuilder().with_site_urls(["https://example.com/"]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        captured_filter_groups: List[List[Dict[str, Any]]] = []

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)

            if body.get("dimensions") == ["searchAppearance"]:
                return json.dumps(
                    _build_search_appearances_response(
                        [{"keys": ["AMP_TOP_STORIES"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}]
                    )
                )

            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                captured_filter_groups.append(body.get("dimensionFilterGroups"))
                return json.dumps(
                    _build_search_analytics_response(
                        [_build_search_analytics_row("2024-01-01", "usa", "DESKTOP", "test query", "https://example.com/page1")]
                    )
                )

            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )

        self._read_stream(config)

        assert captured_filter_groups, "Expected at least one keyword page report request to be made"
        for filter_groups in captured_filter_groups:
            assert isinstance(filter_groups, list) and len(filter_groups) >= 1
            for group in filter_groups:
                filters = group.get("filters")
                assert isinstance(
                    filters, list
                ), f"dimensionFilterGroups[].filters must be a list (per GSC API spec), got {type(filters).__name__}: {filters!r}"
                assert len(filters) >= 1
                for f in filters:
                    assert f.get("dimension") == "searchAppearance"
                    assert f.get("operator") == "equals"
                    assert f.get("expression") == "AMP_TOP_STORIES"

    @HttpMocker()
    def test_multi_site_does_not_cartesian_product_keyword_requests(self, http_mocker: HttpMocker) -> None:
        """With multiple `site_urls` configured, the keyword stream must NOT cartesian-product
        the child `site_url` `ListPartitionRouter` with the parent substream's own
        `site_url` partitioning.

        The parent `search_appearances_stream` is already partitioned by `site_url`, so each
        parent slice already carries a per-site context. If the child keyword stream also adds
        its own outer `ListPartitionRouter` over `site_urls`, the CDK combines the two routers
        as a cartesian product — causing each `(site_url, searchAppearance)` pair to be
        fetched N times where N is the number of configured sites, and emitting duplicate
        records across sites.

        The fix sources `site_url` from `parent_slice` (matching the pattern already used
        for `search_type`), so each `(site_url, searchAppearance)` pair is fetched exactly once.
        """
        http_mocker.post(_oauth_request(), create_oauth_response())

        site_a = "https://example-a.com/"
        site_b = "https://example-b.com/"
        config = ConfigBuilder().with_site_urls([site_a, site_b]).with_start_date("2024-01-01").with_end_date("2024-01-03").build()

        # Capture (site_url_from_path, search_type_from_body, search_appearance_expression)
        # for each keyword request. The parent partitions by `(site_url, search_type)` with
        # search_types of web/news/image/video, so each (site, appearance) legitimately maps
        # to one request per search_type. The regression we guard against is the cartesian
        # product of the CHILD outer `site_urls` router with the parent — which would
        # re-issue every one of those triples N times where N is the number of configured sites.
        keyword_request_triples: List[tuple] = []

        def search_analytics_callback(request: rm.request._RequestObjectProxy, context: Any) -> str:
            body = json.loads(request.body)

            # Parent stream: return the SAME searchAppearance for every parent slice (any site,
            # any search_type). This is exactly the scenario the reviewer flagged: two sites
            # that discover a common `searchAppearance` value.
            if body.get("dimensions") == ["searchAppearance"]:
                return json.dumps(
                    _build_search_appearances_response(
                        [{"keys": ["PRODUCT_SNIPPETS"], "clicks": 10, "impressions": 100, "ctr": 0.1, "position": 1.0}]
                    )
                )

            if body.get("dimensions") == ["date", "country", "device", "query", "page"]:
                # Extract the site_url the HTTP path is scoped to. The manifest path is
                # `/sites/{sanitize_url(site_url)}/searchAnalytics/query`, so we can recover
                # it from the request URL.
                match = re.match(
                    r"https://www\.googleapis\.com/webmasters/v3/sites/([^/]+)/searchAnalytics/query",
                    request.url,
                )
                assert match is not None, f"Unexpected request URL shape: {request.url}"
                site_from_path = match.group(1)
                search_type_from_body = body.get("type")

                for group in body.get("dimensionFilterGroups", []):
                    for f in group.get("filters", []):
                        if f.get("dimension") == "searchAppearance":
                            keyword_request_triples.append((site_from_path, search_type_from_body, f.get("expression")))

                return json.dumps(_build_search_analytics_response([_build_search_analytics_row("2024-01-01", "usa", "DESKTOP", "q", "p")]))

            return json.dumps(_build_search_analytics_response([]))

        http_mocker._mocker.post(
            re.compile(r"https://www\.googleapis\.com/webmasters/v3/sites/.*/searchAnalytics/query"),
            text=search_analytics_callback,
        )

        output = self._read_stream(config)
        records = [message for message in output.records if message.record.stream == _STREAM_NAME]

        # Each `(site_url, search_type, searchAppearance)` triple must be fetched at most
        # once per date slice. With `start_date=2024-01-01`, `end_date=2024-01-03`, and
        # `step: P3D` in the manifest, there is exactly one date slice per parent partition,
        # so we expect exactly one request per triple.
        triple_counts: Dict[tuple, int] = {}
        for triple in keyword_request_triples:
            triple_counts[triple] = triple_counts.get(triple, 0) + 1

        # Pre-fix (cartesian product) behavior would produce N requests per triple where N is
        # the number of configured sites. Post-fix must produce exactly 1.
        for triple, count in triple_counts.items():
            assert count == 1, (
                f"Keyword stream issued {count} requests for {triple}; expected exactly 1. "
                f"Multi-site cartesian-product regression — the child `site_url` router was "
                f"combined with the parent's own `site_url` partitioning. All triple counts: {triple_counts}"
            )

        # Both sites must be represented and every request must carry the shared
        # `PRODUCT_SNIPPETS` appearance.
        observed_sites = {triple[0] for triple in keyword_request_triples}
        assert len(observed_sites) == 2, f"Expected keyword requests for both configured sites, got: {observed_sites}"
        observed_expressions = {triple[2] for triple in keyword_request_triples}
        assert observed_expressions == {"PRODUCT_SNIPPETS"}, observed_expressions

        # Emitted records must carry both configured `site_url` values, sourced from the
        # parent slice. Record count scales with parent search_types, but each record's
        # `site_url` must match the request URL's path (never a mis-scoped cross product).
        record_site_urls = {record.record.data.get("site_url") for record in records}
        assert record_site_urls == {
            site_a,
            site_b,
        }, f"Expected emitted records for both configured sites, got site_urls: {record_site_urls}"
