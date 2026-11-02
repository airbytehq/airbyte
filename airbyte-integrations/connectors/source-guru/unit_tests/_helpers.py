import json
from typing import Any, Mapping

from conftest import get_source as _shared_get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpRequest, HttpResponse


CONFIG: Mapping[str, Any] = {
    "username": "guru-user@example.org",
    "password": "test-api-key",
    "start_date": "2024-01-01T00:00:00Z",
    "team_id": "team-1",
    "search_cards_query": "test",
}
BASE_URL = "https://api.getguru.com/api/v1/"


def get_source(config: Mapping[str, Any] = CONFIG) -> YamlDeclarativeSource:
    return _shared_get_source(config)


def read_stream(stream_name: str, config: Mapping[str, Any] = CONFIG, expecting_exception: bool = False) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    return read(get_source(config), config, catalog, expecting_exception=expecting_exception)


def request(path: str) -> HttpRequest:
    return HttpRequest(url=f"{BASE_URL}{path}", query_params={})


def json_response(body: Any, status_code: int = 200) -> HttpResponse:
    return HttpResponse(body=json.dumps(body), status_code=status_code)
