# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Dict, Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import RecordBuilder


class ObjectResponseBuilder:
    """
    Builds a response whose whole body is a single record. The CDK's HttpResponseBuilder only places records under a
    field (FieldPath/NestedPath) or at the root of a list (RootPath), so it can't express these bodies.
    """

    def __init__(self) -> None:
        self._record: Optional[RecordBuilder] = None
        self._status_code = 200
        self._headers: Dict[str, str] = {}

    def with_record(self, record: RecordBuilder) -> "ObjectResponseBuilder":
        self._record = record
        return self

    def with_status_code(self, status_code: int) -> "ObjectResponseBuilder":
        self._status_code = status_code
        return self

    def with_headers(self, headers: Dict[str, str]) -> "ObjectResponseBuilder":
        self._headers = headers
        return self

    def build(self) -> HttpResponse:
        if self._record is None:
            raise ValueError("A record is required to build an object response")
        return HttpResponse(json.dumps(self._record.build()), self._status_code, self._headers)
