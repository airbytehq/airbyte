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
    """Pagination strategy for cursor-based pagination with links.next."""

    def __init__(self, first_url: Optional[str] = None) -> None:
        self._first_url = first_url

    def update(self, response: Dict[str, Any]) -> None:
        response["meta"]["has_more"] = True
        response["meta"]["after_cursor"] = "after-cursor"
        response["meta"]["before_cursor"] = "before-cursor"
        if self._first_url:
            response["links"]["next"] = (
                self._first_url + "&page[after]=after-cursor" if "?" in self._first_url else self._first_url + "?page[after]=after-cursor"
            )


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
    def custom_roles_response(cls, next_page_url: Optional[str] = None) -> "CustomRolesResponseBuilder":
        return cls(
            find_template("custom_roles", __file__),
            FieldPath("custom_roles"),
            NextPagePaginationStrategy(next_page_url) if next_page_url else None,
        )


class SchedulesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def schedules_response(cls, next_page_url: Optional[str] = None) -> "SchedulesResponseBuilder":
        return cls(
            find_template("schedules", __file__),
            FieldPath("schedules"),
            NextPagePaginationStrategy(next_page_url) if next_page_url else None,
        )


class SlaPoliciesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def sla_policies_response(cls, next_page_url: Optional[str] = None) -> "SlaPoliciesResponseBuilder":
        return cls(
            find_template("sla_policies", __file__),
            FieldPath("sla_policies"),
            NextPagePaginationStrategy(next_page_url) if next_page_url else None,
        )


class GroupsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def groups_response(cls, request_without_cursor_for_pagination: Optional[HttpRequest] = None) -> "GroupsResponseBuilder":
        return cls(
            find_template("groups", __file__),
            FieldPath("groups"),
            CursorBasedPaginationStrategy(http_request_to_str(request_without_cursor_for_pagination)),
        )

    @classmethod
    def groups_response_with_pagination(cls, next_page_url: Optional[str] = None) -> "GroupsResponseBuilder":
        """Response builder for groups with explicit pagination control.

        Args:
            next_page_url: URL for the next page. If None, indicates last page (no more pages).
        """
        return cls(
            find_template("groups", __file__),
            FieldPath("groups"),
            CursorBasedPaginationStrategy(next_page_url) if next_page_url else None,
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
