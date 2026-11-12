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


@pytest.mark.parametrize(
    "policy_ids",
    [
        ["67000087191", "67000087192"],
        [67000087191, 67000087192],
        [],
    ],
)
def test_sla_policy_ids_are_integers(policy_ids) -> None:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([{"id": policy_id} for policy_id in policy_ids]), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    record_ids = [record.record.data["id"] for record in output.records]
    assert record_ids == ([67000087191, 67000087192] if policy_ids else [])
    assert all(type(policy_id) is int for policy_id in record_ids)
