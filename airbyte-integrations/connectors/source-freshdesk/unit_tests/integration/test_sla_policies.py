# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

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


def _sla_policy(policy_id: Any, name: str) -> Dict[str, Any]:
    return {
        "id": policy_id,
        "name": name,
        "description": "An SLA policy",
        "active": True,
        "is_default": False,
        "position": 1,
        "sla_target": {
            "priority_1": {"respond_within": 900, "resolve_within": 900, "business_hours": True, "escalation_enabled": True},
        },
        "applicable_to": {"product_ids": [67000001416], "ticket_types": ["Incident"]},
        "escalation": {"response": {"escalation_time": 1800, "agent_ids": [-1, 67013469919]}},
        "created_at": "2022-12-12T23:01:24Z",
        "updated_at": "2022-12-29T16:11:38Z",
    }


def test_sla_policy_ids_are_emitted_as_integers_when_the_api_returns_strings() -> None:
    # Freshdesk started returning sla_policies ids as JSON strings; the legacy numeric shape must keep working too.
    api_records: List[Dict[str, Any]] = [
        _sla_policy("67000087191", "Test SLA"),
        _sla_policy(67000039537, "Default SLA Policy"),
    ]
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(api_records), 200))

        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    emitted = [record.record.data for record in output.records]
    assert [record["id"] for record in emitted] == [67000087191, 67000039537]
    assert all(type(record["id"]) is int for record in emitted)
    # Every other field is passed through untouched.
    assert emitted == [{**api_record, "id": int(api_record["id"])} for api_record in api_records]
