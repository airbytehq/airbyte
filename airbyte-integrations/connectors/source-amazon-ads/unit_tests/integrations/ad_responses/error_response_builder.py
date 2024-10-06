# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, Optional, Union

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import (
    FieldPath,
    HttpResponseBuilder,
    NestedPath,
    PaginationStrategy,
    RecordBuilder,
    find_template,
)

from .records.fields import DictTemplatePath


class ErrorResponseBuilder(HttpResponseBuilder):
    def __init__(self, template: Dict[str, Any], records_path: Union[FieldPath, NestedPath], pagination_strategy: Union[PaginationStrategy, None]):
        super().__init__(template, records_path, pagination_strategy)
        self._records: Dict[str, Any] = {}

    @classmethod
    def non_breaking_error_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "ErrorResponseBuilder":
        return cls(find_template("non_breaking_error", __file__), DictTemplatePath(), pagination_strategy)

    @classmethod
    def breaking_error_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "ErrorResponseBuilder":
        return cls(find_template("error", __file__), DictTemplatePath(), pagination_strategy)

    def with_record(self, record: RecordBuilder) -> HttpResponseBuilder:
        self._records = record
        return self

    def build(self) -> HttpResponse:
        self._records_path.update(self._response, self._records.build())
        return HttpResponse(json.dumps(self._response), self._status_code)
