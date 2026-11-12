# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _read() -> EntrypointOutput:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return entrypoint_read(_source(config), config, catalog, StateBuilder().build())


def _policy(policy_id, name: str) -> dict:
    return {"id": policy_id, "name": name, "active": True, "is_default": False, "position": 1}


@pytest.mark.parametrize(
    "api_ids",
    (
        pytest.param(["67000087191", "67000087192"], id="string_ids"),
        pytest.param([67000087191, 67000087192], id="integer_ids"),
    ),
)
def test_sla_policies_emit_integer_ids_matching_discovered_schema(api_ids) -> None:
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            HttpResponse(json.dumps([_policy(api_ids[0], "Default"), _policy(api_ids[1], "VIP")]), 200),
        )
        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    records = [record.record.data for record in output.records]
    assert [(record["id"], record["name"]) for record in records] == [(67000087191, "Default"), (67000087192, "VIP")]
    assert all(type(record["id"]) is int for record in records)

    config = ConfigBuilder().domain(_DOMAIN).build()
    discovered = discover(_source(config), config)
    stream = next(s for s in discovered.catalog.catalog.streams if s.name == _STREAM_NAME)
    assert "integer" in stream.json_schema["properties"]["id"]["type"]
