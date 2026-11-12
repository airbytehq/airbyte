# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from urllib.parse import urlencode

from airbyte_cdk.test.mock_http import HttpRequest


BASE_URL = "https://api.outreach.io/api/v2"
TOKEN_REQUEST = HttpRequest(
    "https://api.outreach.io/oauth/token",
    body="grant_type=refresh_token&client_id=test-client-id&client_secret=test-client-secret&refresh_token=test-refresh-token",
)


def page_url(stream_name: str, after: str | None = None) -> str:
    params = {
        "count": "false",
        "sort": "updatedAt",
        "page[size]": "100" if stream_name == "mailings" else "1000",
        "newFilterSyntax": "true",
        "filter[updatedAt][gte]": "2020-11-16T00:00:00.000Z",
    }
    if after:
        params["page[after]"] = after
    return f"{BASE_URL}/{stream_name}?{urlencode(params)}"


def page_request(stream_name: str, token: str, after: str | None = None) -> HttpRequest:
    return HttpRequest(page_url(stream_name, after), headers={"Authorization": f"Bearer {token}"})
