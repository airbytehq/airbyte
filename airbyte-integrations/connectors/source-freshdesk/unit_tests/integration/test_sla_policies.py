# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, List, Mapping

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _policy(policy_id: Any, name: str) -> Mapping[str, Any]:
    return {"id": policy_id, "name": name, "active": True, "is_default": False, "position": 1}


def _read(policies: List[Mapping[str, Any]]) -> List[Mapping[str, Any]]:
    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps(policies), 200),
        )
        output = _run_read()
    assert not output.errors, [error.trace.error for error in output.errors]
    return [record.record.data for record in output.records]


def _run_read():
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


@pytest.mark.parametrize(
    "api_ids",
    (
        pytest.param(["67000087191", "67000087192"], id="ids_returned_as_strings"),
        pytest.param([67000087191, 67000087192], id="ids_returned_as_integers"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers(api_ids: List[Any]) -> None:
    records = _read([_policy(api_ids[0], "Default"), _policy(api_ids[1], "VIP")])

    assert [record["id"] for record in records] == [67000087191, 67000087192]
    assert all(type(record["id"]) is int for record in records)
    assert [record["name"] for record in records] == ["Default", "VIP"]


def test_sla_policies_null_id_is_left_unchanged() -> None:
    records = _read([_policy(None, "Default")])

    assert [record.get("id") for record in records] == [None]
    assert records[0]["name"] == "Default"
