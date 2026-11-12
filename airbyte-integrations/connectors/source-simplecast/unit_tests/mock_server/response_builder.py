# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


def collection_response(records):
    return HttpResponse(body=json.dumps({"collection": records}), status_code=200)
