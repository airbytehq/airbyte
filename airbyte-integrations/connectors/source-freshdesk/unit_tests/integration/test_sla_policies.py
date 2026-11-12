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


def _policy(policy_id: Any, name: str) -> dict:
    return {"id": policy_id, "name": name, "active": True, "is_default": False, "position": 1}


@pytest.mark.parametrize(
    "api_ids, expected_ids",
    (
        pytest.param(["67000087191", "67000087192"], [67000087191, 67000087192], id="string_ids_from_api"),
        pytest.param([67000087191, 67000087192], [67000087191, 67000087192], id="integer_ids_from_api"),
        pytest.param(["67000087191", 67000087192], [67000087191, 67000087192], id="mixed_ids_from_api"),
    ),
)
def test_sla_policy_ids_are_emitted_as_integers(api_ids: List[Any], expected_ids: List[int]) -> None:
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    body = [_policy(policy_id, f"policy {index}") for index, policy_id in enumerate(api_ids)]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(body), 200))
        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    ids = [record.record.data["id"] for record in output.records]
    assert ids == expected_ids
    assert all(type(record_id) is int for record_id in ids)
    assert [record.record.data["name"] for record in output.records] == ["policy 0", "policy 1"]
