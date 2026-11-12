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


_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(_SOURCE_FOLDER_PATH))


@pytest.mark.parametrize("id_type", (str, int))
def test_sla_policy_ids_are_integers(id_type: type) -> None:
    expected_ids = [67000087191, 67000087192]
    policies = [{"id": id_type(policy_id), "name": f"Policy {index}"} for index, policy_id in enumerate(expected_ids)]
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    config = ConfigBuilder().domain("a-domain.freshdesk.com").build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_SOURCE_FOLDER_PATH / "manifest.yaml"), catalog=catalog, config=config, state=state)
    request = HttpRequest("https://a-domain.freshdesk.com/api/v2/sla_policies", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(policies), 200))
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    actual_ids = [record.record.data["id"] for record in output.records]
    assert actual_ids == expected_ids
    assert all(type(policy_id) is int for policy_id in actual_ids)
