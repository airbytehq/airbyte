# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


class ErrorResponseBuilder:
    def __init__(self, status_code: int):
        self._status_code: int = status_code

    @classmethod
    def response_with_status(cls, status_code) -> "ErrorResponseBuilder":
        return cls(status_code)

    def build(self, file_path: Optional[str] = None) -> HttpResponse:
        if not file_path:
            return HttpResponse(json.dumps(find_template(str(self._status_code), __file__)), self._status_code)
        return HttpResponse(json.dumps(find_template(str(file_path), __file__)), self._status_code)

