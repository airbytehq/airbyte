# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

from airbyte_cdk.test.mock_http import HttpResponse


class DatadogPaginatedResponseBuilder:
    """Builds one page of a list endpoint: the records under their field, and `meta` when the test sets it."""

    def __init__(self, records_field: str) -> None:
        self._records_field = records_field
        self._body: dict[str, Any] = {records_field: []}

    def with_records(self, records: list[dict[str, Any]]) -> "DatadogPaginatedResponseBuilder":
        self._body[self._records_field] = records
        return self

    def with_meta(self, meta: dict[str, Any] | None) -> "DatadogPaginatedResponseBuilder":
        self._body["meta"] = meta
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(body=json.dumps(self._body), status_code=200)
