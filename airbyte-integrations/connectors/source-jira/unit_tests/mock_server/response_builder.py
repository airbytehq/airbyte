# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse


class JiraPaginatedResponseBuilder:
    """
    Builder for creating paginated Jira API responses.

    This builder simplifies creating mock responses for pagination tests by handling
    the boilerplate JSON structure that Jira API returns.

    Jira uses cursor-based pagination with the following fields:
    - startAt: The starting index of the returned items
    - maxResults: The maximum number of items returned per page
    - total: The total number of items available
    - isLast: Boolean indicating if this is the last page

    The stop_condition in the manifest is:
    {{ response.get('isLast') or response.get('startAt') + response.get('maxResults') >= response.get('total') }}

    Example usage:
        response = (
            JiraPaginatedResponseBuilder("values")
            .with_records([project1, project2])
            .with_pagination(start_at=0, max_results=50, total=100, is_last=False)
            .build()
        )
    """

    def __init__(self, records_field: str = "values"):
        """
        Initialize the response builder.

        Args:
            records_field: The field name containing the records array (e.g., "values", "issues")
        """
        self._records_field = records_field
        self._records: List[Dict[str, Any]] = []
        self._start_at: int = 0
        self._max_results: int = 50
        self._total: Optional[int] = None
        self._is_last: Optional[bool] = None
        self._status_code: int = 200
        self._extra_fields: Dict[str, Any] = {}

    def with_records(self, records: List[Dict[str, Any]]) -> "JiraPaginatedResponseBuilder":
        """
        Add records to the response.

        Args:
            records: List of record dictionaries to include in the response

        Returns:
            Self for method chaining
        """
        self._records = records
        return self

    def with_pagination(
        self,
        start_at: int = 0,
        max_results: int = 50,
        total: Optional[int] = None,
        is_last: Optional[bool] = None,
    ) -> "JiraPaginatedResponseBuilder":
        """
        Set pagination metadata.

        Args:
            start_at: The starting index of the returned items
            max_results: The maximum number of items returned per page
            total: The total number of items available (defaults to len(records) if not set)
            is_last: Boolean indicating if this is the last page (calculated if not set)

        Returns:
            Self for method chaining
        """
        self._start_at = start_at
        self._max_results = max_results
        self._total = total
        self._is_last = is_last
        return self

    def with_status_code(self, status_code: int) -> "JiraPaginatedResponseBuilder":
        """
        Set the HTTP status code.

        Args:
            status_code: HTTP status code for the response

        Returns:
            Self for method chaining
        """
        self._status_code = status_code
        return self

    def with_extra_field(self, key: str, value: Any) -> "JiraPaginatedResponseBuilder":
        """
        Add an extra field to the response body.

        Args:
            key: Field name
            value: Field value

        Returns:
            Self for method chaining
        """
        self._extra_fields[key] = value
        return self

    def build(self) -> HttpResponse:
        """
        Build the HTTP response with paginated data.

        Returns:
            HttpResponse object with the paginated response body
        """
        total = self._total if self._total is not None else len(self._records)

        if self._is_last is not None:
            is_last = self._is_last
        else:
            is_last = (self._start_at + self._max_results) >= total

        response_body = {
            self._records_field: self._records,
            "startAt": self._start_at,
            "maxResults": self._max_results,
            "total": total,
            "isLast": is_last,
        }

        response_body.update(self._extra_fields)

        return HttpResponse(body=json.dumps(response_body), status_code=self._status_code)

    @classmethod
    def single_page(cls, records_field: str, records: List[Dict[str, Any]]) -> HttpResponse:
        """
        Convenience method to create a single-page response.

        Args:
            records_field: The field name containing the records array
            records: List of records to include

        Returns:
            HttpResponse for a single page with isLast=True
        """
        return (
            cls(records_field).with_records(records).with_pagination(start_at=0, max_results=50, total=len(records), is_last=True).build()
        )

    @classmethod
    def empty_page(cls, records_field: str = "values") -> HttpResponse:
        """
        Convenience method to create an empty response.

        Args:
            records_field: The field name containing the records array

        Returns:
            HttpResponse for an empty result set
        """
        return cls(records_field).with_records([]).with_pagination(start_at=0, max_results=50, total=0, is_last=True).build()


