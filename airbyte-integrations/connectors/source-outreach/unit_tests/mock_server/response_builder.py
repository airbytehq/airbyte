# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Optional

from airbyte_cdk.test.mock_http import HttpResponse


def resource(resource_id: int, resource_type: str, attributes: dict[str, Any], relationships: Optional[dict[str, Any]] = None) -> dict:
    """A JSON:API resource object as Outreach returns it."""
    return {
        "type": resource_type,
        "id": resource_id,
        "attributes": attributes,
        "relationships": relationships or {},
        "links": {"self": f"https://api.outreach.io/api/v2/{resource_type}s/{resource_id}"},
    }


def page_response(resources: list[dict], next_url: Optional[str] = None, headers: Optional[dict[str, str]] = None) -> HttpResponse:
    body: dict[str, Any] = {"data": resources}
    if next_url:
        body["links"] = {"next": next_url}
    return HttpResponse(body=json.dumps(body), status_code=200, headers=headers or {})


def error_response(status_code: int, error_id: str, title: str, detail: str, headers: Optional[dict[str, str]] = None) -> HttpResponse:
    body = {"errors": [{"id": error_id, "title": title, "detail": detail}]}
    return HttpResponse(body=json.dumps(body), status_code=status_code, headers=headers or {})


def token_response() -> HttpResponse:
    return HttpResponse(body=json.dumps({"access_token": "test-access-token", "expires_in": 7200}), status_code=200)
