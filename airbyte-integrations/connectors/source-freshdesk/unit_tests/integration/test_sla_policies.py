# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest
import yaml
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.sources.declarative.models import AddFields
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_YAML_FILE_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"


def _read_ids(records: list[dict]) -> list:
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
    return [record.record.data["id"] for record in output.records]


def test_sla_policy_ids_are_integers() -> None:
    ids = _read_ids([{"id": "67000087191"}, {"id": 67000087192}])
    assert all(type(policy_id) is int for policy_id in ids), ids
    assert ids == [67000087191, 67000087192]


@pytest.mark.parametrize(
    "records, expected_ids",
    [([], []), ([{"id": "not-numeric"}], ["not-numeric"])],
)
def test_sla_policy_ids_preserve_other_values(records: list[dict], expected_ids: list) -> None:
    assert _read_ids(records) == expected_ids


def test_sla_policy_transformation_preserves_null() -> None:
    manifest = yaml.safe_load(_YAML_FILE_PATH.read_text())
    transformation = ModelToComponentFactory().create_component(
        AddFields, manifest["definitions"]["streams"]["sla_policies"]["transformations"][0], config={}
    )
    record = {"id": None}

    transformation.transform(record)

    assert record == {"id": None}
