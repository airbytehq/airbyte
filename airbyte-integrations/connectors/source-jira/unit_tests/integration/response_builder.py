# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse


class JiraPaginatedResponseBuilder:
    """
    Builder for creating paginated Jira API responses.

    This builder simplifies creating mock responses for pagination tests by handling
    the boilerplate JSON structure that Jira API returns.

    Jira uses offset-based pagination with:
    - startAt: The starting index of the returned items
    - maxResults: The maximum number of items per page
    - total: Total number of items available
    - isLast: Boolean indicating if this is the last page

    Example usage:
        response = (
            JiraPaginatedResponseBuilder("values")
            .with_records([project1, project2])
            .with_pagination(start_at=0, max_results=50, total=100)
            .build()
        )
    """

    def __init__(self, record_field: str = "values"):
        """
        Initialize the response builder.

        Args:
            record_field: The field name containing the records (e.g., "values", "issues")
        """
        self.record_field = record_field
        self.records: List[Dict[str, Any]] = []
        self.start_at = 0
        self.max_results = 50
        self.total: Optional[int] = None
        self.is_last: Optional[bool] = None
        self._extra_fields: Dict[str, Any] = {}

    def with_records(self, records: List[Dict[str, Any]]) -> "JiraPaginatedResponseBuilder":
        """
        Add records to the response.

        Args:
            records: List of record dictionaries to include in the response

        Returns:
            Self for method chaining
        """
        self.records = records
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
            start_at: Starting index of returned items
            max_results: Maximum items per page
            total: Total number of items available (defaults to len(records) if not set)
            is_last: Whether this is the last page (calculated if not set)

        Returns:
            Self for method chaining
        """
        self.start_at = start_at
        self.max_results = max_results
        self.total = total
        self.is_last = is_last
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
        total = self.total if self.total is not None else len(self.records)

        if self.is_last is not None:
            is_last = self.is_last
        else:
            is_last = (self.start_at + self.max_results) >= total

        response_body = {
            self.record_field: self.records,
            "startAt": self.start_at,
            "maxResults": self.max_results,
            "total": total,
            "isLast": is_last,
        }

        response_body.update(self._extra_fields)

        return HttpResponse(body=json.dumps(response_body), status_code=200)

    @classmethod
    def single_page(
        cls,
        record_field: str,
        records: List[Dict[str, Any]],
        max_results: int = 50,
    ) -> HttpResponse:
        """
        Convenience method to create a single-page response.

        Args:
            record_field: The field name containing the records
            records: List of records to include
            max_results: Maximum items per page

        Returns:
            HttpResponse for a single page with isLast=True
        """
        return (
            cls(record_field)
            .with_records(records)
            .with_pagination(start_at=0, max_results=max_results, total=len(records), is_last=True)
            .build()
        )

    @classmethod
    def empty_page(cls, record_field: str = "values", max_results: int = 50) -> HttpResponse:
        """
        Convenience method to create an empty response.

        Args:
            record_field: The field name containing the records
            max_results: Maximum items per page

        Returns:
            HttpResponse for an empty result set
        """
        return (
            cls(record_field)
            .with_records([])
            .with_pagination(start_at=0, max_results=max_results, total=0, is_last=True)
            .build()
        )


class JiraJqlPaginatedResponseBuilder:
    """
    Builder for creating paginated Jira JQL search responses.

    JQL search uses token-based pagination with:
    - nextPageToken: Token for the next page (null if last page)
    - isLast: Boolean indicating if this is the last page

    Example usage:
        response = (
            JiraJqlPaginatedResponseBuilder()
            .with_records([issue1, issue2])
            .with_next_page_token("next_token_123")
            .build()
        )
    """

    def __init__(self, record_field: str = "issues"):
        """
        Initialize the response builder.

        Args:
            record_field: The field name containing the records (default: "issues")
        """
        self.record_field = record_field
        self.records: List[Dict[str, Any]] = []
        self.next_page_token: Optional[str] = None
        self.is_last: Optional[bool] = None
        self._extra_fields: Dict[str, Any] = {}

    def with_records(self, records: List[Dict[str, Any]]) -> "JiraJqlPaginatedResponseBuilder":
        """
        Add records to the response.

        Args:
            records: List of record dictionaries to include in the response

        Returns:
            Self for method chaining
        """
        self.records = records
        return self

    def with_next_page_token(self, token: Optional[str]) -> "JiraJqlPaginatedResponseBuilder":
        """
        Set the next page token.

        Args:
            token: Token for the next page, or None if this is the last page

        Returns:
            Self for method chaining
        """
        self.next_page_token = token
        return self

    def with_is_last(self, is_last: bool) -> "JiraJqlPaginatedResponseBuilder":
        """
        Set whether this is the last page.

        Args:
            is_last: True if this is the last page

        Returns:
            Self for method chaining
        """
        self.is_last = is_last
        return self

    def with_extra_field(self, key: str, value: Any) -> "JiraJqlPaginatedResponseBuilder":
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
        is_last = self.is_last if self.is_last is not None else (self.next_page_token is None)

        response_body = {
            self.record_field: self.records,
            "isLast": is_last,
        }

        if self.next_page_token is not None:
            response_body["nextPageToken"] = self.next_page_token

        response_body.update(self._extra_fields)

        return HttpResponse(body=json.dumps(response_body), status_code=200)

    @classmethod
    def single_page(cls, records: List[Dict[str, Any]], record_field: str = "issues") -> HttpResponse:
        """
        Convenience method to create a single-page response.

        Args:
            records: List of records to include
            record_field: The field name containing the records

        Returns:
            HttpResponse for a single page with no next token
        """
        return cls(record_field).with_records(records).with_is_last(True).build()

    @classmethod
    def empty_page(cls, record_field: str = "issues") -> HttpResponse:
        """
        Convenience method to create an empty response.

        Args:
            record_field: The field name containing the records

        Returns:
            HttpResponse for an empty result set
        """
        return cls(record_field).with_records([]).with_is_last(True).build()


class JiraListResponseBuilder:
    """
    Builder for creating non-paginated Jira API list responses.

    Some Jira endpoints return a simple list without pagination metadata.

    Example usage:
        response = JiraListResponseBuilder.build([role1, role2])
    """

    @classmethod
    def build(cls, records: List[Dict[str, Any]], status_code: int = 200) -> HttpResponse:
        """
        Build a simple list response.

        Args:
            records: List of records to include
            status_code: HTTP status code

        Returns:
            HttpResponse with the list as the body
        """
        return HttpResponse(body=json.dumps(records), status_code=status_code)

    @classmethod
    def empty(cls) -> HttpResponse:
        """
        Build an empty list response.

        Returns:
            HttpResponse with an empty list
        """
        return HttpResponse(body=json.dumps([]), status_code=200)


class JiraObjectResponseBuilder:
    """
    Builder for creating single object Jira API responses.

    Some Jira endpoints return a single object (e.g., permissions, settings).

    Example usage:
        response = JiraObjectResponseBuilder.build({"permissions": {...}})
    """

    @classmethod
    def build(cls, obj: Dict[str, Any], status_code: int = 200) -> HttpResponse:
        """
        Build a single object response.

        Args:
            obj: The object to return
            status_code: HTTP status code

        Returns:
            HttpResponse with the object as the body
        """
        return HttpResponse(body=json.dumps(obj), status_code=status_code)


class JiraErrorResponseBuilder:
    """
    Builder for creating Jira API error responses.

    Example usage:
        response = JiraErrorResponseBuilder.build(404, ["Issue not found"])
    """

    @classmethod
    def build(cls, status_code: int, error_messages: List[str]) -> HttpResponse:
        """
        Build an error response.

        Args:
            status_code: HTTP status code
            error_messages: List of error messages

        Returns:
            HttpResponse with error body
        """
        return HttpResponse(
            body=json.dumps({"errorMessages": error_messages}),
            status_code=status_code,
        )

    @classmethod
    def not_found(cls, message: str = "Not found") -> HttpResponse:
        """Build a 404 Not Found response."""
        return cls.build(404, [message])

    @classmethod
    def forbidden(cls, message: str = "Forbidden") -> HttpResponse:
        """Build a 403 Forbidden response."""
        return cls.build(403, [message])

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> HttpResponse:
        """Build a 401 Unauthorized response."""
        return cls.build(401, [message])

    @classmethod
    def bad_request(cls, message: str = "Bad request") -> HttpResponse:
        """Build a 400 Bad Request response."""
        return cls.build(400, [message])
