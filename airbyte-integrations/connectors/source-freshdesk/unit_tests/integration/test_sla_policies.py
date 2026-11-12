# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config: Dict[str, Any]) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _read(config: Dict[str, Any]) -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return entrypoint_read(_source(config), config, catalog, StateBuilder().build())


def _discovered_id_types(config: Dict[str, Any]) -> List[str]:
    catalog = discover(_source(config), config).catalog.catalog
    stream = next(stream for stream in catalog.streams if stream.name == _STREAM_NAME)
    return stream.json_schema["properties"]["id"]["type"]


def _policy(policy_id: Any, name: str) -> Dict[str, Any]:
    return {
        "id": policy_id,
        "name": name,
        "active": True,
        "is_default": False,
        "position": 1,
        "sla_target": {
            "priority_4": {"respond_within": 3600, "resolve_within": 14400, "business_hours": False, "escalation_enabled": True}
        },
        "applicable_to": {"company_ids": [67000087200]},
        "created_at": "2024-01-18T21:18:20Z",
        "updated_at": "2024-01-18T21:18:20Z",
    }


def test_string_ids_from_the_api_are_emitted_as_the_integers_the_catalog_declares() -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    # Freshdesk started returning `id` as a string; the second record keeps the documented numeric shape.
    policies = [_policy("67000087191", "Default SLA Policy"), _policy(67000087192, "Enterprise SLA Policy")]

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"}),
            HttpResponse(json.dumps(policies), 200),
        )
        output = _read(config)

    assert not output.errors
    assert "integer" in _discovered_id_types(config)
    assert [record.record.data["id"] for record in output.records] == [67000087191, 67000087192]
    assert [record.record.data for record in output.records] == [_policy(67000087191, "Default SLA Policy"), policies[1]]
