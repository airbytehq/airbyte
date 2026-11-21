# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


class SalesloftResponseBuilder:
    def __init__(self) -> None:
        self._records = []
        self._next_page = None

    def with_records(self, records: list[dict]) -> "SalesloftResponseBuilder":
        self._records = records
        return self

    def with_next_page(self, page: int) -> "SalesloftResponseBuilder":
        self._next_page = page
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(body=json.dumps({"data": self._records, "metadata": {"paging": {"next_page": self._next_page}}}))
