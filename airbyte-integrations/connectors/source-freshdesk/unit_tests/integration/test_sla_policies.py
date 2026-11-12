# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config: Mapping[str, Any]) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _read() -> EntrypointOutput:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return entrypoint_read(_source(config), config, catalog)


def _sla_policy(policy_id: Any, group_id: Any, respond_within: Any) -> Mapping[str, Any]:
    return {
        "id": policy_id,
        "name": "Default SLA Policy",
        "description": "default policy",
        "active": True,
        "is_default": True,
        "position": 1,
        "sla_target": {"priority_4": {"respond_within": respond_within, "resolve_within": 3600, "business_hours": False}},
        "applicable_to": {"group_ids": [group_id]},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.mark.parametrize(
    "api_policy",
    (
        pytest.param(_sla_policy(67000087191, 67000012345, 900), id="numeric_ids"),
        pytest.param(_sla_policy("67000087191", "67000012345", "900"), id="string_ids"),
    ),
)
def test_sla_policies_emit_integer_ids_matching_discovered_schema(api_policy: Mapping[str, Any]) -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    discovered = discover(_source(config), config)
    schema = next(stream.json_schema for stream in discovered.catalog.catalog.streams if stream.name == _STREAM_NAME)
    assert schema["properties"]["id"]["type"] == ["null", "integer"]

    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([api_policy]), 200))
        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    assert len(output.records) == 1
    record = output.records[0].record.data
    assert record["id"] == 67000087191 and type(record["id"]) is int
    assert record["applicable_to"]["group_ids"] == [67000012345]
    assert type(record["applicable_to"]["group_ids"][0]) is int
    assert record["sla_target"]["priority_4"]["respond_within"] == 900
    assert type(record["sla_target"]["priority_4"]["respond_within"]) is int
    assert record["name"] == "Default SLA Policy"
