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


def _policy(policy_id: Any, name: str) -> Dict[str, Any]:
    return {
        "id": policy_id,
        "name": name,
        "description": "A policy",
        "active": True,
        "is_default": False,
        "position": 1,
        "applicable_to": {"product_ids": [67000001416]},
        "escalation": {"response": {"escalation_time": 1800, "agent_ids": [-1, 67013469919]}},
    }


def test_numeric_ids_are_emitted_as_integers_whether_the_api_returns_strings_or_numbers() -> None:
    # Freshdesk started returning `id` as a numeric string on this endpoint; older responses carry a number.
    # A string that is not a number is left as received instead of being coerced to a made-up value.
    api_records: List[Dict[str, Any]] = [
        _policy("67000087191", "String id"),
        _policy(67000039537, "Integer id"),
        _policy("not-a-number", "Unparseable id"),
    ]
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(api_records), 200))

        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    emitted = [record.record.data for record in output.records]
    assert [record["id"] for record in emitted] == [67000087191, 67000039537, "not-a-number"]
    # Everything other than `id` is passed through untouched.
    assert [{**record, "id": None} for record in emitted] == [{**record, "id": None} for record in api_records]
