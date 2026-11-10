# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


class BrevoResponseBuilder:
    def __init__(self, field: str | None) -> None:
        self._field = field
        self._records: list[dict] | dict = []

    def with_records(self, records: list[dict] | dict) -> "BrevoResponseBuilder":
        self._records = records
        return self

    def build(self) -> HttpResponse:
        body = {self._field: self._records} if self._field else self._records
        return HttpResponse(body=json.dumps(body), status_code=200)
