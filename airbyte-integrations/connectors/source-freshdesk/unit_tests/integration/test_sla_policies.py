# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

import jsonschema
from config_builder import ConfigBuilder

from airbyte_cdk import YamlDeclarativeSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config, catalog=None, state=None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def test_string_ids_are_emitted_as_integers_matching_discovered_schema() -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    state = StateBuilder().build()
    api_policies = [
        {"id": "67000087191", "name": "Default SLA Policy", "position": 1, "is_default": True, "active": True},
        {"id": 67000087192, "name": "VIP SLA Policy", "position": 2, "is_default": False, "active": True},
    ]

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"}),
            HttpResponse(json.dumps(api_policies), 200),
        )
        output = read(_source(config, catalog, state), config, catalog, state)

    discovered = discover(_source(config), config).catalog.catalog
    schema = next(stream.json_schema for stream in discovered.streams if stream.name == _STREAM_NAME)

    records = [record.record.data for record in output.records]
    assert [record["id"] for record in records] == [67000087191, 67000087192]
    for record in records:
        assert type(record["id"]) is int
        jsonschema.validate(record, schema)
