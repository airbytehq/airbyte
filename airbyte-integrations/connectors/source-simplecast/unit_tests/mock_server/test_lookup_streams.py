# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
from urllib.parse import parse_qs, urlparse

import pytest

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS

from ..conftest import get_source


@pytest.mark.parametrize(
    "stream, id_field, record_count",
    [("categories", "value", 19), ("distribution_channels", "id", 5)],
)
@pytest.mark.parametrize("empty", [False, True], ids=["full-list", "empty-list"])
def test_read_lookup_once(stream: str, id_field: str, record_count: int, empty: bool) -> None:
    expected_ids = [] if empty else [str(index) for index in range(record_count)]
    records = [{id_field: record_id, "label": record_id, "name": record_id} for record_id in expected_ids]
    response = HttpResponse(json.dumps({"collection": records}), 200)
    request = HttpRequest(f"https://api.simplecast.com/{stream}", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        # Repeat the full list regardless of offset; the empty sentinel bounds a broken paginator.
        http_mocker.get(request, [response, response, HttpResponse(json.dumps({"collection": []}), 200)])
        config = {"api_token": "test-token"}
        catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
        output = read(get_source(config), config, catalog)

        assert sorted(record.record.data[id_field] for record in output.records) == sorted(expected_ids)
        http_mocker.assert_number_of_calls(request, 1)
        sent_requests = http_mocker._mocker.request_history
        assert len(sent_requests) == 1
        assert "offset" not in parse_qs(urlparse(sent_requests[0].url).query)
        assert output.errors == []
