# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import Any, List, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, NestedPath, PaginationStrategy, RecordBuilder


class RootHttpResponseBuilder(HttpResponseBuilder):
    def __init__(
        self,
        template: List[Any],
        records_path: Optional[Union[FieldPath, NestedPath]] = None,
        pagination_strategy: Optional[PaginationStrategy] = None
    ):
        self._response = template
        self._records: List[RecordBuilder] = []
        self._records_path = records_path
        self._pagination_strategy = pagination_strategy
        self._status_code = 200

    def build(self) -> HttpResponse:
        self._response.extend([record.build() for record in self._records])
        return HttpResponse(json.dumps(self._response), self._status_code)
