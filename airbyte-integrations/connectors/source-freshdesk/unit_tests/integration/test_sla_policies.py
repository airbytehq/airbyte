# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
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


_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(_SOURCE_FOLDER_PATH))
_DOMAIN = "a-domain.freshdesk.com"


def _read_policies(policies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_SOURCE_FOLDER_PATH / "manifest.yaml"), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(policies), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)
    assert not output.errors
    return [message.record.data for message in output.records]


def test_sla_policy_ids_are_integers() -> None:
    records = _read_policies([{"id": "67000087191"}, {"id": 67000039537}])

    ids = [record["id"] for record in records]
    assert ids == [67000087191, 67000039537]
    assert all(type(policy_id) is int for policy_id in ids)


@pytest.mark.parametrize("policy_id", [None, "", "not-an-id", "12.5", "-12"])
def test_non_digit_ids_pass_through(policy_id: Any) -> None:
    records = _read_policies([{"id": policy_id}])
    assert len(records) == 1
    assert records[0].get("id") == policy_id


def test_empty_policies() -> None:
    assert _read_policies([]) == []