class JiraAgileResponseBuilder:
    """
    Builder for creating Agile API responses (boards, sprints, etc.).

    The Agile API uses a slightly different pagination structure with 'values' as the records field.
    """

    def __init__(self, records_field: str = "values"):
        """
        Initialize the response builder.

        Args:
            records_field: The field name containing the records array
        """
        self._records_field = records_field
        self._records: List[Dict[str, Any]] = []
        self._start_at: int = 0
        self._max_results: int = 50
        self._total: Optional[int] = None
        self._is_last: Optional[bool] = None
        self._status_code: int = 200

    def with_records(self, records: List[Dict[str, Any]]) -> "JiraAgileResponseBuilder":
        """Add records to the response."""
        self._records = records
        return self

    def with_pagination(
        self,
        start_at: int = 0,
        max_results: int = 50,
        total: Optional[int] = None,
        is_last: Optional[bool] = None,
    ) -> "JiraAgileResponseBuilder":
        """Set pagination metadata."""
        self._start_at = start_at
        self._max_results = max_results
        self._total = total
        self._is_last = is_last
        return self

    def with_status_code(self, status_code: int) -> "JiraAgileResponseBuilder":
        """Set the HTTP status code."""
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        """Build the HTTP response."""
        total = self._total if self._total is not None else len(self._records)

        if self._is_last is not None:
            is_last = self._is_last
        else:
            is_last = (self._start_at + self._max_results) >= total

        response_body = {
            self._records_field: self._records,
            "startAt": self._start_at,
            "maxResults": self._max_results,
            "total": total,
            "isLast": is_last,
        }

        return HttpResponse(body=json.dumps(response_body), status_code=self._status_code)


class JiraJqlResponseBuilder:
    """
    Builder for creating JQL search responses (issues stream).

    The JQL API uses 'issues' as the records field and supports nextPageToken pagination.
    """

    def __init__(self):
        """Initialize the response builder."""
        self._records: List[Dict[str, Any]] = []
        self._start_at: int = 0
        self._max_results: int = 50
        self._total: Optional[int] = None
        self._is_last: Optional[bool] = None
        self._next_page_token: Optional[str] = None
        self._status_code: int = 200

    def with_records(self, records: List[Dict[str, Any]]) -> "JiraJqlResponseBuilder":
        """Add records to the response."""
        self._records = records
        return self

    def with_pagination(
        self,
        start_at: int = 0,
        max_results: int = 50,
        total: Optional[int] = None,
        is_last: Optional[bool] = None,
        next_page_token: Optional[str] = None,
    ) -> "JiraJqlResponseBuilder":
        """Set pagination metadata."""
        self._start_at = start_at
        self._max_results = max_results
        self._total = total
        self._is_last = is_last
        self._next_page_token = next_page_token
        return self

    def with_status_code(self, status_code: int) -> "JiraJqlResponseBuilder":
        """Set the HTTP status code."""
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        """Build the HTTP response."""
        total = self._total if self._total is not None else len(self._records)

        if self._is_last is not None:
            is_last = self._is_last
        else:
            is_last = self._next_page_token is None

        response_body: Dict[str, Any] = {
            "issues": self._records,
            "startAt": self._start_at,
            "maxResults": self._max_results,
            "total": total,
            "isLast": is_last,
        }

        if self._next_page_token:
            response_body["nextPageToken"] = self._next_page_token

        return HttpResponse(body=json.dumps(response_body), status_code=self._status_code)


class JiraErrorResponseBuilder:
    """
    Builder for creating Jira error responses.
    """

    def __init__(self):
        """Initialize the error response builder."""
        self._error_messages: List[str] = []
        self._errors: Dict[str, str] = {}
        self._status_code: int = 400

    def with_error_messages(self, messages: List[str]) -> "JiraErrorResponseBuilder":
        """Add error messages to the response."""
        self._error_messages = messages
        return self

    def with_errors(self, errors: Dict[str, str]) -> "JiraErrorResponseBuilder":
        """Add field-specific errors to the response."""
        self._errors = errors
        return self

    def with_status_code(self, status_code: int) -> "JiraErrorResponseBuilder":
        """Set the HTTP status code."""
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        """Build the HTTP error response."""
        response_body: Dict[str, Any] = {}

        if self._error_messages:
            response_body["errorMessages"] = self._error_messages

        if self._errors:
            response_body["errors"] = self._errors

        return HttpResponse(body=json.dumps(response_body), status_code=self._status_code)


class JiraSimpleResponseBuilder:
    """
    Builder for creating simple Jira API responses without pagination.

    Used for endpoints that return a single object or a simple array.
    """

    def __init__(self):
        """Initialize the simple response builder."""
        self._body: Any = None
        self._status_code: int = 200

    def with_body(self, body: Any) -> "JiraSimpleResponseBuilder":
        """Set the response body."""
        self._body = body
        return self

    def with_status_code(self, status_code: int) -> "JiraSimpleResponseBuilder":
        """Set the HTTP status code."""
        self._status_code = status_code
        return self

    def build(self) -> HttpResponse:
        """Build the HTTP response."""
        return HttpResponse(body=json.dumps(self._body), status_code=self._status_code)
