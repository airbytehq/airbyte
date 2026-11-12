# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _read_sla_policies() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _sla_policy(policy_id: Any, name: str) -> dict:
    return {
        "id": policy_id,
        "name": name,
        "description": "a policy",
        "active": True,
        "is_default": False,
        "position": 1,
        "sla_target": {
            "priority_1": {"respond_within": 3600, "resolve_within": 7200, "business_hours": True, "escalation_enabled": True}
        },
        "applicable_to": {"group_ids": [67000353915]},
        "escalation": {"response": {"escalation_time": 0, "agent_ids": [67001234567]}},
    }


@pytest.mark.parametrize(
    "api_ids",
    (
        pytest.param(["67000087191", "67000087192"], id="ids_returned_as_strings"),
        pytest.param([67000087191, 67000087192], id="ids_returned_as_numbers"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers(api_ids: list) -> None:
    policies = [_sla_policy(policy_id, f"policy {index}") for index, policy_id in enumerate(api_ids)]

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"}),
            HttpResponse(json.dumps(policies), 200),
        )
        output = _read_sla_policies()

    emitted_ids = [record.record.data["id"] for record in output.records]
    # `==` alone would not catch a bool/str mix-up hidden behind equality, so pin the JSON type too.
    assert emitted_ids == [67000087191, 67000087192]
    assert [type(emitted_id) for emitted_id in emitted_ids] == [int, int]
    # Everything other than the id is passed through untouched.
    assert [{**record.record.data, "id": None} for record in output.records] == [{**policy, "id": None} for policy in policies]
    assert output.errors == []
