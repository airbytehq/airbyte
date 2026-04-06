# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse


class HarvestPaginatedResponseBuilder:
    """
    Builder for creating paginated Harvest API responses.

    This builder simplifies creating mock responses for pagination tests by handling
    the boilerplate JSON structure that Harvest API returns.

    Example usage:
        response = (
            HarvestPaginatedResponseBuilder("clients")
            .with_records([client1, client2])
            .with_page(1, total_pages=2)
            .with_next_page()
            .build()
        )
    """

    def __init__(self, resource_name: str, base_url: str = "https://api.harvestapp.com/v2"):
        """
        Initialize the response builder.

        Args:
            resource_name: The API resource name (e.g., "clients", "projects", "time_entries")
            base_url: Base URL for the API (default: Harvest v2 API)
        """
        self.resource_name = resource_name
        self.base_url = base_url
        self.records = []
        self.page = 1
        self.per_page = 50
        self.total_pages = 1
        self.total_entries = None  # Will be calculated if not set
        self._include_next = False
        self._include_previous = False
        self._query_params: Dict[str, str] = {}

    def with_records(self, records: List[Dict[str, Any]]):
        """
        Add records to the response.

        Args:
            records: List of record dictionaries to include in the response

        Returns:
            Self for method chaining
        """
        self.records = records
        return self

    def with_page(self, page: int, total_pages: int = 1, per_page: int = 50):
        """
        Set pagination metadata.

        Args:
            page: Current page number
            total_pages: Total number of pages available
            per_page: Number of records per page

        Returns:
            Self for method chaining
        """
        self.page = page
        self.total_pages = total_pages
        self.per_page = per_page
        return self

    def with_total_entries(self, total_entries: int):
        """
        Set the total number of entries across all pages.

        Args:
            total_entries: Total count of entries

        Returns:
            Self for method chaining
        """
        self.total_entries = total_entries
        return self

    def with_next_page(self):
        """
        Include a 'next' link in the response.

        The next link will only be added if current page < total_pages.

        Returns:
            Self for method chaining
        """
        self._include_next = True
        return self

    def with_previous_page(self):
        """
        Include a 'previous' link in the response.

        The previous link will only be added if current page > 1.

        Returns:
            Self for method chaining
        """
        self._include_previous = True
        return self

    def with_query_param(self, key: str, value: str):
        """
        Add a query parameter to include in pagination links.

        Useful for including parameters like 'updated_since' in pagination URLs.

        Args:
            key: Query parameter name
            value: Query parameter value

        Returns:
            Self for method chaining
        """
        self._query_params[key] = value
        return self

    def _build_url(self, page: int) -> str:
        """
        Build a pagination URL with query parameters.

        Args:
            page: Page number for the URL

        Returns:
            Fully constructed URL with query parameters
        """
        params = [f"page={page}", f"per_page={self.per_page}"]
        params.extend([f"{k}={v}" for k, v in self._query_params.items()])
        query_string = "&".join(params)
        return f"{self.base_url}/{self.resource_name}?{query_string}"

    def build(self) -> HttpResponse:
        """
        Build the HTTP response with paginated data.

        Returns:
            HttpResponse object with the paginated response body
        """
        # Build links object
        links: Dict[str, Optional[str]] = {
            "first": self._build_url(1),
            "last": self._build_url(self.total_pages),
        }

        # Add next link if requested and not on last page
        if self._include_next and self.page < self.total_pages:
            links["next"] = self._build_url(self.page + 1)
        else:
            links["next"] = None

        # Add previous link if requested and not on first page
        if self._include_previous and self.page > 1:
            links["previous"] = self._build_url(self.page - 1)
        else:
            links["previous"] = None

        # Calculate total_entries if not explicitly set
        if self.total_entries is None:
            self.total_entries = len(self.records)

        # Build response body following Harvest API structure
        response_body = {
            self.resource_name: self.records,
            "per_page": self.per_page,
            "total_pages": self.total_pages,
            "total_entries": self.total_entries,
            "page": self.page,
            "links": links,
        }

        return HttpResponse(body=json.dumps(response_body), status_code=200)

    @classmethod
    def single_page(cls, resource_name: str, records: List[Dict[str, Any]], per_page: int = 50) -> HttpResponse:
        """
        Convenience method to create a single-page response.

        Args:
            resource_name: The API resource name
            records: List of records to include
            per_page: Records per page

        Returns:
            HttpResponse for a single page with no pagination links
        """
        return cls(resource_name).with_records(records).with_page(1, total_pages=1, per_page=per_page).build()

    @classmethod
    def empty_page(cls, resource_name: str, per_page: int = 50) -> HttpResponse:
        """
        Convenience method to create an empty response.

        Args:
            resource_name: The API resource name
            per_page: Records per page

        Returns:
            HttpResponse for an empty result set
        """
        return cls(resource_name).with_records([]).with_page(1, total_pages=0, per_page=per_page).with_total_entries(0).build()
