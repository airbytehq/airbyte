# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_BASE_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"
_LATEST = "2026-10-14T09:41:55.568082Z"


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("empty", [False, True])
def test_incremental_state(stream_name, empty):
    records = [] if empty else [
        {"id": "older", "modified_at": "2026-10-13T09:41:55Z"},
        {"id": "newer", "modified_at": "2026-10-14T09:41:55.568082659Z"},
    ]
    with HttpMocker() as mocker:
        mocker.get(
            HttpRequest(_BASE_URL, query_params={"page": "1", "per_page": "20"}),
            HttpResponse(json.dumps({"apps": records if stream_name == "applications" else [{"id": "app1"}]})),
        )
        if stream_name != "applications":
            mocker.get(
                HttpRequest(f"{_BASE_URL}/app1/{stream_name}", query_params={"page": "1", "per_page": "100"}),
                HttpResponse(json.dumps({stream_name: records})),
            )
        catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert len(output.records) == len(records)
    state = vars(output.most_recent_state.stream_state)
    if stream_name != "applications":
        partition = next(partition for partition in state["states"] if partition["partition"]["app_id"] == "app1")
        state = partition["cursor"]
    assert state["modified_at"] == ("2026-01-01T00:00:00.000000Z" if empty else _LATEST)
    if not empty:
        assert output.records[-1].record.data["modified_at"] == _LATEST
