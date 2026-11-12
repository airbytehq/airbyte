# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Mapping

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover as entrypoint_discover
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _source(config: Mapping[str, Any]) -> YamlDeclarativeSource:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    return YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=StateBuilder().build())


def _sla_policy(policy_id: Any, group_ids: list) -> Mapping[str, Any]:
    return {
        "id": policy_id,
        "name": "Default SLA Policy",
        "active": True,
        "is_default": True,
        "position": 1,
        "applicable_to": {"group_ids": group_ids},
    }


@pytest.mark.parametrize(
    "api_policy, expected_id, expected_group_ids",
    (
        pytest.param(_sla_policy("67000087191", ["67000123456"]), 67000087191, [67000123456], id="string_ids"),
        pytest.param(_sla_policy(67000087192, [67000123457]), 67000087192, [67000123457], id="integer_ids"),
    ),
)
def test_sla_policy_ids_are_emitted_as_the_discovered_integer_type(
    api_policy: Mapping[str, Any], expected_id: int, expected_group_ids: list
) -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()

    discovered = entrypoint_discover(_source(config), config)
    schema = next(stream.json_schema for stream in discovered.catalog.catalog.streams if stream.name == _STREAM_NAME)
    assert schema["properties"]["id"]["type"] == ["null", "integer"]

    with HttpMocker() as http_mocker:
        http_mocker.get(
            HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"}),
            HttpResponse(json.dumps([api_policy]), 200),
        )
        output = entrypoint_read(_source(config), config, catalog, StateBuilder().build())

    assert not output.errors
    records = [message.record.data for message in output.records]
    assert len(records) == 1
    assert records[0]["id"] == expected_id
    assert type(records[0]["id"]) is int
    assert records[0]["applicable_to"]["group_ids"] == expected_group_ids
    assert all(type(group_id) is int for group_id in records[0]["applicable_to"]["group_ids"])
