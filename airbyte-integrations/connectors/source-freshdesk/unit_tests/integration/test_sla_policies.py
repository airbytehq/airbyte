# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"
sys.path.append(str(_SOURCE_FOLDER_PATH))


@pytest.mark.parametrize(
    "record, expected_record",
    (
        ({"id": "67000087191"}, {"id": 67000087191}),
        ({"id": 67000087191}, {"id": 67000087191}),
        ({"id": None}, {"id": None}),
        ({}, {}),
        ({"id": "not-a-number"}, {"id": "not-a-number"}),
    ),
    ids=("numeric-string", "integer", "null", "missing", "non-numeric-string"),
)
def test_sla_policy_id(record: Dict[str, Any], expected_record: Dict[str, Any]) -> None:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain("a-domain.freshdesk.com").build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    request = HttpRequest("https://a-domain.freshdesk.com/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([{"name": "Default SLA", **record}]), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    assert len(output.records) == 1
    emitted_record = output.records[0].record.data
    if "id" in expected_record:
        assert emitted_record.get("id") == expected_record["id"]
        assert type(emitted_record.get("id")) is type(expected_record["id"])
    else:
        assert "id" not in emitted_record
