# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from functools import lru_cache
from pathlib import Path

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"customer_domain": "example.trackhs.com", "api_key": "test-key", "api_secret": "test-secret"}


@lru_cache
def request(path: str, page: int = 1) -> HttpRequest:
    params = {"size": "100"}
    if page > 1 or path == "pms/units/types":
        params["page"] = str(page)
    return HttpRequest(f"https://example.trackhs.com/api/{path}", query_params=params)


def response(key: str, records: list[dict], page: int = 1) -> HttpResponse:
    return HttpResponse(json.dumps({"_embedded": {key: records}, "page": page, "page_size": 100}))


def mock_reservations(http_mocker: HttpMocker, records: list[dict]) -> None:
    http_mocker.get(
        HttpRequest(
            "https://example.trackhs.com/api/pms/reservations",
            query_params={"size": "100", "scroll": "1", "sortColumn": "id", "updatedSince": "1900-01-01T00:00:00+0000"},
        ),
        HttpResponse(json.dumps({"_embedded": {"reservations": records}, "scroll": None})),
    )


def read_stream(name: str) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(name, SyncMode.full_refresh).build()
    local_manifest = Path(__file__).parents[2] / "manifest.yaml"
    ci_manifest = Path("/airbyte/integration_code/source_declarative_manifest/manifest.yaml")
    source = YamlDeclarativeSource(
        path_to_yaml=str(ci_manifest if ci_manifest.exists() else local_manifest), catalog=catalog, config=CONFIG, state=[]
    )
    return read(source, CONFIG, catalog, state=[])
