# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path
from typing import Any

import pytest
from config_builder import ConfigBuilder

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.entrypoint_wrapper import read as entrypoint_read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_MANIFEST_PATH = Path(__file__).parent.parent.parent / "manifest.yaml"
_URL = "https://a-domain.freshdesk.com/api/v2/sla_policies"


def _read() -> EntrypointOutput:
    config = ConfigBuilder().domain("a-domain.freshdesk.com").build()
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    state = StateBuilder().build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config, state=state)
    return entrypoint_read(source, config, catalog, state)


def test_sla_policy_ids_are_integers_across_pages() -> None:
    first_page = HttpRequest(_URL, query_params={"per_page": "100"})
    second_page = HttpRequest(_URL, query_params={"per_page": "100", "page": "2"})
    with HttpMocker() as http_mocker:
        http_mocker.get(
            first_page,
            HttpResponse(
                json.dumps([{"id": "67000087191"}, {"id": 67000087193}]),
                200,
                headers={"link": f'<{_URL}?per_page=100&page=2>; rel="next"'},
            ),
        )
        http_mocker.get(second_page, HttpResponse(json.dumps([{"id": "67000087192"}]), 200))

        output = _read()
        http_mocker.assert_number_of_calls(first_page, 1)
        http_mocker.assert_number_of_calls(second_page, 1)

    assert not output.errors
    ids = [message.record.data["id"] for message in output.records]
    assert all(isinstance(policy_id, int) for policy_id in ids), ids
    assert ids == [67000087191, 67000087193, 67000087192]


@pytest.mark.parametrize("records", ([], [{"name": "Policy", "id": None}], [{"name": "Policy"}]))
def test_sla_policies_empty_or_absent_ids_are_not_cast(records: list[dict[str, Any]]) -> None:
    with HttpMocker() as http_mocker:
        http_mocker.get(HttpRequest(_URL, query_params={"per_page": "100"}), HttpResponse(json.dumps(records), 200))

        output = _read()

    assert not output.errors
    assert len(output.records) == len(records)
    assert all(message.record.data.get("id") is None for message in output.records)
