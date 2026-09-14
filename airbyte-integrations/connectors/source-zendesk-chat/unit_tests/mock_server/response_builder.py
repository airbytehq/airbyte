# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

"""
Response builder for Zendesk Chat API responses.

This module provides response builders for creating mock HTTP responses
for tests, including pagination strategies and error responses.

Example usage:
    response = (
        AgentsResponseBuilder.agents_response()
        .with_record(AgentsRecordBuilder.agents_record().with_id(1001))
        .build()
    )
"""

import json
from typing import Any, Dict, List, Optional

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


class SinceIdPaginationStrategy(PaginationStrategy):
    """Pagination strategy for since_id-based pagination (agents, bans)."""

    def __init__(self, next_since_id: Optional[int] = None) -> None:
        self._next_since_id = next_since_id

    def update(self, response: Dict[str, Any]) -> None:
        pass


class NextPagePaginationStrategy(PaginationStrategy):
    """Pagination strategy for next_page URL-based pagination (chats, agent_timeline)."""

    def __init__(self, next_page_url: Optional[str] = None) -> None:
        self._next_page_url = next_page_url

    def update(self, response: Dict[str, Any]) -> None:
        if self._next_page_url:
            response["next_page"] = self._next_page_url


class ZendeskChatRecordBuilder(RecordBuilder):
    """Base record builder for Zendesk Chat records."""

    @staticmethod
    def extract_record(resource: str, execution_folder: str, data_field: Path):
        return data_field.extract(find_template(resource=resource, execution_folder=execution_folder))


class AccountsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def accounts_record(cls) -> "AccountsRecordBuilder":
        record_template = find_template("accounts", __file__)
        return cls(record_template, FieldPath("account_key"), None)

    def with_account_key(self, account_key: str) -> "AccountsRecordBuilder":
        self._record["account_key"] = account_key
        return self


class AgentsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def agents_record(cls) -> "AgentsRecordBuilder":
        record_template = cls.extract_record("agents", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "AgentsRecordBuilder":
        self._record["id"] = id
        return self

    def with_cursor(self, cursor_value: str) -> "AgentsRecordBuilder":
        return self


class AgentTimelineRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def agent_timeline_record(cls) -> "AgentTimelineRecordBuilder":
        record_template = cls.extract_record("agent_timeline", __file__, NestedPath(["agent_timeline", 0]))
        return cls(record_template, FieldPath("agent_id"), FieldPath("start_time"))

    def with_agent_id(self, agent_id: int) -> "AgentTimelineRecordBuilder":
        self._record["agent_id"] = agent_id
        return self

    def with_start_time(self, start_time: int) -> "AgentTimelineRecordBuilder":
        self._record["start_time"] = start_time
        return self


class BansRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def ip_address_ban_record(cls) -> "BansRecordBuilder":
        record_template = cls.extract_record("bans", __file__, NestedPath(["ip_address", 0]))
        return cls(record_template, FieldPath("id"), None)

    @classmethod
    def visitor_ban_record(cls) -> "BansRecordBuilder":
        record_template = cls.extract_record("bans", __file__, NestedPath(["visitor", 0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "BansRecordBuilder":
        self._record["id"] = id
        return self


class ChatsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def chats_record(cls) -> "ChatsRecordBuilder":
        record_template = cls.extract_record("chats", __file__, NestedPath(["chats", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("update_timestamp"))

    def with_id(self, id: str) -> "ChatsRecordBuilder":
        self._record["id"] = id
        return self

    def with_update_timestamp(self, timestamp: str) -> "ChatsRecordBuilder":
        self._record["update_timestamp"] = timestamp
        return self


class DepartmentsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def departments_record(cls) -> "DepartmentsRecordBuilder":
        record_template = cls.extract_record("departments", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "DepartmentsRecordBuilder":
        self._record["id"] = id
        return self


class GoalsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def goals_record(cls) -> "GoalsRecordBuilder":
        record_template = cls.extract_record("goals", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "GoalsRecordBuilder":
        self._record["id"] = id
        return self


class RolesRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def roles_record(cls) -> "RolesRecordBuilder":
        record_template = cls.extract_record("roles", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "RolesRecordBuilder":
        self._record["id"] = id
        return self


class RoutingSettingsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def routing_settings_record(cls) -> "RoutingSettingsRecordBuilder":
        record_template = cls.extract_record("routing_settings", __file__, NestedPath(["data"]))
        return cls(record_template, FieldPath("enabled"), None)


class ShortcutsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def shortcuts_record(cls) -> "ShortcutsRecordBuilder":
        record_template = cls.extract_record("shortcuts", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "ShortcutsRecordBuilder":
        self._record["id"] = id
        return self


class SkillsRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def skills_record(cls) -> "SkillsRecordBuilder":
        record_template = cls.extract_record("skills", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "SkillsRecordBuilder":
        self._record["id"] = id
        return self


class TriggersRecordBuilder(ZendeskChatRecordBuilder):
    @classmethod
    def triggers_record(cls) -> "TriggersRecordBuilder":
        record_template = cls.extract_record("triggers", __file__, NestedPath([0]))
        return cls(record_template, FieldPath("id"), None)

    def with_id(self, id: int) -> "TriggersRecordBuilder":
        self._record["id"] = id
        return self


class ErrorResponseBuilder:
    """Builder for error responses."""

    def __init__(self, status_code: int):
        self._status_code: int = status_code
        self._error_message: Optional[str] = None

    @classmethod
    def response_with_status(cls, status_code: int) -> "ErrorResponseBuilder":
        return cls(status_code)

    def with_error_message(self, message: str) -> "ErrorResponseBuilder":
        self._error_message = message
        return self

    def build(self) -> HttpResponse:
        if self._error_message:
            body = json.dumps({"error": self._error_message})
        else:
            body = json.dumps({"error": f"Error {self._status_code}"})
        return HttpResponse(body, self._status_code)


class AccountsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def accounts_response(cls) -> "AccountsResponseBuilder":
        return cls(find_template("accounts", __file__), FieldPath("account_key"), None)


class AgentsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def agents_response(cls) -> "AgentsResponseBuilder":
        return cls(find_template("agents", __file__), FieldPath("id"), SinceIdPaginationStrategy())


class AgentTimelineResponseBuilder(HttpResponseBuilder):
    @classmethod
    def agent_timeline_response(cls, next_page_url: Optional[str] = None) -> "AgentTimelineResponseBuilder":
        return cls(
            find_template("agent_timeline", __file__),
            NestedPath(["agent_timeline"]),
            NextPagePaginationStrategy(next_page_url),
        )


class BansResponseBuilder(HttpResponseBuilder):
    @classmethod
    def bans_response(cls) -> "BansResponseBuilder":
        return cls(find_template("bans", __file__), FieldPath("ip_address"), SinceIdPaginationStrategy())


class ChatsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def chats_response(cls, next_page_url: Optional[str] = None) -> "ChatsResponseBuilder":
        return cls(
            find_template("chats", __file__),
            NestedPath(["chats"]),
            NextPagePaginationStrategy(next_page_url),
        )


class DepartmentsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def departments_response(cls) -> "DepartmentsResponseBuilder":
        return cls(find_template("departments", __file__), FieldPath("id"), None)


class GoalsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def goals_response(cls) -> "GoalsResponseBuilder":
        return cls(find_template("goals", __file__), FieldPath("id"), None)


class RolesResponseBuilder(HttpResponseBuilder):
    @classmethod
    def roles_response(cls) -> "RolesResponseBuilder":
        return cls(find_template("roles", __file__), FieldPath("id"), None)


class RoutingSettingsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def routing_settings_response(cls) -> "RoutingSettingsResponseBuilder":
        return cls(find_template("routing_settings", __file__), NestedPath(["data"]), None)


class ShortcutsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def shortcuts_response(cls) -> "ShortcutsResponseBuilder":
        return cls(find_template("shortcuts", __file__), FieldPath("id"), None)


class SkillsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def skills_response(cls) -> "SkillsResponseBuilder":
        return cls(find_template("skills", __file__), FieldPath("id"), None)


class TriggersResponseBuilder(HttpResponseBuilder):
    @classmethod
    def triggers_response(cls) -> "TriggersResponseBuilder":
        return cls(find_template("triggers", __file__), FieldPath("id"), None)


class ZendeskChatResponseBuilder:
    """
    Legacy builder for creating Zendesk Chat API responses.
    Kept for backward compatibility with existing tests.
    """

    def __init__(self, entry_field: Optional[str] = None):
        self._entry_field = entry_field
        self._records: List[Dict[str, Any]] = []
        self._count: Optional[int] = None
        self._next_page: Optional[str] = None
        self._single_record: Optional[Dict[str, Any]] = None
        self._data_wrapper: bool = False

    def with_record(self, record: Dict[str, Any]) -> "ZendeskChatResponseBuilder":
        self._records.append(record)
        return self

    def with_records(self, records: List[Dict[str, Any]]) -> "ZendeskChatResponseBuilder":
        self._records.extend(records)
        return self

    def with_single_record(self, record: Dict[str, Any]) -> "ZendeskChatResponseBuilder":
        self._single_record = record
        return self

    def with_count(self, count: int) -> "ZendeskChatResponseBuilder":
        self._count = count
        return self

    def with_next_page(self, next_page_url: str) -> "ZendeskChatResponseBuilder":
        self._next_page = next_page_url
        return self

    def with_data_wrapper(self) -> "ZendeskChatResponseBuilder":
        self._data_wrapper = True
        return self

    def build(self) -> HttpResponse:
        if self._single_record is not None:
            body = self._single_record
        elif self._data_wrapper:
            body = {"data": self._records}
        elif self._entry_field:
            body = {
                self._entry_field: self._records,
                "count": self._count if self._count is not None else len(self._records),
            }
            if self._next_page:
                body["next_page"] = self._next_page
        else:
            body = self._records

        return HttpResponse(body=json.dumps(body), status_code=200)

    @classmethod
    def array_response(cls, records: List[Dict[str, Any]]) -> HttpResponse:
        return cls().with_records(records).build()

    @classmethod
    def object_response(cls, record: Dict[str, Any]) -> HttpResponse:
        return cls().with_single_record(record).build()

    @classmethod
    def paginated_response(
        cls,
        entry_field: str,
        records: List[Dict[str, Any]],
        count: Optional[int] = None,
        next_page: Optional[str] = None,
    ) -> HttpResponse:
        builder = cls(entry_field).with_records(records)
        if count is not None:
            builder.with_count(count)
        if next_page:
            builder.with_next_page(next_page)
        return builder.build()

    @classmethod
    def error_response(cls, status_code: int, error_message: str) -> HttpResponse:
        return HttpResponse(
            body=json.dumps({"error": {"message": error_message}}),
            status_code=status_code,
        )
