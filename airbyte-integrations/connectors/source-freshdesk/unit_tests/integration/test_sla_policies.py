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


def _policy(policy_id, position):
    return {
        "id": policy_id,
        "name": f"Policy {policy_id}",
        "description": "SLA policy",
        "active": True,
        "is_default": False,
        "position": position,
        "sla_target": {"priority_4": {"respond_within": 900, "resolve_within": 3600, "business_hours": False}},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
    }


@pytest.mark.parametrize(
    "api_ids, api_positions",
    (
        pytest.param(["67000087191", "67000087192"], ["1", "2"], id="ids_returned_as_strings"),
        pytest.param([67000087191, 67000087192], [1, 2], id="ids_returned_as_integers"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers(api_ids, api_positions):
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps([_policy(i, p) for i, p in zip(api_ids, api_positions)]), 200),
        )

        output = _read()

    assert not output.errors
    records = [record.record.data for record in output.records]
    assert [record["id"] for record in records] == [67000087191, 67000087192]
    assert all(type(record["id"]) is int for record in records)
    assert [record["position"] for record in records] == [1, 2]
    assert records[0]["sla_target"]["priority_4"]["respond_within"] == 900
