# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


BASE_URL = "https://app.pennylane.com/api/external/v2"


def list_request(path: str, cursor: str | None = None) -> HttpRequest:
    query_params = {"limit": "100"}
    if cursor is not None:
        query_params["cursor"] = cursor
    return HttpRequest(url=f"{BASE_URL}/{path}", query_params=query_params)


def list_response(records: list[dict], next_cursor: str | None = None) -> HttpResponse:
    return HttpResponse(
        body=json.dumps({"items": records, "has_more": next_cursor is not None, "next_cursor": next_cursor}),
        status_code=200,
    )
