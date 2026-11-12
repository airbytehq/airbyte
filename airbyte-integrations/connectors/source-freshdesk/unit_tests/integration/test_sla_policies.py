# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, List, Optional

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source() -> YamlDeclarativeSource:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _sla_policy(policy_id: Any) -> dict:
    return {
        "id": policy_id,
        "name": "Default SLA Policy",
        "description": "default policy",
        "active": True,
        "is_default": True,
        "position": 1,
    }


@pytest.mark.parametrize(
    "api_ids, expected_ids",
    (
        pytest.param(["67000087191", "67000087192"], [67000087191, 67000087192], id="string_ids"),
        pytest.param([67000087191, 67000087192], [67000087191, 67000087192], id="integer_ids"),
        pytest.param([None], [None], id="null_id"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers(api_ids: List[Optional[Any]], expected_ids: List[Optional[int]]) -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([_sla_policy(policy_id) for policy_id in api_ids]), 200))
        output = read(_source(), config, catalog)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    emitted_ids = [record.record.data.get("id") for record in output.records]
    assert emitted_ids == expected_ids
    assert all(policy_id is None or type(policy_id) is int for policy_id in emitted_ids)

    discovered_stream = next(stream for stream in discover(_source(), config).catalog.catalog.streams if stream.name == _STREAM_NAME)
    assert "integer" in discovered_stream.json_schema["properties"]["id"]["type"]
