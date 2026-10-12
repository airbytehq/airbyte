# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

"""Shared helpers for `source-pipedrive` unit tests."""

import json
from typing import Any, Mapping, Optional

from conftest import get_source as _shared_get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


API_TOKEN = "test_api_token"
START_DATE = "2024-01-01T00:00:00Z"
CONFIG: Mapping[str, Any] = {"api_token": API_TOKEN, "replication_start_date": START_DATE}
BASE_URL = "https://api.pipedrive.com/"


def get_source(config: Mapping[str, Any] = CONFIG, catalog=None) -> YamlDeclarativeSource:
    return _shared_get_source(config)


def read_stream(stream_name: str, config: Mapping[str, Any] = CONFIG, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config, catalog), config, catalog, expecting_exception=expecting_exception)


def request(path: str, params: Optional[Mapping[str, str]] = None) -> HttpRequest:
    query = {"api_token": API_TOKEN}
    query.update(params or {})
    return HttpRequest(url=f"{BASE_URL}{path}", query_params=query)


_DEALS_QUERY = {
    "limit": "500",
    "sort_by": "update_time",
    "sort_direction": "asc",
    "status": "open,won,lost,deleted",
    "updated_since": "2024-01-01T00:00:00Z",
}


def deals_request() -> HttpRequest:
    return request("api/v2/deals", _DEALS_QUERY)


def deals_archived_request() -> HttpRequest:
    """`deals_archived` is read alongside `deals` as a parent of the deal child streams."""
    return request("api/v2/deals/archived", _DEALS_QUERY)


def empty_v2_page() -> HttpResponse:
    return HttpResponse(body=json.dumps({"success": True, "data": [], "additional_data": {"next_cursor": None}}), status_code=200)


def pipedrive_error(status_code: int, error: Optional[str], headers: Optional[Mapping[str, str]] = None) -> HttpResponse:
    body = {"success": False, "errorCode": status_code, "error_info": "Please check developers.pipedrive.com"}
    if error is not None:
        body["error"] = error
    return HttpResponse(body=json.dumps(body), status_code=status_code, headers=headers or {})


def collection(records: list) -> HttpResponse:
    body = {"success": True, "data": records, "additional_data": {"pagination": {"more_items_in_collection": False}}}
    return HttpResponse(body=json.dumps(body), status_code=200)
