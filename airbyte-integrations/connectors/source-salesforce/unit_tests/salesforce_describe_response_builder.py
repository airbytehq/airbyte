# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Optional

from airbyte_cdk.test.mock_http import HttpResponse


class SalesforceDescribeResponseBuilder:
    def __init__(self) -> None:
        self._fields = []

    def field(self, name: str, _type: Optional[str] = None) -> "SalesforceDescribeResponseBuilder":
        self._fields.append({"name": name, "type": _type if _type else "string"})
        return self

    def build(self) -> HttpResponse:
        return HttpResponse(json.dumps({"fields": self._fields}))
