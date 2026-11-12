# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, List, Mapping

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config: Mapping[str, Any]) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _policy(policy_id: Any, position: int) -> Mapping[str, Any]:
    return {"id": policy_id, "name": f"Policy {position}", "position": position, "active": True, "is_default": position == 1}


@pytest.mark.parametrize(
    "api_ids",
    (
        pytest.param(["67000087191", "67000087192"], id="string_ids"),
        pytest.param([67000087191, 67000087192], id="integer_ids"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers_matching_discovered_schema(api_ids: List[Any]) -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    body = [_policy(policy_id, position) for position, policy_id in enumerate(api_ids, start=1)]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(body), 200))
        output = read(_source(config), config, catalog, StateBuilder().build())
        http_mocker.assert_number_of_calls(request, 1)

    discovered = discover(_source(config), config).catalog.catalog
    stream = next(stream for stream in discovered.streams if stream.name == _STREAM_NAME)
    assert "integer" in stream.json_schema["properties"]["id"]["type"]

    assert not output.errors
    ids = [record.record.data["id"] for record in output.records]
    assert ids == [67000087191, 67000087192]
    assert all(type(record_id) is int for record_id in ids)
