# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path
from typing import Any, Optional

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_STREAM_NAME = "sla_policies"

_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def _read() -> EntrypointOutput:
    catalog = CatalogBuilder().with_stream(_STREAM_NAME, SyncMode.full_refresh).build()
    config = ConfigBuilder().domain(_DOMAIN).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def _sla_policy(policy_id: Any) -> dict:
    return {
        "id": policy_id,
        "name": "Default SLA Policy",
        "description": "default policy",
        "active": True,
        "is_default": True,
        "position": 1,
    }


@pytest.mark.parametrize(
    "api_id, expected_id",
    (
        pytest.param("67000087191", 67000087191, id="string_id_is_cast_to_integer"),
        pytest.param(67000087191, 67000087191, id="integer_id_is_unchanged"),
        pytest.param(None, None, id="null_id_is_unchanged"),
    ),
)
def test_sla_policy_id_is_emitted_as_integer(api_id: Any, expected_id: Optional[int]) -> None:
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})
    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps([_sla_policy(api_id)]), 200))

        output = _read()

    assert not output.errors
    assert len(output.records) == 1
    record_id = output.records[0].record.data.get("id")
    assert record_id == expected_id
    assert type(record_id) is type(expected_id)
