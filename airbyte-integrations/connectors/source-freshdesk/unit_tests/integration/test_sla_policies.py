# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import ConfiguredAirbyteCatalog, SyncMode, YamlDeclarativeSource
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


def _catalog() -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()


def _read() -> EntrypointOutput:
    catalog = _catalog()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _policy(policy_id: Any, position: int) -> Dict[str, Any]:
    return {
        "id": policy_id,
        "name": f"Policy {position}",
        "description": "",
        "active": True,
        "is_default": position == 1,
        "position": position,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.mark.parametrize(
    "api_ids",
    (
        pytest.param(["67000087191", "67000087192"], id="ids_as_strings"),
        pytest.param([67000087191, 67000087192], id="ids_as_integers"),
    ),
)
def test_sla_policy_ids_are_emitted_as_integers(api_ids: List[Any]) -> None:
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    body = [_policy(policy_id, position) for position, policy_id in enumerate(api_ids, start=1)]
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(body), 200))

        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    ids = [record.record.data["id"] for record in output.records]
    assert ids == [67000087191, 67000087192]
    assert all(type(record_id) is int for record_id in ids)
    assert [record.record.data["name"] for record in output.records] == ["Policy 1", "Policy 2"]
