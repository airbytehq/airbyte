# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from typing import Any, Dict, List, Mapping, Optional

from unit_tests.conftest import get_source

from airbyte_cdk.models import AirbyteStateMessage, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover, read
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


BASE_URL = "https://ssapi.shipstation.com"
CONFIG = {"username": "user", "password": "pass", "start_date": "2024-01-01T00:00:00Z"}
START_DATE_PARAM = "2024-01-01T00:00:00.0000000"
PAGE_SIZE = 500


def request(path: str, query_params: Optional[Mapping[str, str]] = None) -> HttpRequest:
    return HttpRequest(f"{BASE_URL}/{path}", query_params=dict(query_params) if query_params else None)


def json_response(body: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code, headers=headers or {})


def read_stream(
    stream_name: str,
    sync_mode: SyncMode = SyncMode.full_refresh,
    state: Optional[List[AirbyteStateMessage]] = None,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
    return read(
        get_source(config=CONFIG, state=state),
        config=CONFIG,
        catalog=catalog,
        state=state,
        expecting_exception=expecting_exception,
    )


def discover_schema(stream_name: str) -> Mapping[str, Any]:
    output = discover(get_source(config=CONFIG), config=CONFIG)
    streams = {stream.name: stream for stream in output.catalog.catalog.streams}
    return streams[stream_name].json_schema


def discover_primary_key(stream_name: str) -> List[str]:
    output = discover(get_source(config=CONFIG), config=CONFIG)
    streams = {stream.name: stream for stream in output.catalog.catalog.streams}
    return [path[0] for path in streams[stream_name].source_defined_primary_key]
