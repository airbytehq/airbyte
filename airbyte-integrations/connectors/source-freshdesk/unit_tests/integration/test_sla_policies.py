# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, List

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _read() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _policy(policy_id: Any) -> dict:
    return {
        "id": policy_id,
        "name": "Default SLA Policy",
        "description": "default policy",
        "active": True,
        "is_default": True,
        "position": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.mark.parametrize(
    "api_ids, expected_ids",
    (
        pytest.param(["67000087191", "67000087192"], [67000087191, 67000087192], id="string_ids_coerced_to_integer"),
        pytest.param([67000087191, 67000087192], [67000087191, 67000087192], id="integer_ids_unchanged"),
    ),
)
def test_sla_policies_emits_integer_ids(api_ids: List[Any], expected_ids: List[Any]) -> None:
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([_policy(policy_id) for policy_id in api_ids]), 200))

        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == expected_ids
    assert all(type(policy_id) is int for policy_id in emitted_ids)
    assert [record.record.data["name"] for record in output.records] == ["Default SLA Policy"] * len(api_ids)
