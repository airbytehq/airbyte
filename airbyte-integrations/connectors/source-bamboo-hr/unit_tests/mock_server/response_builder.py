# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any

from airbyte_cdk.test.mock_http import HttpResponse


def response(records: dict[str, Any] | list[dict[str, Any]]) -> HttpResponse:
    return HttpResponse(body=json.dumps(records), status_code=200)
