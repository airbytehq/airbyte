# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from unit_tests.conftest import get_source


FIELDS = json.loads((Path(__file__).parent.parent / "opt_fields_1.7.2.json").read_text())
CONFIG = {
    "credentials": {"option_title": "PAT Credentials", "personal_access_token": "fixture-token"},
    "organization_export_ids": ["1"],
    "num_workers": 1,
}
ENDPOINTS = {
    "projects": ("projects", {"workspace": "1"}),
    "sections_compact": ("projects/1/sections", {}),
    "sections": ("sections/1", {}),
    "tasks": ("tasks", {"project": "1"}),
    "stories_compact": ("tasks/1/stories", {}),
    "stories": ("stories/1", {}),
    "workspaces": ("workspaces", {}),
    "tags": ("tags", {"workspace": "1"}),
    "users": ("users", {"workspace": "1"}),
    "teams": ("organizations/1/teams", {}),
    "team_memberships": ("teams/1/team_memberships", {}),
    "attachments_compact": ("attachments", {"parent": "1"}),
    "attachments": ("attachments/1", {}),
    "portfolios_compact": ("portfolios", {"owner": "1", "workspace": "1"}),
    "portfolios": ("portfolios/1", {}),
    "portfolios_memberships": ("portfolio_memberships", {"portfolio": "1"}),
    "custom_fields": ("workspaces/1/custom_fields", {}),
    "organization_exports": ("organization_exports/1", {}),
    "events": ("events", {"resource": "1"}),
    "portfolio_items": ("portfolios/1/items", {}),
}


def request(stream: str, token: str = "fixture-token", **extra: str) -> HttpRequest:
    path, params = ENDPOINTS[stream]
    query = {"opt_fields": FIELDS[stream], **params, **extra}
    if stream != "events":
        query["limit"] = "100"
    return HttpRequest(
        url=f"https://app.asana.com/api/1.0/{path}",
        query_params=query,
        headers={"Authorization": f"Bearer {token}"},
    )


def response(gid: str = "1", next_page: dict | None = None) -> HttpResponse:
    body = {"data": [{"gid": gid, "created_at": "2026-01-01T00:00:00Z"}]}
    if next_page:
        body["next_page"] = next_page
    return HttpResponse(json.dumps(body), 200)


def mock_parents(http: HttpMocker, exclude: str) -> dict[str, HttpRequest]:
    requests = {}
    for name in FIELDS:
        if name != exclude:
            requests[name] = request(name)
            http.get(requests[name], response())
    return requests


def read_streams(*streams: str, config: dict | None = None):
    config = config or CONFIG
    catalog = CatalogBuilder()
    for stream in streams:
        catalog = catalog.with_stream(stream, SyncMode.full_refresh)
    return read(get_source(config), config, catalog.build())
