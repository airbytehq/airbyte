# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from unit_tests.conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


_CONFIG = {"api_token": "test-token"}
_STREAMS = ["categories", "distribution_channels"]


@pytest.mark.parametrize("stream_name", _STREAMS)
def test_read_unpaginated_stream_once(stream_name):
    if stream_name == "categories":
        records = [{"value": str(i), "label": f"Category {i}", "rss_label": f"Category {i}"} for i in range(19)]
    else:
        records = [{"id": str(i), "name": f"Channel {i}"} for i in range(4)]

    request = HttpRequest(url=f"https://api.simplecast.com/{stream_name}", query_params=ANY_QUERY_PARAMS)
    with HttpMocker() as http_mocker:
        # A terminal error bounds the regression: requests-mock repeats its last response.
        http_mocker.get(
            request,
            [
                HttpResponse(body=json.dumps({"collection": records}), status_code=200),
                HttpResponse(body=json.dumps({"error": "Unexpected repeated request"}), status_code=400),
            ],
        )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

        http_mocker.assert_number_of_calls(request, 1)
        assert not output.errors
        assert [message.record.data for message in output.records] == records
        assert all(message.record.stream == stream_name for message in output.records)
