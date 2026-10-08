# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, Optional
from urllib.parse import quote

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse

from .config import TOKEN_URL


BASE_URL = "https://api.zoom.us/v2"
PAGE_SIZE = "30"


def double_encode_uuid(uuid: str) -> str:
    """Zoom requires webinar UUIDs that start with `/` or contain `//` to be double URL-encoded in paths."""
    return quote(quote(uuid, safe=""), safe="")


class ZoomRequestBuilder:
    @staticmethod
    def token() -> HttpRequest:
        return HttpRequest(url=TOKEN_URL, query_params={"grant_type": "account_credentials", "account_id": "test_account_id"})

    @staticmethod
    def users() -> HttpRequest:
        return HttpRequest(url=f"{BASE_URL}/users", query_params={"page_size": PAGE_SIZE})

    @staticmethod
    def user_webinars(user_id: str, next_page_token: Optional[str] = None) -> HttpRequest:
        return ZoomRequestBuilder.endpoint(f"/users/{user_id}/webinars", paginated=True, next_page_token=next_page_token)

    @staticmethod
    def endpoint(path: str, paginated: bool = False, next_page_token: Optional[str] = None) -> HttpRequest:
        query_params: Optional[Dict[str, str]] = None
        if paginated:
            query_params = {"page_size": PAGE_SIZE}
            if next_page_token:
                query_params["next_page_token"] = next_page_token
        return HttpRequest(url=f"{BASE_URL}{path}", query_params=query_params)


def json_response(body: Dict[str, Any], status_code: int = 200) -> HttpResponse:
    return HttpResponse(json.dumps(body), status_code=status_code)


def zoom_error(code: int, message: str, status_code: int) -> HttpResponse:
    return json_response({"code": code, "message": message}, status_code=status_code)
