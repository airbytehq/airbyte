# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

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

# The manifest references custom components from components.py in the connector folder.
sys.path.append(str(_SOURCE_FOLDER_PATH))


def _read() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _policy(policy_id, name: str) -> dict:
    return {
        "id": policy_id,
        "name": name,
        "description": "Applies to all tickets",
        "active": True,
        "is_default": False,
        "position": 1,
        "sla_target": {
            "priority_4": {"respond_within": 3600, "resolve_within": 14400, "business_hours": False, "escalation_enabled": True},
        },
        "created_at": "2024-05-01T10:00:00Z",
        "updated_at": "2024-05-02T10:00:00Z",
    }


def test_sla_policies_emits_integer_ids_when_api_returns_string_ids() -> None:
    # Freshdesk started returning sla_policies ids as strings; the stream schema (and tickets.sla_policy_id) is integer.
    api_records = [_policy("67000087191", "Default SLA Policy"), _policy(67000087192, "Enterprise SLA Policy")]
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"}),
            HttpResponse(json.dumps(api_records), 200),
        )

        output = _read()

    assert not output.errors
    expected = [_policy(67000087191, "Default SLA Policy"), _policy(67000087192, "Enterprise SLA Policy")]
    assert [record.record.data for record in output.records] == expected
