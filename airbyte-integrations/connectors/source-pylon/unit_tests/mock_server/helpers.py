# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import _run_command, make_file, read
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://api.usepylon.com"
TOKEN = "synthetic-pylon-token"
START = "2026-01-01T00:00:00Z"
NOW = "2026-01-15T00:00:00Z"
CONFIG = {"api_token": TOKEN, "start_date": START}
LIST_STREAMS = (
    "accounts",
    "contacts",
    "tags",
    "teams",
    "users",
    "custom_fields",
    "knowledge_bases",
    "ticket_forms",
    "user_roles",
    "activity_types",
    "issue_statuses",
)


def fixture_record(stream):
    path = Path(__file__).parent.parent / "resource" / "http" / "response" / f"{stream}.json"
    return json.loads(path.read_text())


def list_request(path, cursor=None, **params):
    query = {"limit": "999", **params}
    if cursor:
        query["cursor"] = cursor
    return HttpRequest(f"{BASE}/{path.lstrip('/')}", query_params=query, headers={"Authorization": f"Bearer {TOKEN}"})


def search_request(start=START, end=NOW, cursor=None):
    time_filter = {"field": "updated_at", "operator": "time_range", "values": [start, end]}
    body = {"filter": time_filter, "limit": 999}
    if cursor:
        body["cursor"] = cursor
    return HttpRequest(f"{BASE}/issues/search", body=body, headers={"Authorization": f"Bearer {TOKEN}"})


def page(records, next_cursor=None):
    return HttpResponse(
        json.dumps(
            {
                "data": records,
                "pagination": {"cursor": next_cursor or "", "has_next_page": next_cursor is not None},
            }
        )
    )


def error(status, code="synthetic_error", headers=None):
    return HttpResponse(json.dumps({"code": code, "message": "Synthetic API failure"}), status_code=status, headers=headers or {})


def run(stream, cfg=None, mode=SyncMode.full_refresh, state=None, expecting_exception=False):
    cfg = cfg or CONFIG.copy()
    state = state or StateBuilder().build()
    return read(
        get_source(cfg, state),
        config=cfg,
        catalog=CatalogBuilder().with_stream(stream, mode).build(),
        state=state,
        expecting_exception=expecting_exception,
    )


def check(cfg=None):
    cfg = cfg or CONFIG.copy()
    with TemporaryDirectory() as directory:
        config_file = make_file(Path(directory) / "config.json", cfg)
        return _run_command(get_source(cfg), ["check", "--config", config_file])
