# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any
from urllib.parse import parse_qs, urlsplit

from airbyte_cdk.test.mock_http import HttpResponse

from .request_builder import ACCESS_TOKEN


def login_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": ACCESS_TOKEN, "token_type": "Bearer"}), status_code=200)


def page_response(records: list[dict[str, Any]], next_page_url: str | None = None) -> HttpResponse:
    """One page of a version 5 query. A page with no next page carries both keys as null."""
    next_page_token = parse_qs(urlsplit(next_page_url).query)["nextPageToken"][0] if next_page_url else None
    body = {"nextPageToken": next_page_token, "nextPageUrl": next_page_url, "values": records}
    return HttpResponse(body=json.dumps(body), status_code=200)
