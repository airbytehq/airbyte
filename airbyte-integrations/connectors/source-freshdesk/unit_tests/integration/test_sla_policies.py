# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, List

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover as entrypoint_discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config, catalog=None, state=None) -> YamlDeclarativeSource:
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)


def _policy(policy_id: Any, name: str) -> dict:
    return {"id": policy_id, "name": name, "active": True, "is_default": False, "position": 1}


@pytest.mark.parametrize(
    "raw_ids, expected_ids",
    (
        pytest.param(["67000087191", "67000039537"], [67000087191, 67000039537], id="string_ids"),
        pytest.param([67000087191, 67000039537], [67000087191, 67000039537], id="integer_ids"),
        pytest.param(["67000087191", 67000039537], [67000087191, 67000039537], id="mixed_ids"),
    ),
)
def test_sla_policy_ids_are_emitted_as_integers_matching_discovered_schema(raw_ids: List[Any], expected_ids: List[Any]) -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    state = StateBuilder().build()
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/{_STREAM_NAME}", query_params={"per_page": "100"})
    body = [_policy(policy_id, f"policy {index}") for index, policy_id in enumerate(raw_ids)]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(body), 200))
        output = entrypoint_read(_source(config, catalog, state), config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    discovered = entrypoint_discover(_source(config), config)
    [stream] = [stream for stream in discovered.catalog.catalog.streams if stream.name == _STREAM_NAME]
    assert stream.json_schema["properties"]["id"]["type"] == ["null", "integer"]

    assert not output.errors
    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == expected_ids
    assert all(type(policy_id) is int for policy_id in emitted_ids)
    assert [record.record.data["name"] for record in output.records] == [policy["name"] for policy in body]
