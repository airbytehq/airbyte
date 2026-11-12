# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, List

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _policy(policy_id: Any, position: int) -> dict:
    return {
        "id": policy_id,
        "name": f"Policy {position}",
        "description": None,
        "active": True,
        "is_default": position == 1,
        "position": position,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.mark.parametrize(
    "response_ids, expected_ids",
    (
        pytest.param(["67000087191", "67000087192"], [67000087191, 67000087192], id="string_ids"),
        pytest.param([67000087191, 67000087192], [67000087191, 67000087192], id="integer_ids"),
        pytest.param(["67000087191", 67000087192], [67000087191, 67000087192], id="mixed_ids"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers(response_ids: List[Any], expected_ids: List[int]) -> None:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    body = [_policy(policy_id, position) for position, policy_id in enumerate(response_ids, start=1)]
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/{_STREAM_NAME}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(body), 200))
        source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    emitted_ids = [record.record.data["id"] for record in output.records]
    assert emitted_ids == expected_ids
    assert all(type(emitted_id) is int for emitted_id in emitted_ids)
    assert [record.record.data["name"] for record in output.records] == ["Policy 1", "Policy 2"]
