# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


class WaiteraidResponseBuilder:
    def __init__(self) -> None:
        self._records = []

    def with_records(self, records: list[dict]) -> "WaiteraidResponseBuilder":
        self._records = records
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(body=json.dumps({"status": "OK", "bookings": self._records}), status_code=200)
