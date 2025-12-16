# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the sitemaps stream.

The sitemaps stream is a full refresh stream that:
- Uses GET requests to /webmasters/v3/sites/{site_url}/sitemaps
- Partitions by site_urls from config (ListPartitionRouter)
- Extracts records from the 'sitemap' field in the response
- Has no pagination
- Has no incremental sync
"""

import json
from unittest import TestCase
from urllib.parse import quote

from mock_server.config import ConfigBuilder

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


_STREAM_NAME = "sitemaps"


def _build_sitemaps_response(sitemaps: list) -> HttpResponse:
    """Build a response for the sitemaps endpoint.

    The sitemaps endpoint returns a response with a 'sitemap' array containing
    sitemap objects with path, lastSubmitted, isPending, isSitemapsIndex, type, etc.
    """
    body = {"sitemap": sitemaps}
    return HttpResponse(body=json.dumps(body), status_code=200)


def _build_sitemap_record(
    path: str,
    sitemap_type: str = "sitemap",
    is_pending: bool = False,
    is_sitemaps_index: bool = False,
    last_submitted: str = "2024-01-15T10:30:00.000Z",
    last_downloaded: str = "2024-01-15T11:00:00.000Z",
) -> dict:
    """Build a single sitemap record."""
    return {
        "path": path,
        "lastSubmitted": last_submitted,
        "isPending": is_pending,
        "isSitemapsIndex": is_sitemaps_index,
        "type": sitemap_type,
        "lastDownloaded": last_downloaded,
        "warnings": "0",
        "errors": "0",
        "contents": [{"type": "web", "submitted": "100", "indexed": "95"}],
    }


def _build_oauth_response() -> HttpResponse:
    """Build a mock OAuth token response."""
    body = {
        "access_token": "test_access_token",
        "expires_in": 3600,
        "token_type": "Bearer",
    }
    return HttpResponse(body=json.dumps(body), status_code=200)


def _sitemaps_request(site_url: str) -> HttpRequest:
    """Build a request for the sitemaps endpoint."""
    encoded_site_url = quote(site_url, safe="")
    return HttpRequest(
        url=f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site_url}/sitemaps",
    )


def _oauth_request() -> HttpRequest:
    """Build a request for the OAuth token endpoint."""
    return HttpRequest(
        url="https://oauth2.googleapis.com/token",
        body="grant_type=refresh_token&client_id=test_client_id&client_secret=test_client_secret&refresh_token=test_refresh_token",
    )


class TestSitemapsStream(TestCase):
    """
    Tests for the Google Search Console 'sitemaps' stream.

    These tests verify:
    - Full refresh sync works correctly
    - Partition router handles multiple site URLs
    - Records are correctly extracted from the 'sitemap' field
    - Empty sitemap responses are handled correctly
    """

    @HttpMocker()
    def test_full_refresh_single_site_with_sitemaps(self, http_mocker: HttpMocker) -> None:
        """
        Test reading sitemaps stream with a single site URL that has sitemaps.

        Given: A configured connector with one site URL that has sitemaps
        When: Running a full refresh sync for the sitemaps stream
        Then: The connector should return all sitemap records for that site
        """
        config = ConfigBuilder().with_site_urls(["https://example.com/"]).build()

        http_mocker.post(_oauth_request(), _build_oauth_response())
        http_mocker.get(
            _sitemaps_request("https://example.com/"),
            _build_sitemaps_response(
                [
                    _build_sitemap_record("https://example.com/sitemap.xml"),
                    _build_sitemap_record("https://example.com/sitemap-posts.xml", sitemap_type="sitemap"),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        paths = {r.record.data["path"] for r in output.records}
        assert paths == {"https://example.com/sitemap.xml", "https://example.com/sitemap-posts.xml"}

    @HttpMocker()
    def test_full_refresh_multiple_sites(self, http_mocker: HttpMocker) -> None:
        """
        Test reading sitemaps stream with multiple site URLs (partition router).

        Given: A configured connector with multiple site URLs
        When: Running a full refresh sync for the sitemaps stream
        Then: The connector should fetch sitemaps for each site URL and return all records
        """
        config = ConfigBuilder().with_site_urls(["https://example1.com/", "https://example2.com/"]).build()

        http_mocker.post(_oauth_request(), _build_oauth_response())
        http_mocker.get(
            _sitemaps_request("https://example1.com/"),
            _build_sitemaps_response(
                [
                    _build_sitemap_record("https://example1.com/sitemap.xml"),
                ]
            ),
        )
        http_mocker.get(
            _sitemaps_request("https://example2.com/"),
            _build_sitemaps_response(
                [
                    _build_sitemap_record("https://example2.com/sitemap.xml"),
                    _build_sitemap_record("https://example2.com/sitemap-products.xml"),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 3
        paths = {r.record.data["path"] for r in output.records}
        assert paths == {
            "https://example1.com/sitemap.xml",
            "https://example2.com/sitemap.xml",
            "https://example2.com/sitemap-products.xml",
        }

    @HttpMocker()
    def test_full_refresh_empty_sitemaps(self, http_mocker: HttpMocker) -> None:
        """
        Test reading sitemaps stream when a site has no sitemaps.

        Given: A configured connector with a site URL that has no sitemaps
        When: Running a full refresh sync for the sitemaps stream
        Then: The connector should return zero records without errors
        """
        config = ConfigBuilder().with_site_urls(["https://example.com/"]).build()

        http_mocker.post(_oauth_request(), _build_oauth_response())
        http_mocker.get(
            _sitemaps_request("https://example.com/"),
            _build_sitemaps_response([]),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 0
        # Verify no ERROR logs were produced
        assert not any(log.log.level == "ERROR" for log in output.logs)

    @HttpMocker()
    def test_full_refresh_sc_domain_format(self, http_mocker: HttpMocker) -> None:
        """
        Test reading sitemaps stream with sc-domain format site URL.

        Given: A configured connector with an sc-domain format site URL
        When: Running a full refresh sync for the sitemaps stream
        Then: The connector should correctly encode the URL and return the sitemaps
        """
        config = ConfigBuilder().with_site_urls(["sc-domain:example.com"]).build()

        http_mocker.post(_oauth_request(), _build_oauth_response())
        http_mocker.get(
            _sitemaps_request("sc-domain:example.com"),
            _build_sitemaps_response(
                [
                    _build_sitemap_record("https://example.com/sitemap.xml"),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["path"] == "https://example.com/sitemap.xml"

    @HttpMocker()
    def test_sitemap_record_fields(self, http_mocker: HttpMocker) -> None:
        """
        Test that sitemap records contain all expected fields.

        Given: A configured connector with a site URL that has sitemaps
        When: Running a full refresh sync for the sitemaps stream
        Then: The returned records should contain all expected fields
        """
        config = ConfigBuilder().with_site_urls(["https://example.com/"]).build()

        http_mocker.post(_oauth_request(), _build_oauth_response())
        http_mocker.get(
            _sitemaps_request("https://example.com/"),
            _build_sitemaps_response(
                [
                    _build_sitemap_record(
                        path="https://example.com/sitemap.xml",
                        sitemap_type="sitemap",
                        is_pending=False,
                        is_sitemaps_index=True,
                        last_submitted="2024-01-15T10:30:00.000Z",
                        last_downloaded="2024-01-15T11:00:00.000Z",
                    ),
                ]
            ),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        record = output.records[0].record.data
        assert record["path"] == "https://example.com/sitemap.xml"
        assert record["type"] == "sitemap"
        assert record["isPending"] is False
        assert record["isSitemapsIndex"] is True
        assert record["lastSubmitted"] == "2024-01-15T10:30:00.000Z"
        assert record["lastDownloaded"] == "2024-01-15T11:00:00.000Z"
        assert record["warnings"] == "0"
        assert record["errors"] == "0"
        assert "contents" in record
