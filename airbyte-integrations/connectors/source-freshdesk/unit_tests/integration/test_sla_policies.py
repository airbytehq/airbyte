# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

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


def _read() -> EntrypointOutput:
    catalog: ConfiguredAirbyteCatalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _policy(policy_id, name: str) -> dict:
    return {
        "id": policy_id,
        "name": name,
        "description": "policy",
        "active": True,
        "is_default": False,
        "position": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.mark.parametrize(
    "api_ids, expected_ids",
    (
        pytest.param(["67000087191", "67000087192"], [67000087191, 67000087192], id="string_ids_are_emitted_as_integers"),
        pytest.param([67000087191, 67000087192], [67000087191, 67000087192], id="integer_ids_are_unchanged"),
        pytest.param([None, "67000087192"], [None, 67000087192], id="null_id_is_preserved"),
    ),
)
def test_sla_policies_emit_integer_ids(api_ids, expected_ids) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps([_policy(policy_id, f"policy {i}") for i, policy_id in enumerate(api_ids)]), 200),
        )

        output = _read()

    assert not output.errors, [error.trace.error for error in output.errors]
    emitted_ids = [record.record.data.get("id") for record in output.records]
    assert emitted_ids == expected_ids
    assert all(policy_id is None or type(policy_id) is int for policy_id in emitted_ids), emitted_ids
    assert [record.record.data["name"] for record in output.records] == [f"policy {i}" for i in range(len(api_ids))]
