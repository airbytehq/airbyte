# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from pathlib import Path

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


CONFIG = {"api_token": "test-token"}

# Record counts mirror the API: more records than any page size the connector could assume.
LOOKUP_RECORDS = {
    "categories": [{"value": f"category-{index}", "label": f"Category {index}"} for index in range(19)],
    "distribution_channels": [{"id": f"channel-{index}", "name": f"Channel {index}"} for index in range(3)],
}


@pytest.mark.parametrize("stream_name", sorted(LOOKUP_RECORDS))
def test_lookup_stream_is_read_with_a_single_unpaginated_request(stream_name: str) -> None:
    records = LOOKUP_RECORDS[stream_name]
    # Exact match on an empty query string: any `offset` parameter leaves the request unmatched and fails the read.
    request = HttpRequest(
        f"https://api.simplecast.com/{stream_name}",
        query_params={},
        headers={"Authorization": "Bearer test-token"},
    )
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    source = YamlDeclarativeSource(
        path_to_yaml=str(Path(__file__).parents[2] / "manifest.yaml"),
        config=CONFIG,
        catalog=catalog,
        state=[],
    )

    with HttpMocker() as http_mocker:
        # The API returns the whole list on every call and carries no paging information.
        http_mocker.get(request, HttpResponse(json.dumps({"collection": records})))

        output = read(source, config=CONFIG, catalog=catalog, state=[])

        assert output.errors == []
        assert [record.record.data for record in output.records] == records
        http_mocker.assert_number_of_calls(request, 1)
