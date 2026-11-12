# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@pytest.mark.parametrize("stream_name", ["categories", "distribution_channels"])
@pytest.mark.parametrize("records", [[{"id": "1", "name": "First"}, {"id": "2", "name": "Second"}, {"id": "3", "name": "Third"}], []])
def test_lookup_is_read_once(stream_name, records, requests_mock):
    def response(request, context):
        if requests_mock.call_count > 3:
            raise RuntimeError(f"Lookup endpoint repeatedly requested: {[request.url for request in requests_mock.request_history]}")
        return {"collection": records}

    requests_mock.get(f"https://api.simplecast.com/{stream_name}", json=response)
    config = {"api_token": "test-token"}
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()

    output = read(get_source(config), config=config, catalog=catalog)

    assert output.errors == []
    assert requests_mock.call_count == 1
    assert "offset" not in requests_mock.last_request.qs
    assert [message.record.data for message in output.records] == records
