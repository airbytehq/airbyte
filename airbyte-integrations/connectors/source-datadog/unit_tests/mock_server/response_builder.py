# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from collections.abc import Mapping
from typing import Any

from airbyte_cdk.test.mock_http import HttpResponse


# Error bodies that are not in the shape of Datadog's `APIErrorResponse`, by test id.
UNEXPECTED_ERROR_BODIES = {
    "not-json": "<html>Forbidden</html>",
    "json-not-an-object": json.dumps(["Forbidden"]),
    "no-errors": json.dumps({"message": "Forbidden"}),
    "errors-not-strings": json.dumps({"errors": [{"detail": "Forbidden"}, 403, None]}),
    "errors-not-a-list": json.dumps({"errors": 403}),
}


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


def datadog_error(status_code: int, errors: list[str], headers: Mapping[str, str] | None = None) -> HttpResponse:
    """Builds an error answer in the shape of Datadog's `APIErrorResponse`."""
    return HttpResponse(body=json.dumps({"errors": errors}), status_code=status_code, headers=headers or {})
