# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any

from airbyte_cdk.test.mock_http import HttpRequest


API_BASE_URL = "https://api.appstoreconnect.apple.com/v1"
PAGE_SIZE = "200"


class RequestBuilder:
    """Fluent builder for exact App Store Connect request matching."""

    def __init__(self, url: str) -> None:
        self._url = url
        self._query_params: dict[str, Any] = {}

    @classmethod
    def apps_endpoint(cls) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/apps").with_page_size()

    @classmethod
    def app_substream_endpoint(cls, app_id: str, resource: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/apps/{app_id}/{resource}").with_page_size()

    @classmethod
    def customer_reviews_endpoint(cls, app_id: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/apps/{app_id}/customerReviews")

    @classmethod
    def sales_reports_endpoint(cls) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/salesReports")

    @classmethod
    def finance_reports_endpoint(cls) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/financeReports")

    @classmethod
    def analytics_report_requests_endpoint(cls, app_id: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/apps/{app_id}/analyticsReportRequests").with_page_size()

    @classmethod
    def analytics_reports_endpoint(cls, request_id: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/analyticsReportRequests/{request_id}/reports").with_page_size()

    @classmethod
    def analytics_instances_endpoint(cls, report_id: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/analyticsReports/{report_id}/instances").with_page_size()

    @classmethod
    def analytics_segments_endpoint(cls, instance_id: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/analyticsReportInstances/{instance_id}/segments").with_page_size()

    @classmethod
    def analytics_segment_endpoint(cls, segment_id: str) -> "RequestBuilder":
        return cls(f"{API_BASE_URL}/analyticsReportSegments/{segment_id}")

    @classmethod
    def download_endpoint(cls, url: str) -> "RequestBuilder":
        return cls(url)

    def with_query_param(self, name: str, value: Any) -> "RequestBuilder":
        self._query_params[name] = value
        return self

    def with_page_size(self) -> "RequestBuilder":
        return self.with_query_param("limit", PAGE_SIZE)

    def with_cursor(self, cursor: str) -> "RequestBuilder":
        return self.with_query_param("cursor", cursor)

    @property
    def url(self) -> str:
        return self._url

    def build(self) -> HttpRequest:
        return HttpRequest(url=self._url, query_params=self._query_params or None)
