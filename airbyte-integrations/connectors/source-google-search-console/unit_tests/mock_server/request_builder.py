# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Any, Dict, List, Optional
from urllib.parse import quote

from airbyte_cdk.test.mock_http.request import HttpRequest


class GoogleSearchConsoleRequestBuilder:
    """
    Builder for creating HTTP requests for Google Search Console API endpoints.

    The Google Search Console API has two main endpoint types:
    1. GET endpoints: /webmasters/v3/sites, /webmasters/v3/sites/{site_url}/sitemaps
    2. POST endpoints: /webmasters/v3/sites/{site_url}/searchAnalytics/query

    Example usage:
        request = (
            GoogleSearchConsoleRequestBuilder.sites_endpoint()
            .build()
        )

        request = (
            GoogleSearchConsoleRequestBuilder.search_analytics_endpoint("https://example.com/")
            .with_body_json({
                "startDate": "2024-01-01",
                "endDate": "2024-01-31",
                "dimensions": ["date"],
                "type": "web",
            })
            .build()
        )
    """

    _BASE_URL = "https://www.googleapis.com"

    def __init__(self, path: str, method: str = "GET"):
        self._path = path
        self._method = method
        self._query_params: Dict[str, Any] = {}
        self._body: Optional[str] = None
        self._body_json: Optional[Dict[str, Any]] = None

    @classmethod
    def sites_endpoint(cls) -> "GoogleSearchConsoleRequestBuilder":
        """Create a request builder for the sites endpoint (GET)."""
        return cls("/webmasters/v3/sites")

    @classmethod
    def sitemaps_endpoint(cls, site_url: str) -> "GoogleSearchConsoleRequestBuilder":
        """Create a request builder for the sitemaps endpoint (GET)."""
        encoded_site_url = quote(site_url, safe="")
        return cls(f"/webmasters/v3/sites/{encoded_site_url}/sitemaps")

    @classmethod
    def search_analytics_endpoint(cls, site_url: str) -> "GoogleSearchConsoleRequestBuilder":
        """Create a request builder for the search analytics endpoint (POST)."""
        encoded_site_url = quote(site_url, safe="")
        return cls(f"/webmasters/v3/sites/{encoded_site_url}/searchAnalytics/query", method="POST")

    def with_query_param(self, key: str, value: Any) -> "GoogleSearchConsoleRequestBuilder":
        """Add a query parameter to the request."""
        self._query_params[key] = value
        return self

    def with_body(self, body: str) -> "GoogleSearchConsoleRequestBuilder":
        """Set the raw body of the request."""
        self._body = body
        return self

    def with_body_json(self, body_json: Dict[str, Any]) -> "GoogleSearchConsoleRequestBuilder":
        """Set the JSON body of the request."""
        self._body_json = body_json
        return self

    def with_search_analytics_body(
        self,
        start_date: str,
        end_date: str,
        dimensions: List[str],
        search_type: str = "web",
        aggregation_type: str = "auto",
        data_state: str = "final",
        start_row: int = 0,
        row_limit: int = 25000,
    ) -> "GoogleSearchConsoleRequestBuilder":
        """Set the body for a search analytics request with common parameters."""
        self._body_json = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "type": search_type,
            "aggregationType": aggregation_type,
            "dataState": data_state,
            "startRow": start_row,
            "rowLimit": row_limit,
        }
        return self

    def build(self) -> HttpRequest:
        """Build and return the HttpRequest object."""
        url = f"{self._BASE_URL}{self._path}"

        if self._method == "GET":
            return HttpRequest(
                url=url,
                query_params=self._query_params if self._query_params else None,
            )
        else:
            return HttpRequest(
                url=url,
                query_params=self._query_params if self._query_params else None,
                body=self._body_json if self._body_json else self._body,
            )
