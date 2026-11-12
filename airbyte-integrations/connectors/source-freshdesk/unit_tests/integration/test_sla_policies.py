# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

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

sys.path.append(str(_YAML_FILE_PATH.parent))


@pytest.mark.parametrize("ids", [("67000087191", "67000087192"), (67000087191, 67000087192)], ids=["string", "integer"])
def test_sla_policy_ids_are_integers(ids) -> None:
    policies = [
        {
            "id": policy_id,
            "name": f"Policy {index}",
            "description": "SLA policy",
            "active": True,
            "is_default": False,
            "position": "2",
            "sla_target": {"priority_4": {"respond_within": "3600", "business_hours": False}},
        }
        for index, policy_id in enumerate(ids)
    ]
    records = _read(policies)
    assert [record["id"] for record in records] == [67000087191, 67000087192]
    assert all(type(record["id"]) is int for record in records)
    assert records == [dict(policy, id=int(policy["id"])) for policy in policies]


@pytest.mark.parametrize("policies", [[], [{"id": "not-a-number"}], [{"id": None}], [{"name": "Missing id"}]])
def test_sla_policies_preserve_empty_and_invalid_ids(policies) -> None:
    assert _read(policies) == [{key: value for key, value in policy.items() if value is not None} for policy in policies]


def _read(policies):
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(policies), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    return [record.record.data for record in output.records]
