# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


class NylasResponseBuilder:
    @staticmethod
    def records(records):
        return HttpResponse(json.dumps({"request_id": "request-1", "data": records}), status_code=200)

    @staticmethod
    def error(status_code, message):
        return HttpResponse(
            json.dumps({"request_id": "request-1", "error": {"type": "general", "message": message}}),
            status_code=status_code,
        )
