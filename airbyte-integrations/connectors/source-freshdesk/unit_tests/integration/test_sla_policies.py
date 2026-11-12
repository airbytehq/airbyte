# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover as entrypoint_discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))  # to allow loading custom components


def _policy(policy_id, name: str, position: int) -> dict:
    return {
        "id": policy_id,
        "name": name,
        "description": None,
        "active": True,
        "is_default": position == 1,
        "position": position,
        "sla_target": {
            "priority_1": {"respond_within": 3600, "resolve_within": 86400, "business_hours": True, "escalation_enabled": True},
        },
        "applicable_to": {},
        "created_at": "2024-03-01T10:00:00Z",
        "updated_at": "2024-03-02T10:00:00Z",
    }


def test_sla_policies_ids_are_emitted_as_integers_when_api_returns_strings() -> None:
    """Freshdesk started returning `id` as a string; the stream must keep emitting the integer its schema declares."""
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})

    with HttpMocker() as http_mocker:
        http_mocker.get(
            request,
            HttpResponse(
                json.dumps(
                    [
                        _policy("67000087191", "Default SLA Policy", 1),  # new API shape: string id
                        _policy(67000087192, "Enterprise SLA Policy", 2),  # legacy API shape: numeric id
                    ]
                ),
                200,
            ),
        )
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    ids = [record.record.data["id"] for record in output.records]
    assert ids == [67000087191, 67000087192]
    assert [type(record_id) for record_id in ids] == [int, int]

    discovered = entrypoint_discover(source, config)
    stream = next(s for s in discovered.catalog.catalog.streams if s.name == "sla_policies")
    assert stream.json_schema["properties"]["id"]["type"] == ["null", "integer"]
    # Untouched fields keep their values
    assert output.records[0].record.data["name"] == "Default SLA Policy"
    assert output.records[0].record.data["sla_target"]["priority_1"]["respond_within"] == 3600
