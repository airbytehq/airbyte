import json
from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, find_template, FieldPath
from airbyte_cdk.test.mock_http import HttpResponse
from . import AbstractResponseBuilder
from .pagination import WebAnalyticsPaginationStrategy


class WebAnalyticsResponseBuilder(HttpResponseBuilder):
    @property
    def pagination_strategy(self):
        return self._pagination_strategy

    @classmethod
    def for_stream(cls, stream: str):
        return cls(find_template(stream, __file__), FieldPath("results"), WebAnalyticsPaginationStrategy())


class GenericAbstractResponseBuilder(AbstractResponseBuilder):
    def __init__(self):
        self._body = {}

    def with_value(self, key: str, value: str):
        self._body[key] = value
        return self

    def build(self):
        body = json.dumps(self._body)
        return HttpResponse(body, status_code=200)
