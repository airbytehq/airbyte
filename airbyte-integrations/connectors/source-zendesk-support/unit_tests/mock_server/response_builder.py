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
    """

    def __init__(self, next_page_url: Optional[str] = None) -> None:
        self._next_page_url = next_page_url

    def update(self, response: Dict[str, Any]) -> None:
        response["meta"]["has_more"] = True
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
    """Pagination strategy for end_of_stream-based pagination."""

    def __init__(self, url: str, cursor) -> None:
        self._next_page_url = url
        self._cursor = cursor

    def update(self, response: Dict[str, Any]) -> None:
        response["after_url"] = f"{self._next_page_url}?cursor={self._cursor}"
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
    """Builder for error responses."""

    def __init__(self, status_code: int):
        self._status_code: int = status_code

    @classmethod
    def response_with_status(cls, status_code) -> "ErrorResponseBuilder":
        return cls(status_code)

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps(find_template(str(self._status_code), __file__)), self._status_code)


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
    @classmethod
    def attribute_definitions_response(cls) -> "AttributeDefinitionsResponseBuilder":
        return cls(
            find_template("attribute_definitions", __file__),
            FieldPath("definitions"),
            None,
        )


class UserFieldsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def user_fields_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "UserFieldsResponseBuilder":
        return cls(
            find_template("user_fields", __file__),
            FieldPath("user_fields"),
            NextPagePaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class CategoriesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def categories_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "CategoriesResponseBuilder":
        return cls(
            find_template("categories", __file__),
            FieldPath("categories"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class SectionsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def sections_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "SectionsResponseBuilder":
        return cls(
            find_template("sections", __file__),
            FieldPath("sections"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )


class TopicsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def topics_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "TopicsResponseBuilder":
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
    def macros_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "MacrosResponseBuilder":
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
    def organization_fields_response(
        cls, next_page_url: Optional[str] = None
    ) -> "OrganizationFieldsResponseBuilder":
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
    def ticket_fields_response(
        cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None
    ) -> "TicketFieldsResponseBuilder":
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
