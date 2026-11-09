# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

from airbyte_cdk.test.mock_http import HttpResponse

from .request_builder import RequestBuilder


class ResponseBuilder:
    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._next: str | None = None
        self._has_more = False

    def with_records(self, *records: dict[str, Any]) -> "ResponseBuilder":
        self._records.extend(records)
        return self

    def with_next_page(self, request: RequestBuilder) -> "ResponseBuilder":
        self._next = request.url
        self._has_more = True
        return self

    def with_has_more(self, value: bool) -> "ResponseBuilder":
        self._has_more = value
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps({"data": self._records, "next": self._next, "has_more": self._has_more}), status_code=200)

    @staticmethod
    def singleton(record: dict[str, Any]) -> HttpResponse:
        return HttpResponse(json.dumps(record), status_code=200)
