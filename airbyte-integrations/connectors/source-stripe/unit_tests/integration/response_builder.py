# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


def a_response_with_status(status_code: int) -> HttpResponse:
    return HttpResponse(json.dumps(find_template(str(status_code), __file__)), status_code)
