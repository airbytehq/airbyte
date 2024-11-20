# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, RecordBuilder, find_template

from .records.fields import DictTemplatePath


class ReportInitResponseBuilder(HttpResponseBuilder):
    @classmethod
    def report_init_response(cls) -> "ReportInitResponseBuilder":
        return cls(find_template("report_init_response", __file__), DictTemplatePath(), None)

    def with_record(self, record: RecordBuilder) -> HttpResponseBuilder:
        self._records = record
        return self

    def build(self) -> HttpResponse:
        self._records_path.update(self._response, self._records.build())
        return HttpResponse(json.dumps(self._response), self._status_code)
