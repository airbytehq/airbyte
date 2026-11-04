# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _read() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _request() -> HttpRequest:
    return HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)


def test_sla_policy_ids_are_integers_when_possible() -> None:
    request = _request()
    policies = [
        {"id": "67000087191", "name": "a"},
        {"id": 67000087192, "name": "b"},
        {"id": None, "name": "c"},
    ]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(policies), 200))

        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    assert len(output.records) == 3
    ids = [record.record.data.get("id") for record in output.records]
    assert ids == [67000087191, 67000087192, None]
    assert type(ids[0]) is int
    assert type(ids[1]) is int


def test_non_numeric_sla_policy_id_passes_through() -> None:
    request = _request()
    policies = [{"id": "abc", "name": "a"}]

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(policies), 200))

        output = _read()
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    ids = [record.record.data.get("id") for record in output.records]
    assert ids == ["abc"]
    assert type(ids[0]) is str
