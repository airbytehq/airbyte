# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import json

import pytest
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.models import AddFields
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_cdk.test.state_builder import StateBuilder


_CONFIG = {"api_key": "test_api_key", "user_id": "test_user_id", "start_date": "2026-01-01T00:00:00Z"}
_APPS_URL = "https://api.clarifai.com/v2/users/test_user_id/apps"


def _read_stream(stream_name, records, state=None):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()
    with HttpMocker() as mocker:
        if stream_name == "applications":
            mocker.get(
                HttpRequest(_APPS_URL, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(json.dumps({"apps": records})),
            )
        else:
            mocker.get(
                HttpRequest(_APPS_URL, query_params={"page": "1", "per_page": "20"}),
                HttpResponse(json.dumps({"apps": [{"id": "app1"}, {"id": "app2"}]})),
            )
            for app_id in ["app1", "app2"]:
                mocker.get(
                    HttpRequest(f"{_APPS_URL}/{app_id}/{stream_name}", query_params={"page": "1", "per_page": "100"}),
                    HttpResponse(json.dumps({stream_name: records})),
                )
        return read(get_source(_CONFIG, state), config=_CONFIG, catalog=catalog, state=state)


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
@pytest.mark.parametrize("fraction", ["904417", "9044173", "90441730", "904417302"])
def test_incremental_state_advances(stream_name, fraction):
    records = [
        {"id": "latest", "modified_at": f"2026-10-02T17:05:11.{fraction}Z"},
        {"id": "earlier", "modified_at": f"2026-10-01T17:05:11.{fraction}Z"},
    ]
    output = _read_stream(stream_name, records)
    state = output.most_recent_state.stream_state.__dict__
    expected = {"modified_at": "2026-10-02T17:05:11.904417Z"}
    if stream_name == "applications":
        assert state == expected
    else:
        assert {entry["partition"]["app_id"]: entry["cursor"] for entry in state["states"]} == {
            "app1": expected,
            "app2": expected,
        }
    expected_records = [{"id": record["id"], "modified_at": record["modified_at"].split(".")[0] + ".904417Z"} for record in records]
    assert [message.record.data for message in output.records] == expected_records * (1 if stream_name == "applications" else 2)

    resumed_state = StateBuilder().with_stream_state(stream_name, state).build()
    resumed_output = _read_stream(stream_name, records, resumed_state)
    # No request-side or client-side incremental filtering is configured for these streams.
    assert [message.record.data["id"] for message in resumed_output.records] == ["latest", "earlier"] * (
        1 if stream_name == "applications" else 2
    )
    assert resumed_output.most_recent_state.stream_state.__dict__ == state


@pytest.mark.parametrize("stream_name", ["applications", "datasets", "models"])
def test_empty_incremental_read(stream_name):
    output = _read_stream(stream_name, [])
    assert not output.records


@pytest.mark.parametrize(
    "record",
    [
        {"id": "missing"},
        {"id": "null", "modified_at": None},
        {"id": "seconds", "modified_at": "2026-10-02T17:05:11Z"},
        {"id": "milliseconds", "modified_at": "2026-10-02T17:05:11.904Z"},
        {"id": "microseconds", "modified_at": "2026-10-02T17:05:11.904417Z"},
    ],
)
def test_normalization_preserves_short_null_and_missing_cursors(record):
    transformation = ModelToComponentFactory().create_component(
        AddFields, get_source(_CONFIG).resolved_manifest["definitions"]["normalize_modified_at"], _CONFIG
    )
    original = dict(record)
    transformation.transform(record, config=_CONFIG)
    assert record == original
    output = _read_stream("applications", [record])
    assert [message.record.data for message in output.records] == [{key: value for key, value in record.items() if value is not None}]
