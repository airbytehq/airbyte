# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any, Dict, List

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_YAML_FILE_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"


def _read(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(records), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    return [record.record.data for record in output.records]


@pytest.mark.parametrize("policy_id", ("67000087191", 67000087191))
def test_sla_policy_id_is_integer(policy_id: Any) -> None:
    records = _read([{"id": policy_id}])

    assert [record["id"] for record in records] == [67000087191]
    assert all(type(record["id"]) is int for record in records)


@pytest.mark.parametrize("record", ({}, {"id": "not-a-number"}, {"id": ""}, {"id": "1.5"}, {"id": "-1"}))
def test_sla_policy_other_ids_are_unchanged(record: Dict[str, Any]) -> None:
    record = {"name": "Test policy", **record}
    assert _read([record]) == [record]


def test_sla_policy_null_id_is_not_coerced() -> None:
    records = _read([{"id": None}])

    assert len(records) == 1
    assert records[0].get("id") is None


def test_sla_policies_empty_response() -> None:
    assert _read([]) == []
