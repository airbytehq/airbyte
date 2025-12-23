# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse


class ZendeskChatResponseBuilder:
    """
    Builder for creating Zendesk Chat API responses.

    Supports different response shapes:
    - Array responses (agents, departments, goals, roles, shortcuts, skills, triggers)
    - Object responses (accounts, routing_settings)
    - Paginated responses with next_page (chats, agent_timeline)
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
