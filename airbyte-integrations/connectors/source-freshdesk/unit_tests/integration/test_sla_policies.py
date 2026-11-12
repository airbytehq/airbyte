# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import sys
from pathlib import Path

from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_DOMAIN = "a-domain.freshdesk.com"
_SOURCE_FOLDER_PATH = Path(__file__).parent.parent.parent
_YAML_FILE_PATH = _SOURCE_FOLDER_PATH / "manifest.yaml"

sys.path.append(str(_SOURCE_FOLDER_PATH))


def test_string_ids_are_emitted_as_integers() -> None:
    policies = [
        {
            "id": "67000087191",
            "name": "Default SLA Policy",
            "position": "1",
            "applicable_to": {"group_ids": ["67000012345"]},
            "escalation": {"response": {"escalation_time": "3600", "agent_ids": ["67000054321"]}},
        },
        {"id": 67000087192, "name": "VIP", "position": 2, "applicable_to": {"group_ids": [67000012346]}},
    ]
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    state = StateBuilder().build()
    request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})

    with HttpMocker() as http_mocker:
        http_mocker.get(request, HttpResponse(json.dumps(policies), 200))
        source = YamlDeclarativeSource(path_to_yaml=str(_YAML_FILE_PATH), catalog=catalog, config=config, state=state)
        output = entrypoint_read(source, config, catalog, state)
        http_mocker.assert_number_of_calls(request, 1)

    assert not output.errors
    records = [message.record.data for message in output.records]
    assert [record["id"] for record in records] == [67000087191, 67000087192]
    assert [record["position"] for record in records] == [1, 2]
    assert [record["applicable_to"]["group_ids"] for record in records] == [[67000012345], [67000012346]]
    assert records[0]["escalation"]["response"] == {"escalation_time": 3600, "agent_ids": [67000054321]}
