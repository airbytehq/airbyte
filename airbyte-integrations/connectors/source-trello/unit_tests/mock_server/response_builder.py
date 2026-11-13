# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpResponse


class TrelloResponseBuilder:
    @staticmethod
    def records(records: list[dict]) -> HttpResponse:
        return HttpResponse(body=json.dumps(records), status_code=200)
