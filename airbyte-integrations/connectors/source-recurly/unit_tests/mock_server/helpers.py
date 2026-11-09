# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import base64
import json

from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


BASE = "https://v3.recurly.com"
API_KEY = "synthetic-recurly-key"
START = "2026-01-01T00:00:00Z"
NOW = "2026-01-15T00:00:00Z"
CONFIG = {"api_key": API_KEY, "begin_time": START}
AUTH = {"Authorization": "Basic " + base64.b64encode(f"{API_KEY}:".encode()).decode()}


def list_request(path, begin=START, end=NOW, **extra):
    query = {"sort": "updated_at", "order": "asc", "limit": "200", "begin_time": begin, "end_time": end, **extra}
    return HttpRequest(f"{BASE}/{path.lstrip('/')}", query_params=query, headers=AUTH)


def page_request(path, cursor, begin=START, end=NOW):
    return list_request(path, begin=begin, end=end, cursor=cursor)


def page(records, next_path=None):
    return HttpResponse(json.dumps({"object": "list", "has_more": next_path is not None, "next": next_path, "data": records}))


def record(record_id, updated_at, **fields):
    return {"id": record_id, "object": "synthetic", "created_at": updated_at, "updated_at": updated_at, **fields}


def error(status, error_type="synthetic", headers=None):
    body = {"error": {"type": error_type, "message": "Synthetic Recurly failure"}}
    return HttpResponse(json.dumps(body), status_code=status, headers=headers or {})


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
