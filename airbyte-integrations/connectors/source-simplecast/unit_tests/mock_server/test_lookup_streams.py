# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json
import logging
from collections import Counter
from itertools import islice

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.mock_http.request import ANY_QUERY_PARAMS


@pytest.mark.parametrize("stream", ["categories", "distribution_channels"])
@pytest.mark.parametrize("record_count", [3, 0])
def test_lookup_stream_is_read_once(stream: str, record_count: int) -> None:
    config = {"api_token": "test-token"}
    records = [{"id": str(index), "name": f"Lookup {index}"} for index in range(record_count)]
    catalog = CatalogBuilder().with_stream(stream, SyncMode.full_refresh).build()
    request = HttpRequest(f"https://api.simplecast.com/{stream}", query_params=ANY_QUERY_PARAMS)

    with HttpMocker() as mocker:
        mocker.get(request, HttpResponse(json.dumps({"collection": records}), 200))
        # Bound consumption so a repeating full page cannot keep the test running forever.
        messages = list(islice(get_source(config).read(logging.getLogger(__name__), config, catalog), 10))

        mocker.assert_number_of_calls(request, 1)
        assert Counter(message.record.data["id"] for message in messages if message.type == Type.RECORD) == Counter(
            record["id"] for record in records
        )
        assert not any(message.type == Type.TRACE and message.trace.error for message in messages)
