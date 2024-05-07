# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import FieldPath, HttpResponseBuilder, PaginationStrategy, find_template

from . import AbstractResponseBuilder


class HubspotStreamResponseBuilder(HttpResponseBuilder):
    @property
    def pagination_strategy(self):
        return self._pagination_strategy

    @classmethod
    def for_stream(cls, stream: str, records_path: str, pagination_strategy: PaginationStrategy):
        return cls(find_template(stream, __file__), FieldPath(records_path), pagination_strategy)


class GenericResponseBuilder(AbstractResponseBuilder):
    def __init__(self):
        self._body = {}

    def with_value(self, key: str, value: str):
        self._body[key] = value
        return self

    def build(self):
        body = json.dumps(self._body)
        return HttpResponse(body, status_code=200)
