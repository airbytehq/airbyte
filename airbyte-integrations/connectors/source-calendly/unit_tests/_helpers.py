# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Mapping

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_key": "test_api_key", "start_date": "2024-01-01T00:00:00Z"}
ORGANIZATION_URI = "https://api.calendly.com/organizations/test-organization"
USER = {"uri": "https://api.calendly.com/users/test-user", "current_organization": ORGANIZATION_URI}


def request(path: str, params: Mapping[str, str] | None = None, body: Mapping[str, Any] | None = None) -> HttpRequest:
    return HttpRequest(
        url=f"https://api.calendly.com/{path}",
        query_params=dict(params or {}),
        headers={"Authorization": f"Bearer {CONFIG['api_key']}"},
        body=body,
    )


def collection(records: list[dict[str, Any]], next_page_token: str | None = None) -> HttpResponse:
    return HttpResponse(body=json.dumps({"collection": records, "pagination": {"next_page_token": next_page_token}}), status_code=200)


def resource(record: Mapping[str, Any]) -> HttpResponse:
    return HttpResponse(body=json.dumps({"resource": record}), status_code=200)


def read_stream(
    stream_name: str, config: Mapping[str, Any] = CONFIG, state=None, sync_mode: SyncMode = SyncMode.incremental
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(get_source(config, state), config, catalog, state=state)


def mock_user(http_mocker: HttpMocker) -> HttpRequest:
    target = request("users/me")
    http_mocker.get(target, resource(USER))
    return target


def list_request(stream: str, page_token: str | None = None, min_start_time: str = "2024-01-01T00:00:00.000000Z") -> HttpRequest:
    params = {"count": "100", "organization": ORGANIZATION_URI}
    if stream in {"event_types", "organization_memberships"}:
        params["sort"] = "updated_at:desc"
    if stream == "scheduled_events":
        params.update(sort="start_time:desc", min_start_time=min_start_time)
    if page_token is not None:
        params["page_token"] = page_token
    return request(stream, params)


def invitees_request(event_id: str, page_token: str | None = None) -> HttpRequest:
    params = {"count": "100", "sort": "created_at:desc"}
    if page_token is not None:
        params["page_token"] = page_token
    return request(f"scheduled_events/{event_id}/invitees", params)


def event(event_id: str) -> dict[str, str]:
    return {"uri": f"https://api.calendly.com/scheduled_events/{event_id}", "start_time": "2024-01-15T00:00:00.000000Z"}
