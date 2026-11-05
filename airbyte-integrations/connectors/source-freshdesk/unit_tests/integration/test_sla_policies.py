# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
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
_MANIFEST_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"


@pytest.mark.parametrize(
    "records, expected_ids",
    (
        ([{"id": "67000087191"}, {"id": 67000087192}], [67000087191, 67000087192]),
        ([{"id": "9007199254740993"}], [9007199254740993]),
        ([], []),
    ),
    ids=("string-and-integer", "large-integer", "empty"),
)
def test_read_emits_integer_ids(records, expected_ids) -> None:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(records), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    actual_ids = [record.record.data["id"] for record in output.records]
    assert actual_ids == expected_ids
    assert all(isinstance(record_id, int) for record_id in actual_ids)
