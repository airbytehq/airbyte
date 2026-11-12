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


@pytest.mark.parametrize(
    "api_id, expected_id",
    (
        pytest.param("67000087191", 67000087191, id="string_id_from_api"),
        pytest.param(67000087192, 67000087192, id="integer_id_from_api"),
    ),
)
def test_sla_policies_emit_integer_id(api_id, expected_id) -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    policy = {"id": api_id, "name": "Default SLA Policy", "is_default": True, "position": 1, "active": True}

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS),
            HttpResponse(json.dumps([policy]), 200),
        )
        output = entrypoint_read(source, config, catalog, state)

    assert output.errors == []
    assert [record.record.data["id"] for record in output.records] == [expected_id]
    assert type(output.records[0].record.data["id"]) is int
    assert output.records[0].record.data["name"] == "Default SLA Policy"
