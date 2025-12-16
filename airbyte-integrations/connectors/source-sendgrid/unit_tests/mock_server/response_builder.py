#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import abc
import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import PaginationStrategy


class AbstractResponseBuilder(abc.ABC):
    @abc.abstractmethod
    def build(self) -> HttpResponse:
        pass


class SendGridOffsetPaginationStrategy(PaginationStrategy):
    """Pagination strategy for SendGrid offset-based pagination (bounces, blocks, etc.)."""

    def __init__(self, page_size: int = 500):
        self._page_size = page_size

    def update(self, response: Dict[str, Any]) -> None:
        pass


class SendGridCursorPaginationStrategy(PaginationStrategy):
    """Pagination strategy for SendGrid cursor-based pagination (lists, singlesends, etc.)."""

    NEXT_PAGE_URL = "https://api.sendgrid.com/v3/marketing/lists?page_token=next_token&page_size=1000"

    def __init__(self, next_url: str = None):
        self._next_url = next_url or self.NEXT_PAGE_URL

    def update(self, response: Dict[str, Any]) -> None:
        response["_metadata"] = {"next": self._next_url}


def _load_template(stream_name: str) -> Dict[str, Any]:
    """Load a JSON response template from the resource directory."""
    response_path = Path(__file__).parent.parent / "resource" / "http" / "response" / f"{stream_name}.json"
    return json.loads(response_path.read_text())


class SendGridResponseBuilder(AbstractResponseBuilder):
    """Generic response builder for SendGrid streams."""

    def __init__(self, records: List[Dict[str, Any]], records_path: Optional[str] = None):
        self._records = records
        self._records_path = records_path
        self._metadata: Dict[str, Any] = {}

    def with_pagination(self, next_url: str) -> "SendGridResponseBuilder":
        self._metadata["next"] = next_url
        return self

    def build(self) -> HttpResponse:
        if self._records_path:
            body = {self._records_path: self._records, "_metadata": self._metadata}
        else:
            body = self._records
        return HttpResponse(body=json.dumps(body), status_code=200)


class OffsetPaginatedResponseBuilder(AbstractResponseBuilder):
    """Response builder for offset-paginated streams (bounces, blocks, spam_reports, etc.)."""

    def __init__(self, stream_name: str):
        self._stream_name = stream_name
        self._template = _load_template(stream_name)
        self._records: List[Dict[str, Any]] = []

    def with_record(self, record: Dict[str, Any]) -> "OffsetPaginatedResponseBuilder":
        self._records.append(record)
        return self

    def with_records(self, records: List[Dict[str, Any]]) -> "OffsetPaginatedResponseBuilder":
        self._records.extend(records)
        return self

    def with_template_record(self) -> "OffsetPaginatedResponseBuilder":
        if isinstance(self._template, list) and len(self._template) > 0:
            self._records.append(copy.deepcopy(self._template[0]))
        return self

    def with_template_records(self, count: int) -> "OffsetPaginatedResponseBuilder":
        if isinstance(self._template, list) and len(self._template) > 0:
            for _ in range(count):
                self._records.append(copy.deepcopy(self._template[0]))
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(body=json.dumps(self._records), status_code=200)


class CursorPaginatedResponseBuilder(AbstractResponseBuilder):
    """Response builder for cursor-paginated streams (lists, singlesends, templates, etc.)."""

    def __init__(self, stream_name: str, records_path: str = "result"):
        self._stream_name = stream_name
        self._records_path = records_path
        self._template = _load_template(stream_name)
        self._records: List[Dict[str, Any]] = []
        self._next_url: Optional[str] = None

    def with_record(self, record: Dict[str, Any]) -> "CursorPaginatedResponseBuilder":
        self._records.append(record)
        return self

    def with_records(self, records: List[Dict[str, Any]]) -> "CursorPaginatedResponseBuilder":
        self._records.extend(records)
        return self

    def with_template_record(self) -> "CursorPaginatedResponseBuilder":
        if isinstance(self._template, dict) and self._records_path in self._template:
            records = self._template[self._records_path]
            if isinstance(records, list) and len(records) > 0:
                self._records.append(copy.deepcopy(records[0]))
        return self

    def with_template_records(self, count: int) -> "CursorPaginatedResponseBuilder":
        if isinstance(self._template, dict) and self._records_path in self._template:
            records = self._template[self._records_path]
            if isinstance(records, list) and len(records) > 0:
                for _ in range(count):
                    self._records.append(copy.deepcopy(records[0]))
        return self

    def with_pagination(self, next_url: str) -> "CursorPaginatedResponseBuilder":
        self._next_url = next_url
        return self

    def build(self) -> HttpResponse:
        metadata = {"next": self._next_url} if self._next_url else {}
        body = {self._records_path: self._records, "_metadata": metadata}
        return HttpResponse(body=json.dumps(body), status_code=200)


class EmptyResponseBuilder(AbstractResponseBuilder):
    """Response builder for empty responses."""

    def __init__(self, is_array: bool = True, records_path: Optional[str] = None):
        self._is_array = is_array
        self._records_path = records_path

    def build(self) -> HttpResponse:
        if self._records_path:
            body = {self._records_path: [], "_metadata": {}}
        elif self._is_array:
            body = []
        else:
            body = {}
        return HttpResponse(body=json.dumps(body), status_code=200)


class ErrorResponseBuilder(AbstractResponseBuilder):
    """Response builder for error responses."""

    def __init__(self, status_code: int = 500, error_message: str = "Internal Server Error"):
        self._status_code = status_code
        self._error_message = error_message

    def build(self) -> HttpResponse:
        body = {"errors": [{"message": self._error_message}]}
        return HttpResponse(body=json.dumps(body), status_code=self._status_code)
