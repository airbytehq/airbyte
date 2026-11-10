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
_YAML_FILE_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"


@pytest.mark.parametrize(
    "records",
    [
        [{"id": "67000087191", "name": "Default"}, {"id": 67000087192, "name": "Priority"}],
        [],
        [{"name": "Missing id"}, {"id": None, "name": "Null id"}],
    ],
)
def test_sla_policy_ids_are_integers(records) -> None:
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
    emitted = [message.record.data for message in output.records]
    assert len(emitted) == len(records)
    for actual, original in zip(emitted, records):
        if original.get("id") is not None:
            assert isinstance(actual["id"], int)
            assert actual == {**original, "id": int(original["id"])}
        else:
            assert actual.get("id") is None
            assert actual["name"] == original["name"]
