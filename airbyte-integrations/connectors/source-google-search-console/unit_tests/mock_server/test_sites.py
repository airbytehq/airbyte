# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""
Mock server tests for the sites stream.

The sites stream is a simple full refresh stream that:
- Uses GET requests to /webmasters/v3/sites/{site_url}
- Partitions by site_urls from config (ListPartitionRouter)
- Returns a single record per site_url
- Has no pagination
- Has no incremental sync
"""

import json
from unittest import TestCase
from urllib.parse import quote

from mock_server.config import ConfigBuilder
from mock_server.response_builder import (
    GoogleSearchConsoleSitesResponseBuilder,
    build_error_response,
    create_oauth_response,
    create_sites_response,
)

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest
from unit_tests.conftest import get_source


_STREAM_NAME = "sites"


def _sites_request(site_url: str) -> HttpRequest:
    """Build a request for the sites endpoint."""
    encoded_site_url = quote(site_url, safe="")
    return HttpRequest(
        url=f"https://www.googleapis.com/webmasters/v3/sites/{encoded_site_url}",
    )


def _oauth_request() -> HttpRequest:
    """Build a request for the OAuth token endpoint.

    The OAuth token refresh request includes a form-encoded body with:
    - grant_type: refresh_token
    - client_id: the client ID
    - client_secret: the client secret
    - refresh_token: the refresh token

    We need to match the body exactly for the mock to work.
    """
    return HttpRequest(
        url="https://oauth2.googleapis.com/token",
        body="grant_type=refresh_token&client_id=test_client_id&client_secret=test_client_secret&refresh_token=test_refresh_token",
    )


class TestSitesStream(TestCase):
    """
    Tests for the Google Search Console 'sites' stream.

    These tests verify:
    - Full refresh sync works correctly
    - Partition router handles multiple site URLs
    """

    @HttpMocker()
    def test_full_refresh_single_site(self, http_mocker: HttpMocker) -> None:
        """
        Test reading sites stream with a single site URL.

        Given: A configured Google Search Console connector with one site URL
        When: Running a full refresh sync for the sites stream
        Then: The connector should make the correct API request and return one record
        """
        config = ConfigBuilder().with_site_urls(["https://example.com/"]).build()

        http_mocker.post(_oauth_request(), create_oauth_response())
        http_mocker.get(
            _sites_request("https://example.com/"),
            create_sites_response(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 1
        assert output.records[0].record.data["siteUrl"] == "https://example.com/"
        assert output.records[0].record.data["permissionLevel"] == "siteOwner"

    @HttpMocker()
    def test_full_refresh_multiple_sites(self, http_mocker: HttpMocker) -> None:
        """
        Test reading sites stream with multiple site URLs (partition router).

        Given: A configured connector with multiple site URLs
        When: Running a full refresh sync for the sites stream
        Then: The connector should fetch data for each site URL and return all records
        """
        config = ConfigBuilder().with_site_urls(["https://example1.com/", "https://example2.com/"]).build()

        http_mocker.post(_oauth_request(), create_oauth_response())
        http_mocker.get(
            _sites_request("https://example1.com/"),
            GoogleSearchConsoleSitesResponseBuilder().with_site("https://example1.com/").build(),
        )
        http_mocker.get(
            _sites_request("https://example2.com/"),
            GoogleSearchConsoleSitesResponseBuilder().with_site("https://example2.com/", "siteFullUser").build(),
        )

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert len(output.records) == 2
        site_urls = {r.record.data["siteUrl"] for r in output.records}
        assert site_urls == {"https://example1.com/", "https://example2.com/"}

    @HttpMocker()
    def test_unverified_site_returns_config_error(self, http_mocker: HttpMocker) -> None:
        site_url = "https://unverified.example.com/"
        google_message = f"'{site_url}' is not a verified Search Console site in this account."
        config = ConfigBuilder().with_site_urls([site_url]).build()

        http_mocker.post(_oauth_request(), create_oauth_response())
        http_mocker.get(_sites_request(site_url), build_error_response(404, google_message, "notFound"))

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert output.errors
        error = output.errors[-1].trace.error
        assert error.failure_type == FailureType.config_error
        log_messages = "\n".join(log.log.message for log in output.logs)
        assert "Configured site URL is not a verified Search Console property in this account." in log_messages
        assert site_url in log_messages

    @HttpMocker()
    def test_insufficient_permissions_returns_config_error(self, http_mocker: HttpMocker) -> None:
        site_url = "https://restricted.example.com/"
        google_message = f"User does not have sufficient permission for site '{site_url}'."
        config = ConfigBuilder().with_site_urls([site_url]).build()

        http_mocker.post(_oauth_request(), create_oauth_response())
        http_mocker.get(_sites_request(site_url), build_error_response(403, google_message, "forbidden"))

        source = get_source(config=config)
        catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
        output = read(source, config=config, catalog=catalog)

        assert output.errors
        error = output.errors[-1].trace.error
        assert error.failure_type == FailureType.config_error
        log_messages = "\n".join(log.log.message for log in output.logs)
        assert "Configured site URL is not accessible with the account's Search Console permissions." in log_messages
        assert site_url in log_messages
