#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#


import json
from http import HTTPStatus
from typing import Any, Mapping

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def response_with_status(status_code: HTTPStatus) -> HttpResponse:
    return HttpResponse(json.dumps(find_template(str(status_code), __file__)), status_code)


def build_response(body: Mapping[str, Any], status_code: HTTPStatus) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)
