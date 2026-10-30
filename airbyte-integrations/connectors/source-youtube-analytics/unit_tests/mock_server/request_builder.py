#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

from typing import Dict

from airbyte_cdk.test.mock_http import HttpRequest

from .config import CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN


class YoutubeAnalyticsRequestBuilder:
    """
    Builder for YouTube Reporting API requests.

    Example usage:
        request = (
            YoutubeAnalyticsRequestBuilder.reports_endpoint("job-1")
            .with_created_after("2025-11-09T00:00:00.000000Z")
            .build()
        )
    """

    BASE_URL = "https://youtubereporting.googleapis.com/v1"
    TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {}

    @classmethod
    def token_request(cls) -> HttpRequest:
        """The OAuth refresh call every sync makes before its first API request.

        `OAuthAuthenticator` form-encodes the payload in a fixed order (`abstract_oauth.py`,
        `build_refresh_request_body`), and `HttpRequest` compares non-mapping bodies byte for
        byte, so the order here has to match.
        """
        return HttpRequest(
            url=cls.TOKEN_URL,
            body=f"grant_type=refresh_token&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&refresh_token={REFRESH_TOKEN}",
        )

    @classmethod
    def jobs_endpoint(cls) -> "YoutubeAnalyticsRequestBuilder":
        return cls("/jobs")

    @classmethod
    def reports_endpoint(cls, job_id: str) -> "YoutubeAnalyticsRequestBuilder":
        return cls(f"/jobs/{job_id}/reports")

    @classmethod
    def report_types_endpoint(cls) -> "YoutubeAnalyticsRequestBuilder":
        return cls("/reportTypes").with_query_param("includeSystemManaged", "true")

    @classmethod
    def download_endpoint(cls, report_id: str) -> "YoutubeAnalyticsRequestBuilder":
        """The report file itself. `base_retriever` uses the listing's `downloadUrl` as its `url_base`."""
        return cls(f"/media/CHANNEL/{report_id}").with_query_param("alt", "media")

    @classmethod
    def download_url(cls, report_id: str) -> str:
        """The `downloadUrl` to put on a report listing, matching `download_endpoint`."""
        return f"{cls.BASE_URL}/media/CHANNEL/{report_id}?alt=media"

    def with_created_after(self, created_after: str) -> "YoutubeAnalyticsRequestBuilder":
        return self.with_query_param("createdAfter", created_after)

    def with_on_behalf_of_content_owner(self, content_owner_id: str) -> "YoutubeAnalyticsRequestBuilder":
        return self.with_query_param("onBehalfOfContentOwner", content_owner_id)

    def with_query_param(self, key: str, value: str) -> "YoutubeAnalyticsRequestBuilder":
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(url=f"{self.BASE_URL}{self._path}", query_params=dict(self._query_params))
