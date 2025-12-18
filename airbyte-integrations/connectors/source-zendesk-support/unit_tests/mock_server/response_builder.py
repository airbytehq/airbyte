# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Consolidated response builder for Zendesk Support API responses.

This module provides response builders for creating mock HTTP responses
for tests, including pagination strategies and error responses.

Example usage:
    response = (
        ZendeskSupportResponseBuilder.tags_response(request_for_pagination)
        .with_record(TagsRecordBuilder.tags_record())
        .build()
    )
"""

import json
from typing import Any, Dict, Optional

from airbyte_cdk.connector_builder.models import HttpRequest
from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    PaginationStrategy,
    Path,
    RecordBuilder,
    find_template,
)

from .utils import http_request_to_str


# Pagination Strategies


class CursorBasedPaginationStrategy(PaginationStrategy):
    """Pagination strategy for cursor-based pagination with links.next.

    For links_next_paginator with page_token_option: RequestPath, the connector uses
    the full URL from links.next as the next request. The next_page_url should already
    include all necessary query parameters (including the cursor).

    Per playbook: The last page response must explicitly satisfy the stop_condition
    (meta.has_more = false) to verify pagination stops correctly.
    """

    def __init__(self, next_page_url: Optional[str] = None) -> None:
        self._next_page_url = next_page_url

    def update(self, response: Dict[str, Any]) -> None:
        # Set has_more based on whether there's a next page URL
        # This ensures the stop_condition (not response['meta']['has_more']) is properly verified
        response["meta"]["has_more"] = self._next_page_url is not None
        response["meta"]["after_cursor"] = "after-cursor"
        response["meta"]["before_cursor"] = "before-cursor"
        if self._next_page_url:
            response["links"]["next"] = self._next_page_url


class NextPagePaginationStrategy(PaginationStrategy):
    """Pagination strategy for next_page URL-based pagination."""

    def __init__(self, next_page_url: str) -> None:
        self._next_page_url = next_page_url

    def update(self, response: Dict[str, Any]) -> None:
        response["next_page"] = self._next_page_url


class EndOfStreamPaginationStrategy(PaginationStrategy):
    """Pagination strategy for end_of_stream-based pagination.

    Different streams use different paginators:
    - end_of_stream_paginator uses: cursor_value: '{{ response.get("next_page", {}) }}'
    - after_url_paginator uses: cursor_value: '{{ response.get("after_url") }}'

    Both use: stop_condition: '{{ response.get("end_of_stream") }}'

    We set both next_page and after_url to support both paginator types.
    """

    def __init__(self, url: str, cursor) -> None:
        self._next_page_url = url
        self._cursor = cursor

    def update(self, response: Dict[str, Any]) -> None:
        # Handle URLs that may already have query params
        if self._next_page_url and "?" in self._next_page_url:
            next_url = f"{self._next_page_url}&cursor={self._cursor}"
        else:
            next_url = f"{self._next_page_url}?cursor={self._cursor}"
        response["next_page"] = next_url
        response["after_url"] = next_url
        response["after_cursor"] = self._cursor
        response["end_of_stream"] = False


# Base Record Builder


class ZendeskSupportRecordBuilder(RecordBuilder):
    """Base record builder for Zendesk Support records."""

    @staticmethod
    def extract_record(resource: str, execution_folder: str, data_field: Path):
        return data_field.extract(find_template(resource=resource, execution_folder=execution_folder))


# Per-Stream Record Builders


class TagsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def tags_record(cls) -> "TagsRecordBuilder":
        record_template = cls.extract_record("tags", __file__, NestedPath(["tags", 0]))
        return cls(record_template, FieldPath("name"), None)

    def with_name(self, name: str) -> "TagsRecordBuilder":
        self._record["name"] = name
        return self


class BrandsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def brands_record(cls) -> "BrandsRecordBuilder":
        record_template = cls.extract_record("brands", __file__, NestedPath(["brands", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "BrandsRecordBuilder":
        self._record["id"] = id
        return self


class AutomationsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def automations_record(cls) -> "AutomationsRecordBuilder":
        record_template = cls.extract_record("automations", __file__, NestedPath(["automations", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "AutomationsRecordBuilder":
        self._record["id"] = id
        return self


class CustomRolesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def custom_roles_record(cls) -> "CustomRolesRecordBuilder":
        record_template = cls.extract_record("custom_roles", __file__, NestedPath(["custom_roles", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "CustomRolesRecordBuilder":
        self._record["id"] = id
        return self


class SchedulesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def schedules_record(cls) -> "SchedulesRecordBuilder":
        record_template = cls.extract_record("schedules", __file__, NestedPath(["schedules", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "SchedulesRecordBuilder":
        self._record["id"] = id
        return self


class SlaPoliciesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def sla_policies_record(cls) -> "SlaPoliciesRecordBuilder":
        record_template = cls.extract_record("sla_policies", __file__, NestedPath(["sla_policies", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "SlaPoliciesRecordBuilder":
        self._record["id"] = id
        return self

    def with_title(self, title: str) -> "SlaPoliciesRecordBuilder":
        self._record["title"] = title
        return self


class GroupsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def groups_record(cls) -> "GroupsRecordBuilder":
        record_template = cls.extract_record("groups", __file__, NestedPath(["groups", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "GroupsRecordBuilder":
        self._record["id"] = id
        return self


class UsersRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def users_record(cls) -> "UsersRecordBuilder":
        record_template = cls.extract_record("users", __file__, NestedPath(["users", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    @classmethod
    def record(cls) -> "UsersRecordBuilder":
        """Alias for users_record() for backward compatibility."""
        return cls.users_record()

    def with_id(self, id: int) -> "UsersRecordBuilder":
        self._record["id"] = id
        return self


class TicketMetricsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_metrics_record(cls) -> "TicketMetricsRecordBuilder":
        record_template = cls.extract_record("ticket_metrics", __file__, NestedPath(["ticket_metrics", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    @classmethod
    def stateless_ticket_metrics_record(cls) -> "TicketMetricsRecordBuilder":
        """Alias for ticket_metrics_record() for backward compatibility."""
        return cls.ticket_metrics_record()

    @classmethod
    def stateful_ticket_metrics_record(cls) -> "TicketMetricsRecordBuilder":
        """Record builder for stateful ticket metrics (single ticket metric)."""
        record_template = cls.extract_record("stateful_ticket_metrics", __file__, FieldPath("ticket_metric"))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketMetricsRecordBuilder":
        self._record["id"] = id
        return self


class TicketsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def tickets_record(cls) -> "TicketsRecordBuilder":
        record_template = cls.extract_record("tickets", __file__, NestedPath(["tickets", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketsRecordBuilder":
        self._record["id"] = id
        return self


class TicketFormsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_forms_record(cls) -> "TicketFormsRecordBuilder":
        record_template = cls.extract_record("ticket_forms", __file__, NestedPath(["ticket_forms", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketFormsRecordBuilder":
        self._record["id"] = id
        return self


class ArticlesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def articles_record(cls) -> "ArticlesRecordBuilder":
        record_template = cls.extract_record("articles", __file__, NestedPath(["articles", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    @classmethod
    def record(cls) -> "ArticlesRecordBuilder":
        """Alias for articles_record() for backward compatibility."""
        return cls.articles_record()

    def with_id(self, id: int) -> "ArticlesRecordBuilder":
        self._record["id"] = id
        return self


class PostsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def posts_record(cls) -> "PostsRecordBuilder":
        record_template = cls.extract_record("posts", __file__, NestedPath(["posts", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "PostsRecordBuilder":
        self._record["id"] = id
        return self


class PostCommentsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def post_comments_record(cls) -> "PostCommentsRecordBuilder":
        record_template = cls.extract_record("post_comments", __file__, NestedPath(["comments", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    @classmethod
    def posts_comments_record(cls) -> "PostCommentsRecordBuilder":
        """Alias for post_comments_record() for backward compatibility."""
        return cls.post_comments_record()

    def with_id(self, id: int) -> "PostCommentsRecordBuilder":
        self._record["id"] = id
        return self


class PostVotesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def post_votes_record(cls) -> "PostVotesRecordBuilder":
        record_template = cls.extract_record("post_votes", __file__, NestedPath(["votes", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    @classmethod
    def posts_votes_record(cls) -> "PostVotesRecordBuilder":
        """Alias for post_votes_record() for backward compatibility."""
        return cls.post_votes_record()

    def with_id(self, id: int) -> "PostVotesRecordBuilder":
        self._record["id"] = id
        return self


class PostCommentVotesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def post_comment_votes_record(cls) -> "PostCommentVotesRecordBuilder":
        record_template = cls.extract_record("post_comment_votes", __file__, NestedPath(["votes", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    @classmethod
    def post_commetn_votes_record(cls) -> "PostCommentVotesRecordBuilder":
        """Alias with typo for backward compatibility (original code had typo)."""
        return cls.post_comment_votes_record()

    def with_id(self, id: int) -> "PostCommentVotesRecordBuilder":
        self._record["id"] = id
        return self


# Error Response Builder


class ErrorResponseBuilder:
    """Builder for error responses.

    Per playbook: FAIL error handlers must assert both error code AND error message.
    Use with_error_message() to set a deterministic error message that can be asserted in tests.
    """

    def __init__(self, status_code: int):
        self._status_code: int = status_code
        self._error_message: Optional[str] = None

    @classmethod
    def response_with_status(cls, status_code: int) -> "ErrorResponseBuilder":
        return cls(status_code)

    def with_error_message(self, message: str) -> "ErrorResponseBuilder":
        """Set a custom error message for the response.

        For 403/404 errors, the manifest uses {{ response.get('error') }}.
        For 504 errors, the manifest uses {{ response.text }}.
        """
        self._error_message = message
        return self

    def build(self) -> HttpResponse:
        if self._error_message:
            body = json.dumps({"error": self._error_message})
        else:
            body = json.dumps({"error": f"Error {self._status_code}"})
        return HttpResponse(body, self._status_code)


# Response Builders for each stream


class TagsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def tags_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "TagsResponseBuilder":
        return cls(
            find_template("tags", __file__),
            FieldPath("tags"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class BrandsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def brands_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "BrandsResponseBuilder":
        return cls(
            find_template("brands", __file__),
            FieldPath("brands"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class AutomationsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def automations_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "AutomationsResponseBuilder":
        return cls(
            find_template("automations", __file__),
            FieldPath("automations"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class CustomRolesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def custom_roles_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "CustomRolesResponseBuilder":
        """Response builder for custom_roles stream with next_page pagination."""
        return cls(
            find_template("custom_roles", __file__),
            FieldPath("custom_roles"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class SchedulesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def schedules_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "SchedulesResponseBuilder":
        """Response builder for schedules stream with next_page pagination."""
        return cls(
            find_template("schedules", __file__),
            FieldPath("schedules"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class SlaPoliciesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def sla_policies_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "SlaPoliciesResponseBuilder":
        """Response builder for sla_policies stream with next_page pagination."""
        return cls(
            find_template("sla_policies", __file__),
            FieldPath("sla_policies"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class GroupsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def groups_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "GroupsResponseBuilder":
        """Response builder for groups stream.

        The groups stream uses the base retriever which has:
        - next_page field for pagination (not links.next)
        - per_page parameter (not page[size])
        - stop_condition: last_page_size == 0

        Args:
            request_without_cursor_for_pagination: HttpRequest for the next page. If None, indicates last page.
        """
        return cls(
            find_template("groups", __file__),
            FieldPath("groups"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class UsersResponseBuilder(HttpResponseBuilder):
    @classmethod
    def users_response(cls, url: Optional[HttpRequest] = None, cursor: Optional[str] = None) -> "UsersResponseBuilder":
        return cls(
            find_template("users", __file__),
            FieldPath("users"),
            EndOfStreamPaginationStrategy(http_request_to_str(url), cursor),
        )

    @classmethod
    def identities_response(cls, url: Optional[HttpRequest] = None, cursor: Optional[str] = None) -> "UsersResponseBuilder":
        return cls(
            find_template("users", __file__),
            FieldPath("identities"),
            EndOfStreamPaginationStrategy(http_request_to_str(url), cursor),
        )


class TicketMetricsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_metrics_response(cls, url: Optional[str] = None, cursor: Optional[str] = None) -> "TicketMetricsResponseBuilder":
        return cls(
            find_template("ticket_metrics", __file__),
            FieldPath("ticket_metrics"),
            EndOfStreamPaginationStrategy(url, cursor) if url and cursor else None,
        )

    @classmethod
    def stateless_ticket_metrics_response(cls) -> "TicketMetricsResponseBuilder":
        """Response builder for stateless ticket metrics (list of metrics)."""
        return cls(
            find_template("stateless_ticket_metrics", __file__),
            FieldPath("ticket_metrics"),
            CursorBasedPaginationStrategy(),
        )

    @classmethod
    def stateful_ticket_metrics_response(cls) -> "TicketMetricsResponseBuilder":
        """Response builder for stateful ticket metrics (single ticket metric)."""
        return cls(
            find_template("stateful_ticket_metrics", __file__),
            FieldPath("ticket_metric"),
            CursorBasedPaginationStrategy(),
        )


class TicketsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def tickets_response(cls, url: Optional[str] = None, cursor: Optional[str] = None) -> "TicketsResponseBuilder":
        return cls(
            find_template("tickets", __file__),
            FieldPath("tickets"),
            EndOfStreamPaginationStrategy(url, cursor) if url and cursor else None,
        )


class TicketFormsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_forms_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "TicketFormsResponseBuilder":
        return cls(
            find_template("ticket_forms", __file__),
            FieldPath("ticket_forms"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class ArticlesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def articles_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "ArticlesResponseBuilder":
        return cls(
            find_template("articles", __file__),
            FieldPath("articles"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )

    @classmethod
    def response(cls, next_page_url: Optional[HttpRequest] = None) -> "ArticlesResponseBuilder":
        """Alias for articles_response() for backward compatibility."""
        return cls.articles_response(next_page_url)


class PostsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def posts_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "PostsResponseBuilder":
        return cls(
            find_template("posts", __file__),
            FieldPath("posts"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class PostCommentsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def post_comments_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "PostCommentsResponseBuilder":
        return cls(
            find_template("post_comments", __file__),
            FieldPath("comments"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )

    @classmethod
    def posts_comments_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "PostCommentsResponseBuilder":
        """Alias for post_comments_response() for backward compatibility."""
        return cls.post_comments_response(request_without_cursor_for_pagination)


class PostVotesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def post_votes_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "PostVotesResponseBuilder":
        return cls(
            find_template("post_votes", __file__),
            FieldPath("votes"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )

    @classmethod
    def posts_votes_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "PostVotesResponseBuilder":
        """Alias for post_votes_response() for backward compatibility."""
        return cls.post_votes_response(request_without_cursor_for_pagination)


class PostCommentVotesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def post_comment_votes_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "PostCommentVotesResponseBuilder":
        return cls(
            find_template("post_comment_votes", __file__),
            FieldPath("votes"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


# Record Builders for new streams


class AccountAttributesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def account_attributes_record(cls) -> "AccountAttributesRecordBuilder":
        record_template = cls.extract_record("account_attributes", __file__, NestedPath(["attributes", 0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: str) -> "AccountAttributesRecordBuilder":
        self._record["id"] = id
        return self


class AttributeDefinitionsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def attribute_definitions_record(cls) -> "AttributeDefinitionsRecordBuilder":
        record_template = cls.extract_record("attribute_definitions", __file__, FieldPath("definitions"))
        return cls(record_template, None, None)


class UserFieldsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def user_fields_record(cls) -> "UserFieldsRecordBuilder":
        record_template = cls.extract_record("user_fields", __file__, NestedPath(["user_fields", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "UserFieldsRecordBuilder":
        self._record["id"] = id
        return self


class CategoriesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def categories_record(cls) -> "CategoriesRecordBuilder":
        record_template = cls.extract_record("categories", __file__, NestedPath(["categories", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "CategoriesRecordBuilder":
        self._record["id"] = id
        return self


class SectionsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def sections_record(cls) -> "SectionsRecordBuilder":
        record_template = cls.extract_record("sections", __file__, NestedPath(["sections", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "SectionsRecordBuilder":
        self._record["id"] = id
        return self


class TopicsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def topics_record(cls) -> "TopicsRecordBuilder":
        record_template = cls.extract_record("topics", __file__, NestedPath(["topics", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TopicsRecordBuilder":
        self._record["id"] = id
        return self


# Response Builders for new streams


class AccountAttributesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def account_attributes_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "AccountAttributesResponseBuilder":
        return cls(
            find_template("account_attributes", __file__),
            FieldPath("attributes"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class AttributeDefinitionsResponseBuilder(HttpResponseBuilder):
    """Custom response builder for attribute_definitions stream.

    This stream uses a custom extractor (ZendeskSupportAttributeDefinitionsExtractor) that expects
    a nested structure with definitions.conditions_all and definitions.conditions_any arrays.
    The standard HttpResponseBuilder.build() would replace the definitions field with an empty list,
    so we override build() to preserve the template structure.
    """

    @classmethod
    def attribute_definitions_response(cls) -> "AttributeDefinitionsResponseBuilder":
        return cls(
            find_template("attribute_definitions", __file__),
            FieldPath("definitions"),
            None,
        )

    def build(self) -> HttpResponse:
        # Override to preserve the nested structure - don't replace definitions with records list
        return HttpResponse(json.dumps(self._response), self._status_code)


class UserFieldsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def user_fields_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "UserFieldsResponseBuilder":
        return cls(
            find_template("user_fields", __file__),
            FieldPath("user_fields"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class CategoriesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def categories_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "CategoriesResponseBuilder":
        return cls(
            find_template("categories", __file__),
            FieldPath("categories"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class SectionsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def sections_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "SectionsResponseBuilder":
        return cls(
            find_template("sections", __file__),
            FieldPath("sections"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TopicsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def topics_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "TopicsResponseBuilder":
        return cls(
            find_template("topics", __file__),
            FieldPath("topics"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


# Record Builders for semi-incremental streams


class GroupMembershipsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def group_memberships_record(cls) -> "GroupMembershipsRecordBuilder":
        record_template = cls.extract_record("group_memberships", __file__, NestedPath(["group_memberships", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "GroupMembershipsRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "GroupMembershipsRecordBuilder":
        self._record["updated_at"] = cursor
        return self


class MacrosRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def macros_record(cls) -> "MacrosRecordBuilder":
        record_template = cls.extract_record("macros", __file__, NestedPath(["macros", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "MacrosRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "MacrosRecordBuilder":
        self._record["updated_at"] = cursor
        return self


class OrganizationFieldsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def organization_fields_record(cls) -> "OrganizationFieldsRecordBuilder":
        record_template = cls.extract_record("organization_fields", __file__, NestedPath(["organization_fields", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "OrganizationFieldsRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "OrganizationFieldsRecordBuilder":
        self._record["updated_at"] = cursor
        return self


class OrganizationMembershipsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def organization_memberships_record(cls) -> "OrganizationMembershipsRecordBuilder":
        record_template = cls.extract_record("organization_memberships", __file__, NestedPath(["organization_memberships", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "OrganizationMembershipsRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "OrganizationMembershipsRecordBuilder":
        self._record["updated_at"] = cursor
        return self


class TicketFieldsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_fields_record(cls) -> "TicketFieldsRecordBuilder":
        record_template = cls.extract_record("ticket_fields", __file__, NestedPath(["ticket_fields", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketFieldsRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "TicketFieldsRecordBuilder":
        self._record["updated_at"] = cursor
        return self


class TicketActivitiesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_activities_record(cls) -> "TicketActivitiesRecordBuilder":
        record_template = cls.extract_record("ticket_activities", __file__, NestedPath(["activities", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketActivitiesRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "TicketActivitiesRecordBuilder":
        self._record["updated_at"] = cursor
        return self


class TriggersRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def triggers_record(cls) -> "TriggersRecordBuilder":
        record_template = cls.extract_record("triggers", __file__, NestedPath(["triggers", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TriggersRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor: str) -> "TriggersRecordBuilder":
        self._record["updated_at"] = cursor
        return self


# Response Builders for semi-incremental streams


class GroupMembershipsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def group_memberships_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "GroupMembershipsResponseBuilder":
        return cls(
            find_template("group_memberships", __file__),
            FieldPath("group_memberships"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class MacrosResponseBuilder(HttpResponseBuilder):
    @classmethod
    def macros_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "MacrosResponseBuilder":
        return cls(
            find_template("macros", __file__),
            FieldPath("macros"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class OrganizationFieldsResponseBuilder(HttpResponseBuilder):
    """Response builder for organization_fields stream.

    This stream uses the base retriever with next_page pagination (not links.next).
    """

    @classmethod
    def organization_fields_response(cls, next_page_url: Optional[str] = None) -> "OrganizationFieldsResponseBuilder":
        return cls(
            find_template("organization_fields", __file__),
            FieldPath("organization_fields"),
            NextPagePaginationStrategy(next_page_url),
        )


class OrganizationMembershipsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def organization_memberships_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "OrganizationMembershipsResponseBuilder":
        return cls(
            find_template("organization_memberships", __file__),
            FieldPath("organization_memberships"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TicketFieldsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_fields_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "TicketFieldsResponseBuilder":
        return cls(
            find_template("ticket_fields", __file__),
            FieldPath("ticket_fields"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TicketActivitiesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_activities_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "TicketActivitiesResponseBuilder":
        return cls(
            find_template("ticket_activities", __file__),
            FieldPath("activities"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TriggersResponseBuilder(HttpResponseBuilder):
    """Response builder for triggers stream.

    This stream uses the base retriever with next_page pagination (not links.next).
    """

    @classmethod
    def triggers_response(cls, next_page_url: Optional[str] = None) -> "TriggersResponseBuilder":
        return cls(
            find_template("triggers", __file__),
            FieldPath("triggers"),
            NextPagePaginationStrategy(next_page_url),
        )


# Additional Record Builders for missing streams


class OrganizationsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def organizations_record(cls) -> "OrganizationsRecordBuilder":
        record_template = cls.extract_record("organizations", __file__, NestedPath(["organizations", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "OrganizationsRecordBuilder":
        self._record["id"] = id
        return self


class SatisfactionRatingsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def satisfaction_ratings_record(cls) -> "SatisfactionRatingsRecordBuilder":
        record_template = cls.extract_record("satisfaction_ratings", __file__, NestedPath(["satisfaction_ratings", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "SatisfactionRatingsRecordBuilder":
        self._record["id"] = id
        return self


class TicketAuditsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_audits_record(cls) -> "TicketAuditsRecordBuilder":
        record_template = cls.extract_record("ticket_audits", __file__, NestedPath(["audits", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("created_at"))

    def with_id(self, id: int) -> "TicketAuditsRecordBuilder":
        self._record["id"] = id
        return self


class TicketCommentsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_comments_record(cls) -> "TicketCommentsRecordBuilder":
        record_template = cls.extract_record("ticket_comments", __file__, NestedPath(["ticket_events", 0, "child_events", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketCommentsRecordBuilder":
        self._record["id"] = id
        return self


class TicketMetricEventsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_metric_events_record(cls) -> "TicketMetricEventsRecordBuilder":
        record_template = cls.extract_record("ticket_metric_events", __file__, NestedPath(["ticket_metric_events", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("time"))

    def with_id(self, id: int) -> "TicketMetricEventsRecordBuilder":
        self._record["id"] = id
        return self


class TicketSkipsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_skips_record(cls) -> "TicketSkipsRecordBuilder":
        record_template = cls.extract_record("ticket_skips", __file__, NestedPath(["skips", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "TicketSkipsRecordBuilder":
        self._record["id"] = id
        return self


class AuditLogsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def audit_logs_record(cls) -> "AuditLogsRecordBuilder":
        record_template = cls.extract_record("audit_logs", __file__, NestedPath(["audit_logs", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("created_at"))

    def with_id(self, id: int) -> "AuditLogsRecordBuilder":
        self._record["id"] = id
        return self


class ArticleCommentsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def article_comments_record(cls) -> "ArticleCommentsRecordBuilder":
        record_template = cls.extract_record("article_comments", __file__, NestedPath(["comments", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "ArticleCommentsRecordBuilder":
        self._record["id"] = id
        return self


class ArticleVotesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def article_votes_record(cls) -> "ArticleVotesRecordBuilder":
        record_template = cls.extract_record("article_votes", __file__, NestedPath(["votes", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "ArticleVotesRecordBuilder":
        self._record["id"] = id
        return self


class ArticleAttachmentsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def article_attachments_record(cls) -> "ArticleAttachmentsRecordBuilder":
        record_template = cls.extract_record("article_attachments", __file__, NestedPath(["article_attachments", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "ArticleAttachmentsRecordBuilder":
        self._record["id"] = id
        return self


class ArticleCommentVotesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def article_comment_votes_record(cls) -> "ArticleCommentVotesRecordBuilder":
        record_template = cls.extract_record("article_comment_votes", __file__, NestedPath(["votes", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "ArticleCommentVotesRecordBuilder":
        self._record["id"] = id
        return self


# Additional Response Builders for missing streams


class OrganizationsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def organizations_response(cls, url: Optional[str] = None, cursor: Optional[str] = None) -> "OrganizationsResponseBuilder":
        return cls(
            find_template("organizations", __file__),
            FieldPath("organizations"),
            EndOfStreamPaginationStrategy(url, cursor) if url and cursor else None,
        )


class SatisfactionRatingsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def satisfaction_ratings_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "SatisfactionRatingsResponseBuilder":
        return cls(
            find_template("satisfaction_ratings", __file__),
            FieldPath("satisfaction_ratings"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TicketAuditsResponseBuilder(HttpResponseBuilder):
    """Response builder for ticket_audits stream.

    Per manifest.yaml, ticket_audits uses CursorPagination with before_url as the cursor value.
    Use with_before_url() to set a next page URL for testing is_data_feed pagination stop behavior.
    """

    def __init__(self, template: Dict[str, Any], records_path: Path, pagination_strategy: Optional[PaginationStrategy]):
        super().__init__(template, records_path, pagination_strategy)
        self._before_url: Optional[str] = None

    @classmethod
    def ticket_audits_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "TicketAuditsResponseBuilder":
        return cls(
            find_template("ticket_audits", __file__),
            FieldPath("audits"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )

    def with_before_url(self, before_url: str) -> "TicketAuditsResponseBuilder":
        """Set the before_url to signal there's a next page.

        Per manifest.yaml, ticket_audits uses cursor_value: "{{ response.get('before_url') }}"
        Setting this signals to the connector that there's more data to fetch.
        For is_data_feed tests, set this but don't mock the next page - if the connector
        tries to fetch it, the test will fail due to an unmatched HTTP request.
        """
        self._before_url = before_url
        return self

    def build(self) -> HttpResponse:
        response = super().build()
        if self._before_url:
            body = json.loads(response.body)
            body["before_url"] = self._before_url
            return HttpResponse(json.dumps(body), response.status_code)
        return response


class TicketCommentsResponseBuilder(HttpResponseBuilder):
    """Custom response builder for ticket_comments stream.

    This stream uses a custom extractor (ZendeskSupportExtractorEvents) that expects
    a nested structure with ticket_events[].child_events[] where child_events have event_type="Comment".
    The standard HttpResponseBuilder.build() would replace the ticket_events field with an empty list,
    so we override build() to preserve the template structure.
    """

    @classmethod
    def ticket_comments_response(cls, url: Optional[str] = None, cursor: Optional[str] = None) -> "TicketCommentsResponseBuilder":
        return cls(
            find_template("ticket_comments", __file__),
            FieldPath("ticket_events"),
            EndOfStreamPaginationStrategy(url, cursor) if url and cursor else None,
        )

    def build(self) -> HttpResponse:
        # Override to preserve the nested structure - don't replace ticket_events with records list
        return HttpResponse(json.dumps(self._response), self._status_code)


class TicketMetricEventsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_metric_events_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "TicketMetricEventsResponseBuilder":
        return cls(
            find_template("ticket_metric_events", __file__),
            FieldPath("ticket_metric_events"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TicketSkipsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ticket_skips_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "TicketSkipsResponseBuilder":
        return cls(
            find_template("ticket_skips", __file__),
            FieldPath("skips"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class AuditLogsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def audit_logs_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "AuditLogsResponseBuilder":
        return cls(
            find_template("audit_logs", __file__),
            FieldPath("audit_logs"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class ArticleCommentsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def article_comments_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "ArticleCommentsResponseBuilder":
        return cls(
            find_template("article_comments", __file__),
            FieldPath("comments"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class ArticleVotesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def article_votes_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "ArticleVotesResponseBuilder":
        return cls(
            find_template("article_votes", __file__),
            FieldPath("votes"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class ArticleAttachmentsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def article_attachments_response(cls) -> "ArticleAttachmentsResponseBuilder":
        return cls(
            find_template("article_attachments", __file__),
            FieldPath("article_attachments"),
            None,
        )


class ArticleCommentVotesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def article_comment_votes_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "ArticleCommentVotesResponseBuilder":
        return cls(
            find_template("article_comment_votes", __file__),
            FieldPath("votes"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class UserIdentitiesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def user_identities_record(cls) -> "UserIdentitiesRecordBuilder":
        record_template = cls.extract_record("user_identities", __file__, NestedPath(["identities", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "UserIdentitiesRecordBuilder":
        self._record["id"] = id
        return self


class UserIdentitiesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def user_identities_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "UserIdentitiesResponseBuilder":
        return cls(
            find_template("user_identities", __file__),
            FieldPath("identities"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )
