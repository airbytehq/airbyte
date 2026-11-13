# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from conftest import get_source
from freezegun import freeze_time

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker
from mock_server.config import ConfigBuilder
from mock_server.request_builder import BambooHrRequestBuilder
from mock_server.response_builder import response


@freeze_time("2026-11-10T00:00:00Z")
def test_saved_state_replays_365_days(http_mocker: HttpMocker) -> None:
    config = ConfigBuilder().with_start_date("2020-01-01T00:00:00Z").build()
    catalog = CatalogBuilder().with_stream("time_off_requests_stream", SyncMode.incremental).build()
    initial = (
        BambooHrRequestBuilder("time_off/requests/").with_query_param("start", "2020-01-01").with_query_param("end", "2026-11-10").build()
    )
    http_mocker.get(initial, response([{"id": "1", "created": "2026-11-05"}]))
    first = read(get_source(config), config, catalog)
    assert first.errors == []
    assert [message.record.data["id"] for message in first.records] == ["1"]
    assert first.most_recent_state.stream_state.created == "2026-11-05"
    state = [first.state_messages[-1].state]
    replay = (
        BambooHrRequestBuilder("time_off/requests/").with_query_param("start", "2025-11-05").with_query_param("end", "2026-11-10").build()
    )
    http_mocker.get(replay, response([{"id": "1", "created": "2026-11-05"}]))
    second = read(get_source(config, state), config, catalog, state=state)
    http_mocker.assert_number_of_calls(replay, 1)
    assert second.errors == []
    assert [message.record.data["id"] for message in second.records] == ["1"]
    assert second.most_recent_state.stream_state.created == "2026-11-05"
    http_mocker.assert_number_of_calls(initial, 1)
