#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import copy
import json
import logging
from pathlib import Path
from typing import Optional
from unittest.mock import Mock

import pendulum
import pytest
from requests_mock import Mocker
from source_zenloop import SourceZenloop
from source_zenloop.components import ZenloopPartitionRouter

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.types import StreamSlice


CONNECTOR_ROOT = Path(__file__).resolve().parents[1]
ANSWER_STREAMS = [("answers", "survey_id", "surveys"), ("answers_survey_group", "survey_group_id", "survey_groups")]


@pytest.mark.parametrize("config_field", ["survey_id", "survey_group_id"])
@pytest.mark.parametrize("parent_id", [None, "", "configured-parent"])
def test_partition_router(config_field: str, parent_id: Optional[str]) -> None:
    parent = Mock()
    parent.stream_slices.return_value = [StreamSlice(partition={}, cursor_slice={})]
    parent.read_records.return_value = [{"public_hash_id": "parent-1"}, {"public_hash_id": "parent-2"}]
    config = {config_field: parent_id}
    router = ZenloopPartitionRouter(
        parent_stream_configs=[
            ParentStreamConfig(stream=parent, parent_key="public_hash_id", partition_field="id", config=config, parameters={})
        ],
        config=config,
        parameters={"config_parent_field": config_field},
    )

    slices = list(router.stream_slices())

    ids = [parent_id] if parent_id else ["parent-1", "parent-2"]
    assert slices == [StreamSlice(partition={"id": value, "parent_slice": {}}, cursor_slice={}) for value in ids]
    if parent_id:
        parent.read_records.assert_not_called()
        parent.stream_slices.assert_not_called()
    else:
        parent.read_records.assert_called_once()


def test_discover() -> None:
    catalog = SourceZenloop().discover(logging.getLogger(), {"api_token": "test-token"})
    assert [stream.name for stream in catalog.streams] == ["surveys", "survey_groups", "properties", "answers", "answers_survey_group"]
    for stream in catalog.streams:
        if stream.name in {"answers", "answers_survey_group"}:
            assert stream.default_cursor_field == ["inserted_at"]
            assert stream.supported_sync_modes == [SyncMode.full_refresh, SyncMode.incremental]


@pytest.mark.parametrize("stream_name,config_field,parent_path", ANSWER_STREAMS)
def test_legacy_partition_state_resumes_and_advances(stream_name: str, config_field: str, parent_path: str, requests_mock: Mocker) -> None:
    sample_state = json.loads((CONNECTOR_ROOT / "integration_tests/sample_state.json").read_text())
    legacy_state = next(
        item["stream"]["stream_state"] for item in sample_state if item["stream"]["stream_descriptor"]["name"] == stream_name
    )
    parent_id = legacy_state["states"][0]["partition"]["id"]
    config = {"api_token": "test-token", config_field: parent_id, "date_from": "2021-08-01"}
    stream = next(stream for stream in SourceZenloop().streams(config) if stream.name == stream_name)
    stream.state = copy.deepcopy(legacy_state)
    assert stream.state == legacy_state
    slices = stream.stream_slices(sync_mode=SyncMode.incremental)
    first_slice = next(iter(slices))
    assert first_slice.partition == {"id": parent_id, "parent_slice": {}}
    assert first_slice.cursor_slice["start_time"] == "2021-08-18T08:35:49.540000Z"
    record = {"id": "answer-1", "inserted_at": "2021-08-20T09:00:00.000Z"}
    requests_mock.get(f"https://api.zenloop.com/v1/{parent_path}/{parent_id}/answers", json={"answers": [record]})
    assert [dict(item) for item in stream.read_records(sync_mode=SyncMode.incremental, stream_slice=first_slice)] == [record]
    assert stream.state == {
        "states": [{"partition": {"id": parent_id, "parent_slice": {}}, "cursor": {"inserted_at": record["inserted_at"]}}]
    }
    resumed_stream = next(stream for stream in SourceZenloop().streams(config) if stream.name == stream_name)
    resumed_stream.state = stream.state
    assert (
        next(iter(resumed_stream.stream_slices(sync_mode=SyncMode.incremental))).cursor_slice["start_time"] == "2021-08-20T09:00:00.000000Z"
    )


@pytest.mark.parametrize("stream_name,config_field,parent_path", ANSWER_STREAMS)
@pytest.mark.parametrize("date_from", [None, "", "2021-10-24", "2021-10-24T03:30:30Z"])
def test_date_from_compatibility(
    stream_name: str, config_field: str, parent_path: str, date_from: Optional[str], requests_mock: Mocker
) -> None:
    config = {"api_token": "test-token", config_field: "parent-1"}
    if date_from is not None:
        config["date_from"] = date_from
    stream = next(stream for stream in SourceZenloop().streams(config) if stream.name == stream_name)
    first_slice = next(iter(stream.stream_slices(sync_mode=SyncMode.incremental)))
    expected_start = "2021-10-24" if date_from else pendulum.today("UTC").to_date_string()
    assert first_slice.cursor_slice["start_time"] == f"{expected_start}T00:00:00.000000Z"
    requests_mock.get(f"https://api.zenloop.com/v1/{parent_path}/parent-1/answers", json={"answers": []})
    assert list(stream.read_records(sync_mode=SyncMode.incremental, stream_slice=first_slice)) == []
    assert requests_mock.last_request.qs["date_from"] == [f"{expected_start}t00:00:00.000000z"]
