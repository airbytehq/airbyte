# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


def data_response(records):
    return HttpResponse(body=json.dumps({"request_id": "test-request", "data": records}), status_code=200)
