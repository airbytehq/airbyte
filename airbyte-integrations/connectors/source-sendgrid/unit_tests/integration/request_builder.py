# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS, HttpRequest


API_BASE_URL = "https://api.sendgrid.com"


class RequestBuilder:
    """Builder for SendGrid API requests"""

    @classmethod
    def bounces_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/suppression/bounces")

    @classmethod
    def spam_reports_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/suppression/spam_reports")

    @classmethod
    def global_suppressions_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/suppression/unsubscribes")

    @classmethod
    def blocks_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/suppression/blocks")

    @classmethod
    def invalid_emails_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/suppression/invalid_emails")

    @classmethod
    def suppression_groups_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/asm/groups")

    @classmethod
    def suppression_group_members_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/asm/suppressions")

    @classmethod
    def lists_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/lists")

    @classmethod
    def segments_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/segments/2.0")

    @classmethod
    def singlesend_stats_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/stats/singlesends")

    @classmethod
    def stats_automations_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/stats/automations")

    @classmethod
    def singlesends_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/singlesends")

    @classmethod
    def templates_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/templates")

    @classmethod
    def campaigns_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/campaigns")

    @classmethod
    def contacts_export_endpoint(cls) -> "RequestBuilder":
        return cls(resource="v3/marketing/contacts/exports")

    @classmethod
    def contacts_export_status_endpoint(cls, export_id: str) -> "RequestBuilder":
        return cls(resource=f"v3/marketing/contacts/exports/{export_id}")

    @classmethod
    def contacts_download_endpoint(cls, download_url: str) -> "RequestBuilder":
        """Create a request builder for the contacts download URL (external S3/storage URL)"""
        builder = cls()
        builder._full_url = download_url
        return builder

    def __init__(self, resource: str = "") -> None:
        self._resource = resource
        self._query_params: Dict[str, Any] = {}
        self._any_query_params = False
        self._full_url: Optional[str] = None

    def with_query_param(self, key: str, value: Any) -> "RequestBuilder":
        self._query_params[key] = value
        return self

    def with_limit(self, limit: int) -> "RequestBuilder":
        self._query_params["limit"] = str(limit)
        return self

    def with_offset(self, offset: int) -> "RequestBuilder":
        self._query_params["offset"] = str(offset)
        return self

    def with_start_time(self, start_time: int) -> "RequestBuilder":
        self._query_params["start_time"] = str(start_time)
        return self

    def with_end_time(self, end_time: int) -> "RequestBuilder":
        self._query_params["end_time"] = str(end_time)
        return self

    def with_page_size(self, page_size: int) -> "RequestBuilder":
        self._query_params["page_size"] = str(page_size)
        return self

    def with_any_query_params(self) -> "RequestBuilder":
        """Use for endpoints with dynamic query params"""
        self._any_query_params = True
        return self

    def build(self) -> HttpRequest:
        query_params = ANY_QUERY_PARAMS if self._any_query_params else (self._query_params if self._query_params else None)
        # Use full URL if set (for external URLs like S3 download), otherwise build from base + resource
        url = self._full_url if self._full_url else f"{API_BASE_URL}/{self._resource}"
        return HttpRequest(
            url=url,
            query_params=query_params,
        )
