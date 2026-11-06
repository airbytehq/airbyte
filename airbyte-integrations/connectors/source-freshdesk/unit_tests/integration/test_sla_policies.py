# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

from config_builder import ConfigBuilder
from jsonschema import validate

from airbyte_cdk import SyncMode, YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import discover, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_SOURCE_PATH = Path("/airbyte/integration_code/source_declarative_manifest")
_MANIFEST_PATH = (_SOURCE_PATH if _SOURCE_PATH.exists() else Path(__file__).parents[2]) / "manifest.yaml"
_DOMAIN = "any-domain.freshdesk.com"


def test_sla_policy_ids_match_discovered_schema() -> None:
    config = ConfigBuilder().domain(_DOMAIN).build()
    catalog = CatalogBuilder().with_stream("sla_policies", SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(path_to_yaml=str(_MANIFEST_PATH), catalog=catalog, config=config)
    discovered_catalog = discover(source, config).catalog.catalog
    assert discovered_catalog is not None
    schema = next(stream.json_schema for stream in discovered_catalog.streams if stream.name == "sla_policies")
    first_page = [
        {"id": "67000087191", "name": "Standard", "active": True},
        {"id": 67000087192, "name": "Priority", "active": False},
        {"id": None, "name": "Null ID"},
    ]
    second_page = [
        {"id": "9007199254740993", "name": "Large ID"},
        {"name": "Missing ID"},
        {"id": "0", "name": "Zero ID"},
    ]
    first_request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100"})
    second_request = HttpRequest(f"https://{_DOMAIN}/api/v2/sla_policies", query_params={"per_page": "100", "page": "2"})

    with HttpMocker() as http_mocker:
        http_mocker.get(
            first_request,
            HttpResponse(
                json.dumps(first_page),
                headers={"Link": f'<https://{_DOMAIN}/api/v2/sla_policies?per_page=100&page=2>; rel="next"'},
            ),
        )
        http_mocker.get(second_request, HttpResponse(json.dumps(second_page)))

        output = read(source, config, catalog)
        http_mocker.assert_number_of_calls(first_request, 1)
        http_mocker.assert_number_of_calls(second_request, 1)

    assert not output.errors
    records = []
    for message in output.records:
        assert message.record is not None
        records.append(message.record.data)
    assert records == [
        {"id": 67000087191, "name": "Standard", "active": True},
        first_page[1],
        {"name": "Null ID"},
        {"id": 9007199254740993, "name": "Large ID"},
        second_page[1],
        {"id": 0, "name": "Zero ID"},
    ]
    for record in records:
        validate(record, schema)
        if record.get("id") is not None:
            assert type(record["id"]) is int
