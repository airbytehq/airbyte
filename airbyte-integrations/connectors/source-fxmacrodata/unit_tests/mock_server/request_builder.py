# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


class FXMacroDataRequestBuilder:
    BASE_URL = "https://api.fxmacrodata.com/v1"

    def __init__(self, path: str) -> None:
        self._path = path
        self._query_params: Dict[str, str] = {}
        self._headers: Dict[str, str] = {}

    @classmethod
    def announcements_endpoint(cls, currency: str, indicator: str) -> "FXMacroDataRequestBuilder":
        return cls(f"/announcements/{currency}/{indicator}").with_query_param("limit", "100")

    @classmethod
    def calendar_endpoint(cls, currency: str) -> "FXMacroDataRequestBuilder":
        return cls(f"/calendar/{currency}")

    @classmethod
    def data_catalogue_endpoint(cls, currency: str) -> "FXMacroDataRequestBuilder":
        return cls(f"/data_catalogue/{currency}")

    @classmethod
    def forex_endpoint(cls, base: str, quote: str) -> "FXMacroDataRequestBuilder":
        return cls(f"/forex/{base}/{quote}").with_query_param("limit", "100")

    def with_start_date(self, start_date: str) -> "FXMacroDataRequestBuilder":
        return self.with_query_param("start_date", start_date)

    def with_offset(self, offset: int) -> "FXMacroDataRequestBuilder":
        return self.with_query_param("offset", str(offset))

    def with_query_param(self, key: str, value: str) -> "FXMacroDataRequestBuilder":
        self._query_params[key] = value
        return self

    def with_header(self, key: str, value: str) -> "FXMacroDataRequestBuilder":
        self._headers[key] = value
        return self

    def build(self) -> HttpRequest:
        return HttpRequest(
            url=f"{self.BASE_URL}{self._path}",
            query_params=dict(self._query_params) or None,
            headers=dict(self._headers) or None,
        )


def paged_response(rows: List[Dict[str, Any]], next_offset: Optional[int] = None, **extra: Any) -> HttpResponse:
    """A list response in the shape the announcements and forex endpoints return."""
    body = {
        **extra,
        "pagination": {
            "limit": 100,
            "offset": 0,
            "returned_count": len(rows),
            "has_more": next_offset is not None,
            "next_offset": next_offset,
        },
        "data": rows,
    }
    return json_response(body)


def json_response(body: Any, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code, headers={"Content-Type": "application/json"})
