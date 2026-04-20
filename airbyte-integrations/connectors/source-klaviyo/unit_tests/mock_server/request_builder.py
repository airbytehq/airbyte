# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from typing import Dict, Optional
from urllib.parse import parse_qs, urlparse

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


class KlaviyoRequestBuilder:
    """
    Builder for creating HTTP requests for Klaviyo API endpoints.

    This builder helps create clean, reusable request definitions for tests
    instead of manually constructing HttpRequest objects each time.

    Example usage:
        request = (
            KlaviyoRequestBuilder.profiles_endpoint("test_api_key")
            .with_page_size(100)
            .with_filter("greater-than(updated,2024-01-01T00:00:00+00:00)")
            .build()
        )
    """

    BASE_URL = "https://a.klaviyo.com/api"
    REVISION = "2024-10-15"

    @classmethod
    def profiles_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /profiles endpoint."""
        return cls("profiles", api_key)

    @classmethod
    def events_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /events endpoint."""
        return cls("events", api_key)

    @classmethod
    def templates_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /templates endpoint (email_templates stream)."""
        return cls("templates", api_key)

    @classmethod
    def campaigns_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /campaigns endpoint."""
        return cls("campaigns", api_key)

    @classmethod
    def flows_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /flows endpoint."""
        return cls("flows", api_key)

    @classmethod
    def metrics_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /metrics endpoint."""
        return cls("metrics", api_key)

    @classmethod
    def lists_endpoint(cls, api_key: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /lists endpoint."""
        return cls("lists", api_key)

    @classmethod
    def lists_detailed_endpoint(cls, api_key: str, list_id: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /lists/{list_id} endpoint."""
        return cls(f"lists/{list_id}", api_key)

    @classmethod
    def campaign_recipient_estimations_endpoint(cls, api_key: str, campaign_id: str) -> "KlaviyoRequestBuilder":
        """Create a request builder for the /campaign-recipient-estimations/{campaign_id} endpoint."""
        return cls(f"campaign-recipient-estimations/{campaign_id}", api_key)

    @classmethod
    def from_url(cls, url: str, api_key: str) -> "KlaviyoRequestBuilder":
        """
        Create a request builder from a full URL (used for pagination links).

        Args:
            url: Full URL including query parameters
            api_key: The Klaviyo API key

        Returns:
            KlaviyoRequestBuilder configured with the URL path and query params
        """
        parsed = urlparse(url)
        path = parsed.path.replace("/api/", "")
        builder = cls(path, api_key)
        builder._full_url = url
        if parsed.query:
            query_params = parse_qs(parsed.query)
            builder._query_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        return builder

    def __init__(self, resource: str, api_key: str):
        """
        Initialize the request builder.

        Args:
            resource: The API resource (e.g., 'profiles', 'events')
            api_key: The Klaviyo API key
        """
        self._resource = resource
        self._api_key = api_key
        self._query_params: Dict = {}
        self._full_url: Optional[str] = None

    def with_any_query_params(self) -> "KlaviyoRequestBuilder":
        """Accept any query parameters (useful for flexible matching)."""
        self._query_params = ANY_QUERY_PARAMS
        return self

    def with_query_params(self, query_params: dict) -> "KlaviyoRequestBuilder":
        """Set specific query parameters for the request."""
        self._query_params = query_params
        return self

    def with_page_size(self, size: int) -> "KlaviyoRequestBuilder":
        """Set the page size parameter."""
        self._query_params["page[size]"] = str(size)
        return self

    def with_filter(self, filter_expr: str) -> "KlaviyoRequestBuilder":
        """Set the filter parameter."""
        self._query_params["filter"] = filter_expr
        return self

    def with_sort(self, sort_field: str) -> "KlaviyoRequestBuilder":
        """Set the sort parameter."""
        self._query_params["sort"] = sort_field
        return self

    def with_additional_fields(self, fields: str) -> "KlaviyoRequestBuilder":
        """Set the additional-fields[profile] parameter."""
        self._query_params["additional-fields[profile]"] = fields
        return self

    def with_additional_fields_list(self, fields: str) -> "KlaviyoRequestBuilder":
        """Set the additional-fields[list] parameter."""
        self._query_params["additional-fields[list]"] = fields
        return self

    def with_fields_event(self, fields: str) -> "KlaviyoRequestBuilder":
        """Set the fields[event] parameter."""
        self._query_params["fields[event]"] = fields
        return self

    def with_fields_metric(self, fields: str) -> "KlaviyoRequestBuilder":
        """Set the fields[metric] parameter."""
        self._query_params["fields[metric]"] = fields
        return self

    def with_include(self, include: str) -> "KlaviyoRequestBuilder":
        """Set the include parameter."""
        self._query_params["include"] = include
        return self

    def build(self) -> HttpRequest:
        """
        Build and return the HttpRequest object.

        Returns:
            HttpRequest configured with the URL, query params, and headers
        """
        if self._full_url:
            parsed = urlparse(self._full_url)
            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        else:
            url = f"{self.BASE_URL}/{self._resource}"

        return HttpRequest(
            url=url,
            query_params=self._query_params if self._query_params else ANY_QUERY_PARAMS,
            headers={
                "Authorization": f"Klaviyo-API-Key {self._api_key}",
                "Accept": "application/json",
                "Revision": self.REVISION,
            },
        )
