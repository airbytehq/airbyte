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
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _policy(policy_id, name):
    return {"id": policy_id, "name": name, "active": True, "is_default": False, "position": 1}


@pytest.mark.parametrize(
    "api_ids",
    (
        pytest.param(["67000087191", "67000087192"], id="string_ids"),
        pytest.param([67000087191, 67000087192], id="integer_ids"),
    ),
)
def test_sla_policies_ids_are_emitted_as_integers(api_ids):
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps([_policy(api_ids[0], "Default"), _policy(api_ids[1], "Premium")]), 200),
        )
        output = entrypoint_read(source, config, catalog, state)

    ids = [record.record.data["id"] for record in output.records]
    assert ids == [67000087191, 67000087192]
    assert all(type(policy_id) is int for policy_id in ids)
    assert [record.record.data["name"] for record in output.records] == ["Default", "Premium"]
