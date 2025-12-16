# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Consolidated request builder for Zendesk Support API endpoints.

This builder helps create clean, reusable request definitions for tests
instead of manually constructing HttpRequest objects each time.

Example usage:
    request = (
        ZendeskSupportRequestBuilder.tags_endpoint("user@example.com", "password")
        .with_page_size(100)
        .with_after_cursor("cursor123")
        .build()
    )
"""

import abc
import base64
from typing import Any, Dict, Optional

from airbyte_cdk.test.mock_http import HttpRequest


class Authenticator(abc.ABC):
    """Base authenticator interface."""

    @property
    @abc.abstractmethod
    def client_access_token(self) -> str:
        """Return the authorization header value."""


class ApiTokenAuthenticator(Authenticator):
    """Authenticator for Zendesk API token authentication."""

    def __init__(self, email: str, password: str) -> None:
        super().__init__()
        self._email = f"{email}/token"
        self._password = password

    @property
    def client_access_token(self) -> str:
        api_token = base64.b64encode(f"{self._email}:{self._password}".encode("utf-8"))
        return f"Basic {api_token.decode('utf-8')}"


class ZendeskSupportRequestBuilder:
    """
    Builder for creating HTTP requests for Zendesk Support API endpoints.

    All endpoint factory methods are @classmethods that return a configured builder.
    Use fluent methods like .with_page_size() and .with_after_cursor() to add
    query parameters, then call .build() to get the HttpRequest.
    """

    DEFAULT_SUBDOMAIN = "d3v-airbyte"

    # Endpoint factory methods for each stream
    @classmethod
    def tags_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /tags endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "tags").with_authenticator(authenticator)

    @classmethod
    def brands_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /brands endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "brands").with_authenticator(authenticator)

    @classmethod
    def automations_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /automations endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "automations").with_authenticator(authenticator)

    @classmethod
    def custom_roles_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /custom_roles endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "custom_roles").with_authenticator(authenticator)

    @classmethod
    def schedules_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /business_hours/schedules.json endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "business_hours/schedules.json").with_authenticator(authenticator)

    @classmethod
    def sla_policies_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /slas/policies.json endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "slas/policies.json").with_authenticator(authenticator)

    @classmethod
    def groups_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /groups endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "groups").with_authenticator(authenticator)

    @classmethod
    def users_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /users endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "users").with_authenticator(authenticator)

    @classmethod
    def ticket_metrics_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_metrics endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_metrics").with_authenticator(authenticator)

    @classmethod
    def tickets_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /tickets endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "tickets").with_authenticator(authenticator)

    @classmethod
    def ticket_forms_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_forms endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_forms").with_authenticator(authenticator)

    @classmethod
    def articles_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/articles endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "help_center/articles").with_authenticator(authenticator)

    @classmethod
    def posts_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "community/posts").with_authenticator(authenticator)

    @classmethod
    def post_comments_endpoint(cls, authenticator: Authenticator, post_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts/{post_id}/comments endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"community/posts/{post_id}/comments").with_authenticator(authenticator)

    @classmethod
    def post_votes_endpoint(cls, authenticator: Authenticator, post_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts/{post_id}/votes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"community/posts/{post_id}/votes").with_authenticator(authenticator)

    @classmethod
    def post_comment_votes_endpoint(cls, authenticator: Authenticator, post_id: int, comment_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts/{post_id}/comments/{comment_id}/votes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"community/posts/{post_id}/comments/{comment_id}/votes").with_authenticator(authenticator)

    def __init__(self, subdomain: str, resource: str) -> None:
        """
        Initialize the request builder.

        Args:
            subdomain: The Zendesk subdomain (e.g., 'd3v-airbyte')
            resource: The API resource path (e.g., 'tags', 'brands')
        """
        self._subdomain = subdomain
        self._resource = resource
        self._authenticator: Optional[Authenticator] = None
        self._page_size: Optional[int] = None
        self._after_cursor: Optional[str] = None
        self._custom_url: Optional[str] = None
        self._query_params: Dict[str, Any] = {}

    @property
    def url(self) -> str:
        """Build the full URL for the request."""
        if self._custom_url:
            return self._custom_url
        return f"https://{self._subdomain}.zendesk.com/api/v2/{self._resource}"

    @property
    def query_params(self) -> Dict[str, Any]:
        """Build query parameters for the request."""
        params = dict(self._query_params)
        if self._page_size is not None:
            params["page[size]"] = self._page_size
        if self._after_cursor is not None:
            params["page[after]"] = self._after_cursor
        return params if params else None

    @property
    def headers(self) -> Dict[str, Any]:
        """Build headers for the request."""
        if self._authenticator:
            return {"Authorization": self._authenticator.client_access_token}
        return {}

    def with_authenticator(self, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Set the authenticator for the request."""
        self._authenticator = authenticator
        return self

    def with_page_size(self, page_size: int) -> "ZendeskSupportRequestBuilder":
        """Set the page[size] query parameter for pagination."""
        self._page_size = page_size
        return self

    def with_after_cursor(self, after_cursor: str) -> "ZendeskSupportRequestBuilder":
        """Set the page[after] query parameter for cursor-based pagination."""
        self._after_cursor = after_cursor
        return self

    def with_custom_url(self, custom_url: str) -> "ZendeskSupportRequestBuilder":
        """Override the URL for pagination requests that use next_page URLs."""
        self._custom_url = custom_url
        return self

    def with_query_param(self, key: str, value: Any) -> "ZendeskSupportRequestBuilder":
        """Add a custom query parameter."""
        self._query_params[key] = value
        return self

    def build(self) -> HttpRequest:
        """
        Build and return the HttpRequest object.

        Returns:
            HttpRequest configured with the URL, query params, and headers
        """
        return HttpRequest(
            url=self.url,
            query_params=self.query_params,
            headers=self.headers,
        )
