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
import calendar
from typing import Any, Dict, Optional, Union

from airbyte_cdk.test.mock_http import HttpRequest
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.utils.datetime_helpers import AirbyteDateTime, ab_datetime_parse


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
        """Create a request builder for the /incremental/users/cursor.json endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "incremental/users/cursor.json").with_authenticator(authenticator)

    @classmethod
    def user_identities_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /incremental/users/cursor.json endpoint with include=identities (for user_identities stream)."""
        return cls(cls.DEFAULT_SUBDOMAIN, "incremental/users/cursor.json").with_authenticator(authenticator).with_include("identities")

    @classmethod
    def ticket_metrics_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_metrics endpoint (alias for stateless)."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_metrics").with_authenticator(authenticator)

    @classmethod
    def stateless_ticket_metrics_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_metrics endpoint (stateless)."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_metrics").with_authenticator(authenticator)

    @classmethod
    def stateful_ticket_metrics_endpoint(cls, authenticator: Authenticator, ticket_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /tickets/{ticket_id}/metrics endpoint (stateful)."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"tickets/{ticket_id}/metrics").with_authenticator(authenticator)

    @classmethod
    def tickets_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /incremental/tickets/cursor.json endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "incremental/tickets/cursor.json").with_authenticator(authenticator)

    @classmethod
    def ticket_forms_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_forms endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_forms").with_authenticator(authenticator)

    @classmethod
    def articles_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/incremental/articles endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "help_center/incremental/articles").with_authenticator(authenticator)

    @classmethod
    def posts_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "community/posts").with_authenticator(authenticator)

    @classmethod
    def post_comments_endpoint(cls, authenticator: Authenticator, post_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts/{post_id}/comments endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"community/posts/{post_id}/comments").with_authenticator(authenticator)

    @classmethod
    def posts_comments_endpoint(cls, authenticator: Authenticator, post_id: int) -> "ZendeskSupportRequestBuilder":
        """Alias for post_comments_endpoint() for backward compatibility."""
        return cls.post_comments_endpoint(authenticator, post_id)

    @classmethod
    def post_votes_endpoint(cls, authenticator: Authenticator, post_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts/{post_id}/votes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"community/posts/{post_id}/votes").with_authenticator(authenticator)

    @classmethod
    def posts_votes_endpoint(cls, authenticator: Authenticator, post_id: int) -> "ZendeskSupportRequestBuilder":
        """Alias for post_votes_endpoint() for backward compatibility."""
        return cls.post_votes_endpoint(authenticator, post_id)

    @classmethod
    def post_comment_votes_endpoint(cls, authenticator: Authenticator, post_id: int, comment_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/posts/{post_id}/comments/{comment_id}/votes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"community/posts/{post_id}/comments/{comment_id}/votes").with_authenticator(authenticator)

    @classmethod
    def account_attributes_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /routing/attributes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "routing/attributes").with_authenticator(authenticator)

    @classmethod
    def attribute_definitions_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /routing/attributes/definitions endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "routing/attributes/definitions").with_authenticator(authenticator)

    @classmethod
    def user_fields_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /user_fields endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "user_fields").with_authenticator(authenticator)

    @classmethod
    def categories_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/categories endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "help_center/categories").with_authenticator(authenticator)

    @classmethod
    def sections_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/sections endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "help_center/sections").with_authenticator(authenticator)

    @classmethod
    def topics_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /community/topics endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "community/topics").with_authenticator(authenticator)

    @classmethod
    def group_memberships_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /group_memberships endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "group_memberships").with_authenticator(authenticator)

    @classmethod
    def macros_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /macros endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "macros").with_authenticator(authenticator)

    @classmethod
    def organization_fields_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /organization_fields endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "organization_fields").with_authenticator(authenticator)

    @classmethod
    def organization_memberships_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /organization_memberships endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "organization_memberships").with_authenticator(authenticator)

    @classmethod
    def organizations_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /incremental/organizations endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "incremental/organizations").with_authenticator(authenticator)

    @classmethod
    def satisfaction_ratings_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /satisfaction_ratings endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "satisfaction_ratings").with_authenticator(authenticator)

    @classmethod
    def ticket_fields_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_fields endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_fields").with_authenticator(authenticator)

    @classmethod
    def ticket_activities_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /activities endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "activities").with_authenticator(authenticator)

    @classmethod
    def ticket_audits_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /ticket_audits endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "ticket_audits").with_authenticator(authenticator)

    @classmethod
    def ticket_comments_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /incremental/ticket_events.json endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "incremental/ticket_events.json").with_authenticator(authenticator)

    @classmethod
    def ticket_metric_events_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /incremental/ticket_metric_events endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "incremental/ticket_metric_events").with_authenticator(authenticator)

    @classmethod
    def ticket_skips_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /skips.json endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "skips.json").with_authenticator(authenticator)

    @classmethod
    def triggers_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /triggers endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "triggers").with_authenticator(authenticator)

    @classmethod
    def audit_logs_endpoint(cls, authenticator: Authenticator) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /audit_logs endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, "audit_logs").with_authenticator(authenticator)

    @classmethod
    def article_comments_endpoint(cls, authenticator: Authenticator, article_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/articles/{article_id}/comments endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"help_center/articles/{article_id}/comments").with_authenticator(authenticator)

    @classmethod
    def article_votes_endpoint(cls, authenticator: Authenticator, article_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/articles/{article_id}/votes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"help_center/articles/{article_id}/votes").with_authenticator(authenticator)

    @classmethod
    def article_comment_votes_endpoint(
        cls, authenticator: Authenticator, article_id: int, comment_id: int
    ) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/articles/{article_id}/comments/{comment_id}/votes endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"help_center/articles/{article_id}/comments/{comment_id}/votes").with_authenticator(
            authenticator
        )

    @classmethod
    def article_attachments_endpoint(cls, authenticator: Authenticator, article_id: int) -> "ZendeskSupportRequestBuilder":
        """Create a request builder for the /help_center/articles/{article_id}/attachments endpoint."""
        return cls(cls.DEFAULT_SUBDOMAIN, f"help_center/articles/{article_id}/attachments").with_authenticator(authenticator)

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
        if self._query_params is ANY_QUERY_PARAMS:
            return ANY_QUERY_PARAMS
        params = {}
        for key, value in self._query_params.items():
            params[key] = value
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

    def with_page_after(self, next_page_token: str) -> "ZendeskSupportRequestBuilder":
        """Alias for with_after_cursor() for backward compatibility."""
        return self.with_after_cursor(next_page_token)

    def with_custom_url(self, custom_url: str) -> "ZendeskSupportRequestBuilder":
        """Override the URL for pagination requests that use next_page URLs."""
        self._custom_url = custom_url
        return self

    def with_query_param(self, key: str, value: Any) -> "ZendeskSupportRequestBuilder":
        """Add a custom query parameter."""
        self._query_params[key] = value
        return self

    def with_any_query_params(self) -> "ZendeskSupportRequestBuilder":
        """Allow any query parameters to match. Use when parameters are dynamic or can't be precisely mocked."""
        self._query_params = ANY_QUERY_PARAMS
        return self

    def with_start_time(self, start_time: Union[str, AirbyteDateTime, int]) -> "ZendeskSupportRequestBuilder":
        """Set the start_time query parameter for incremental syncs.

        Converts datetime strings and AirbyteDateTime to Unix timestamps.
        Integer values are passed through as-is.
        """
        if isinstance(start_time, AirbyteDateTime):
            self._query_params["start_time"] = calendar.timegm(start_time.timetuple())
        elif isinstance(start_time, int):
            self._query_params["start_time"] = start_time
        elif isinstance(start_time, str):
            parsed = ab_datetime_parse(start_time)
            self._query_params["start_time"] = calendar.timegm(parsed.utctimetuple())
        return self

    def with_cursor(self, cursor: str) -> "ZendeskSupportRequestBuilder":
        """Set the cursor query parameter for cursor-based pagination."""
        self._query_params["cursor"] = cursor
        return self

    def with_include(self, include: str) -> "ZendeskSupportRequestBuilder":
        """Set the include query parameter for including related resources."""
        self._query_params["include"] = include
        return self

    def with_per_page(self, per_page: int) -> "ZendeskSupportRequestBuilder":
        """Set the per_page query parameter for pagination."""
        self._query_params["per_page"] = per_page
        return self

    def with_sort_by(self, sort_by: str) -> "ZendeskSupportRequestBuilder":
        """Set the sort_by query parameter for sorting."""
        self._query_params["sort_by"] = sort_by
        return self

    def with_sort_order(self, sort_order: str) -> "ZendeskSupportRequestBuilder":
        """Set the sort_order query parameter for sorting."""
        self._query_params["sort_order"] = sort_order
        return self

    def with_sort(self, sort: str) -> "ZendeskSupportRequestBuilder":
        """Set the sort query parameter for sorting."""
        self._query_params["sort"] = sort
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
