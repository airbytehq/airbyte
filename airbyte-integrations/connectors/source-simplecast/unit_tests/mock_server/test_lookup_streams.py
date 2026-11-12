# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import AirbyteStreamStatus, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


@pytest.mark.parametrize("stream_name,record_key", [("categories", "value"), ("distribution_channels", "id")])
@pytest.mark.parametrize("record_count", [0, 1, 19])
def test_lookup_emits_complete_collection_once(stream_name: str, record_key: str, record_count: int) -> None:
    config = {"api_token": "test-token"}
    records = [
        {record_key: f"lookup-{index}", "label" if stream_name == "categories" else "name": f"Lookup {index}"}
        for index in range(record_count)
    ]
    url = f"https://api.simplecast.com/{stream_name}"
    response = {"href": url, "collection": records}
    with requests_mock.Mocker() as mocker:
        # Repeat the complete collection as the API does when offset is ignored.
        # An empty fourth response bounds the unfixed connector's otherwise endless read.
        mocker.get(url, [{"json": response}] * 3 + [{"json": {"href": url, "collection": []}}])
        output = read(
            get_source(config),
            config=config,
            catalog=CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build(),
        )

    assert output.errors == []
    assert [message.record.data for message in output.records] == records
    assert [request.url for request in mocker.request_history] == [url]
    assert any(
        trace.trace.stream_status and trace.trace.stream_status.status == AirbyteStreamStatus.COMPLETE for trace in output.trace_messages
    )
