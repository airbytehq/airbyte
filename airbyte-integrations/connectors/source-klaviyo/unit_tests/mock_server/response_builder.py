# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class KlaviyoPaginatedResponseBuilder:
    """
    Builder for creating paginated Klaviyo API responses.

    This builder simplifies creating mock responses for pagination tests by handling
    the boilerplate JSON structure that Klaviyo API returns.

    Example usage:
        response = (
            KlaviyoPaginatedResponseBuilder()
            .with_records([record1, record2])
            .with_next_page_link("https://a.klaviyo.com/api/profiles?page[cursor]=abc123")
            .build()
        )
    """

    def __init__(self, base_url: str = "https://a.klaviyo.com/api"):
        """
        Initialize the response builder.

        Args:
            base_url: Base URL for the API (default: Klaviyo API)
        """
        self.base_url = base_url
        self.records: List[Dict[str, Any]] = []
        self._next_page_link: Optional[str] = None
        self._self_link: Optional[str] = None

    def with_records(self, records: List[Dict[str, Any]]) -> "KlaviyoPaginatedResponseBuilder":
        """
        Add records to the response.

        Args:
            records: List of record dictionaries to include in the response

        Returns:
            Self for method chaining
        """
        self.records = records
        return self

    def with_next_page_link(self, next_link: str) -> "KlaviyoPaginatedResponseBuilder":
        """
        Set the next page link for pagination.

        Args:
            next_link: Full URL for the next page

        Returns:
            Self for method chaining
        """
        self._next_page_link = next_link
        return self

    def with_self_link(self, self_link: str) -> "KlaviyoPaginatedResponseBuilder":
        """
        Set the self link for the current page.

        Args:
            self_link: Full URL for the current page

        Returns:
            Self for method chaining
        """
        self._self_link = self_link
        return self

    def build(self) -> HttpResponse:
        """
        Build the HTTP response with paginated data.

        Returns:
            HttpResponse object with the paginated response body
        """
        links: Dict[str, Optional[str]] = {}

        if self._self_link:
            links["self"] = self._self_link

        if self._next_page_link:
            links["next"] = self._next_page_link

        response_body: Dict[str, Any] = {
            "data": self.records,
        }

        if links:
            response_body["links"] = links

        return HttpResponse(body=json.dumps(response_body), status_code=200)

    @classmethod
    def single_page(cls, records: List[Dict[str, Any]]) -> HttpResponse:
        """
        Convenience method to create a single-page response.

        Args:
            records: List of records to include

        Returns:
            HttpResponse for a single page with no pagination links
        """
        return cls().with_records(records).build()

    @classmethod
    def empty_page(cls) -> HttpResponse:
        """
        Convenience method to create an empty response.

        Returns:
            HttpResponse for an empty result set
        """
        return cls().with_records([]).build()


def create_response(resource_name: str, status_code: int = 200, has_next: bool = False, next_cursor: Optional[str] = None) -> HttpResponse:
    """
    Create HTTP response using template from resource/http/response/<resource_name>.json

    Args:
        resource_name: Name of the JSON file (without .json extension)
        status_code: HTTP status code
        has_next: Whether there's a next page (for pagination)
        next_cursor: Cursor value for pagination
    """
    body = json.dumps(find_template(resource_name, __file__))

    return HttpResponse(body, status_code)


def error_response(status_code: int, error_message: str = "Error occurred") -> HttpResponse:
    """Create error response (401, 403, 429, etc.)"""
    error_body = {
        "errors": [
            {
                "id": "error-id",
                "status": status_code,
                "code": "error_code",
                "title": "Error",
                "detail": error_message,
            }
        ]
    }

    headers = {}
    if status_code == 429:
        headers["Retry-After"] = "1"

    return HttpResponse(json.dumps(error_body), status_code, headers)
