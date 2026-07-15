# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def create_response(resource_name: str, status_code: int = 200) -> HttpResponse:
    """
    Create HTTP response using template from resource/http/response/<resource_name>.json

    Args:
        resource_name: Name of the JSON file (without .json extension)
        status_code: HTTP status code
    """
    body = json.dumps(find_template(resource_name, __file__))
    return HttpResponse(body, status_code)


def create_oauth_response() -> HttpResponse:
    """Create OAuth token response from template."""
    return create_response("oauth")


def create_sites_response() -> HttpResponse:
    """Create sites endpoint response from template."""
    return create_response("sites")


def create_sitemaps_response() -> HttpResponse:
    """Create sitemaps endpoint response from template."""
    return create_response("sitemaps")


def create_sitemaps_empty_response() -> HttpResponse:
    """Create empty sitemaps endpoint response from template."""
    return create_response("sitemaps_empty")


def create_search_analytics_response() -> HttpResponse:
    """Create search analytics endpoint response from template."""
    return create_response("search_analytics")


def create_search_analytics_empty_response() -> HttpResponse:
    """Create empty search analytics endpoint response from template."""
    return create_response("search_analytics_empty")


def create_search_appearances_response() -> HttpResponse:
    """Create search appearances endpoint response from template."""
    return create_response("search_appearances")


def error_response(status_code: int) -> HttpResponse:
    """Create error response (400, 403, 429, etc.) from template."""
    return create_response(str(status_code), status_code)


class GoogleSearchConsoleSitesResponseBuilder:
    """
    Builder for creating HTTP responses for the sites endpoint.

    The sites endpoint /webmasters/v3/sites/{site_url} returns a single site object:
    {
        "siteUrl": "https://example.com/",
        "permissionLevel": "siteOwner"
    }
    """

    def __init__(self):
        self._site_url: str = "https://example.com/"
        self._permission_level: str = "siteOwner"

    def with_site(
        self,
        site_url: str,
        permission_level: str = "siteOwner",
    ) -> "GoogleSearchConsoleSitesResponseBuilder":
        """Set the site details for the response."""
        self._site_url = site_url
        self._permission_level = permission_level
        return self

    def build(self) -> HttpResponse:
        """Build and return the HttpResponse object."""
        body = {
            "siteUrl": self._site_url,
            "permissionLevel": self._permission_level,
        }
        return HttpResponse(body=json.dumps(body), status_code=200)


class GoogleSearchConsoleSitemapsResponseBuilder:
    """
    Builder for creating HTTP responses for the sitemaps endpoint.

    The sitemaps endpoint returns a list of sitemaps in the format:
    {
        "sitemap": [
            {
                "path": "https://example.com/sitemap.xml",
                "lastSubmitted": "2024-01-01T00:00:00.000Z",
                "isPending": false,
                "isSitemapsIndex": false,
                "type": "sitemap",
                "lastDownloaded": "2024-01-01T00:00:00.000Z",
                "warnings": "0",
                "errors": "0",
                "contents": [...]
            },
            ...
        ]
    }
    """

    def __init__(self):
        self._sitemaps: List[Dict[str, Any]] = []

    def with_sitemap(
        self,
        path: str,
        last_submitted: str = "2024-01-01T00:00:00.000Z",
        is_pending: bool = False,
        is_sitemaps_index: bool = False,
        sitemap_type: str = "sitemap",
        last_downloaded: str = "2024-01-01T00:00:00.000Z",
        warnings: str = "0",
        errors: str = "0",
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> "GoogleSearchConsoleSitemapsResponseBuilder":
        """Add a sitemap to the response."""
        sitemap = {
            "path": path,
            "lastSubmitted": last_submitted,
            "isPending": is_pending,
            "isSitemapsIndex": is_sitemaps_index,
            "type": sitemap_type,
            "lastDownloaded": last_downloaded,
            "warnings": warnings,
            "errors": errors,
            "contents": contents if contents else [{"type": "web", "submitted": "100", "indexed": "95"}],
        }
        self._sitemaps.append(sitemap)
        return self

    def build(self) -> HttpResponse:
        """Build and return the HttpResponse object."""
        body = {"sitemap": self._sitemaps}
        return HttpResponse(body=json.dumps(body), status_code=200)


class GoogleSearchConsoleSearchAnalyticsResponseBuilder:
    """
    Builder for creating HTTP responses for the search analytics endpoint.

    The search analytics endpoint returns rows in the format:
    {
        "rows": [
            {
                "keys": ["2024-01-01", "usa", "desktop"],
                "clicks": 100,
                "impressions": 1000,
                "ctr": 0.1,
                "position": 5.5
            },
            ...
        ],
        "responseAggregationType": "auto"
    }

    Pagination is handled via startRow/rowLimit in the request body.
    When there are more results, the response contains the same number of rows as rowLimit.
    When there are no more results, the response contains fewer rows than rowLimit or is empty.
    """

    def __init__(self):
        self._rows: List[Dict[str, Any]] = []
        self._response_aggregation_type: str = "auto"

    def with_record(
        self,
        keys: List[str],
        clicks: int = 0,
        impressions: int = 0,
        ctr: float = 0.0,
        position: float = 0.0,
    ) -> "GoogleSearchConsoleSearchAnalyticsResponseBuilder":
        """Add a record to the response."""
        self._rows.append(
            {
                "keys": keys,
                "clicks": clicks,
                "impressions": impressions,
                "ctr": ctr,
                "position": position,
            }
        )
        return self

    def with_aggregation_type(self, aggregation_type: str) -> "GoogleSearchConsoleSearchAnalyticsResponseBuilder":
        """Set the response aggregation type."""
        self._response_aggregation_type = aggregation_type
        return self

    def build(self) -> HttpResponse:
        """Build and return the HttpResponse object."""
        body: Dict[str, Any] = {"responseAggregationType": self._response_aggregation_type}
        if self._rows:
            body["rows"] = self._rows
        return HttpResponse(body=json.dumps(body), status_code=200)


def build_error_response(status_code: int, error_message: str, error_reason: str = "error") -> HttpResponse:
    """Build an error response with the given status code and message."""
    body = {
        "error": {
            "code": status_code,
            "message": error_message,
            "errors": [
                {
                    "message": error_message,
                    "domain": "global",
                    "reason": error_reason,
                }
            ],
        }
    }
    return HttpResponse(body=json.dumps(body), status_code=status_code)


def build_permission_denied_response() -> HttpResponse:
    """Build a 403 permission denied response from template."""
    return error_response(403)


def build_rate_limited_response() -> HttpResponse:
    """Build a 429 rate limited response from template."""
    return error_response(429)


def build_bad_request_response(message: str = "Invalid request") -> HttpResponse:
    """Build a 400 bad request response from template."""
    return error_response(400)
