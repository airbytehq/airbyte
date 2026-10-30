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
from airbyte_cdk.test.state_builder import StateBuilder


_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(_SOURCE_FOLDER_PATH))
_DOMAIN = "a-domain.freshdesk.com"


@pytest.mark.parametrize(
    "id_fields, expected_id_fields",
    [
        ({"id": "67000012345"}, {"id": 67000012345}),
        ({"id": 67000012345}, {"id": 67000012345}),
        ({"id": "9007199254740993"}, {"id": 9007199254740993}),
        ({"id": "0"}, {"id": 0}),
        ({"id": 0}, {"id": 0}),
        ({"id": None}, {"id": None}),
        ({}, {}),
        ({"id": "not-a-number"}, {"id": "not-a-number"}),
        ({"id": ""}, {"id": ""}),
    ],
)
def test_sla_policy_ids_are_normalized_without_losing_data(
    id_fields: dict[str, str | int | None], expected_id_fields: dict[str, str | int | None]
) -> None:
    policy = {**id_fields, "name": "Test policy", "active": True, "position": 1}
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_SOURCE_FOLDER_PATH / "manifest.yaml"), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([policy]), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    assert len(output.records) == 1
    record = output.records[0].record
    assert record is not None
    assert {key: value for key, value in record.data.items() if key != "id"} == {"name": "Test policy", "active": True, "position": 1}
    assert record.data.get("id") == expected_id_fields.get("id")
    assert type(record.data.get("id")) is type(expected_id_fields.get("id"))
    if not id_fields:
        assert "id" not in record.data
