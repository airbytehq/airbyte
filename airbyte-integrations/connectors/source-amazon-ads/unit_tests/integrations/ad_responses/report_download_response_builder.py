# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import gzip
import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, find_template

from .records.fields import ListTemplatePath


class ReportDownloadResponseBuilder(HttpResponseBuilder):
    @classmethod
    def download_report(cls) -> "ReportDownloadResponseBuilder":
        return cls(find_template("download_report_file", __file__), ListTemplatePath(), None)

    def build(self) -> HttpResponse:
        http_response = super().build()
        http_response._body = gzip.compress(http_response._body.encode("iso-8859-1"))
        return http_response
