# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import AirbyteStateMessageSerializer, SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("fraction", ["904417302", "904417", "904"], ids=["nanoseconds", "microseconds", "milliseconds"])
def test_modified_at_advances_state(stream_name, fraction):
    config = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
    records = [
        {"id": "newest", "modified_at": f"2026-10-02T17:05:11.{fraction}Z"},
        {"id": "older", "modified_at": f"2026-10-01T17:05:11.{fraction}Z"},
    ]
    base_url = "https://api.clarifai.com/v2/users/test_user_id/apps"
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with HttpMocker() as mocker:
        if stream_name == "applications":
            url, response_key, page_size = base_url, "apps", "20"
        else:
            mocker.get(
                HttpRequest(url=base_url, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(json.dumps({"apps": [{"id": "app1"}]})),
            )
            url, response_key, page_size = f"{base_url}/app1/{stream_name}", stream_name, "100"
        mocker.get(
            HttpRequest(url=url, query_params={"page": "1", "per_page": page_size}),
            HttpResponse(json.dumps({response_key: records})),
        )
        output = read(get_source(config), config=config, catalog=catalog)

        previous_state = [output.state_messages[-1].state]
        resumed_output = read(get_source(config, previous_state), config=config, catalog=catalog, state=previous_state)

    expected_records = [dict(record, modified_at=record["modified_at"][:26] + "Z") for record in records] if len(fraction) > 6 else records
    assert [message.record.data for message in output.records] == expected_records
    assert (
        AirbyteStateMessageSerializer.dump(resumed_output.state_messages[-1].state)["stream"]["stream_state"]
        == (AirbyteStateMessageSerializer.dump(output.state_messages[-1].state)["stream"]["stream_state"])
    )
    state = AirbyteStateMessageSerializer.dump(output.state_messages[-1].state)["stream"]["stream_state"]
    if stream_name != "applications":
        assert state["states"][0]["partition"]["app_id"] == "app1"
        state = state["states"][0]["cursor"]
    assert state == {"modified_at": f"2026-10-02T17:05:11.{fraction[:6].ljust(6, '0')}Z"}


def test_missing_modified_at_is_not_populated():
    config = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
    records = [{"id": "missing"}, {"id": "null", "modified_at": None}, {"id": "empty", "modified_at": ""}]
    catalog = CatalogBuilder().with_stream("applications", SyncMode.full_refresh).build()
    with HttpMocker() as mocker:
        mocker.get(
            HttpRequest(url="https://api.clarifai.com/v2/users/test_user_id/apps", query_params={"page": "1", "per_page": "20"}),
            HttpResponse(json.dumps({"apps": records})),
        )
        output = read(get_source(config), config=config, catalog=catalog)

    assert not output.errors
    assert [message.record.data for message in output.records] == [
        {"id": "missing"},
        {"id": "null"},
        {"id": "empty", "modified_at": ""},
    ]
