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
    query = {"limit": "50"}
    query.update(params or {})
    return HttpRequest(url=f"{BASE_URL}{path}", query_params=query)


def deals_request() -> HttpRequest:
    return request("v1/recents", {"items": "deal", "since_timestamp": "2024-01-01 00:00:00"})


def pipedrive_error(status_code: int, error: Optional[str], headers: Optional[Mapping[str, str]] = None) -> HttpResponse:
    body = {"success": False, "errorCode": status_code, "error_info": "Please check developers.pipedrive.com"}
    if error is not None:
        body["error"] = error
    return HttpResponse(body=json.dumps(body), status_code=status_code, headers=headers or {})


def collection(records: list) -> HttpResponse:
    body = {"success": True, "data": records, "additional_data": {"pagination": {"more_items_in_collection": False}}}
    return HttpResponse(body=json.dumps(body), status_code=200)
