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


def _policy(policy_id, name: str) -> dict:
    return {
        "id": policy_id,
        "name": name,
        "description": "policy description",
        "active": True,
        "is_default": False,
        "position": 1,
        "sla_target": {
            "priority_1": {"respond_within": 3600, "resolve_within": 14400, "business_hours": True, "escalation_enabled": True},
        },
        "applicable_to": {"company_ids": [67000012345]},
        "created_at": "2024-01-18T21:18:20Z",
        "updated_at": "2024-01-18T21:18:20Z",
    }


def test_read_emits_integer_ids_when_api_returns_string_ids() -> None:
    """Freshdesk started returning sla_policies ids as numeric strings; the stream must keep emitting integers."""
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"}),
            HttpResponse(
                json.dumps([_policy("67000087191", "Test SLA"), _policy(67000039537, "Default SLA Policy")]),
                200,
            ),
        )

        output = _read()

    assert not output.errors
    assert [record.record.data["id"] for record in output.records] == [67000087191, 67000039537]
    # Every other field is emitted as the API returned it.
    assert output.records[0].record.data == _policy(67000087191, "Test SLA")
