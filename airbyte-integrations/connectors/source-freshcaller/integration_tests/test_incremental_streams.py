#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pendulum
import pytest
from airbyte_cdk.models import SyncMode
from source_freshcaller.streams import APIIncrementalFreshcallerStream, CallMetrics, Calls


@pytest.fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(APIIncrementalFreshcallerStream, "cursor_field", "created_time")
    mocker.patch.object(APIIncrementalFreshcallerStream, "__abstractmethods__", set())


@pytest.fixture
def args():
    return {"authenticator": None, "config": {"api_key": "", "domain": "airbyte", "start_date": "2021-01-01T00:00:00.000Z"}}


@pytest.fixture
def stream(patch_incremental_base_class, args):
    return APIIncrementalFreshcallerStream(**args)


@pytest.fixture
def call_metrics_stream(args):
    return CallMetrics(**args)


@pytest.fixture
def calls_stream(args):
    return Calls(**args)


@pytest.fixture
def streams_dict(calls_stream, call_metrics_stream):
    return {"calls_stream": calls_stream, "call_metrics_stream": call_metrics_stream}


@pytest.mark.parametrize("fixture_name, expected", [("calls_stream", "created_time"), ("call_metrics_stream", "created_time")])
def test_cursor_field(streams_dict, fixture_name, expected):
    stream = streams_dict[fixture_name]
    assert stream.cursor_field == expected


@pytest.mark.parametrize("fixture_name", [("calls_stream"), ("call_metrics_stream")])
def test_get_updated_state(streams_dict, fixture_name):
    stream = streams_dict[fixture_name]
    inputs = {
        "current_stream_state": {"created_time": "2021-10-10T00:00:00.00Z"},
        "latest_record": {"created_time": "2021-10-20T00:00:00.00Z"},
    }
    state = stream.get_updated_state(**inputs)
    assert state["created_time"] == pendulum.parse("2021-10-20T00:00:00.00Z")

    inputs = {"current_stream_state": state, "latest_record": {"created_time": "2021-10-30T00:00:00.00Z"}}
    state = stream.get_updated_state(**inputs)
    assert state["created_time"] == pendulum.parse("2021-10-30T00:00:00.00Z")


@pytest.mark.parametrize("fixture_name", [("calls_stream"), ("call_metrics_stream")])
def test_get_updated_state_2(streams_dict, fixture_name):
    stream = streams_dict[fixture_name]
    current_stream_state = {"created_time": pendulum.now().add(days=-40)}
    inputs = {"sync_mode": SyncMode.incremental, "cursor_field": [], "stream_state": current_stream_state}
    # The number of slices should be total lookback days by window_in_days i.e., 40 / 5 = 8
    assert len(stream.stream_slices(**inputs)) == 8


def test_end_of_stream_state(calls_stream, requests_mock):
    stream = calls_stream
    requests_mock.get(
        "https://airbyte.freshcaller.com/api/v1/calls?per_page=1000",
        json={
            "calls": [{"created_time": "2021-10-30T00:00:00.00Z"}, {"created_time": "2021-10-29T00:00:00.00Z"}],
            "meta": {"total_pages": 40, "current": 40},
        },
    )

    state = {"created_time": "2021-10-01T00:00:00.00Z"}
    sync_mode = SyncMode.incremental
    last_state = None
    for idx, app_slice in enumerate(stream.stream_slices(state, **MagicMock())):
        for record in stream.read_records(sync_mode=sync_mode, stream_slice=app_slice):
            state = stream.get_updated_state(state, record)
            last_state = state["created_time"]
    assert last_state == pendulum.parse("2021-10-30T00:00:00.00Z")


@pytest.mark.parametrize("fixture_name", [("calls_stream"), ("call_metrics_stream")])
def test_supports_incremental(mocker, streams_dict, fixture_name):
    stream = streams_dict[fixture_name]
    mocker.patch.object(APIIncrementalFreshcallerStream, "cursor_field", "dummy_field")
    assert stream.supports_incremental


@pytest.mark.parametrize("fixture_name", [("calls_stream"), ("call_metrics_stream")])
def test_source_defined_cursor(mocker, streams_dict, fixture_name):
    stream = streams_dict[fixture_name]
    assert stream.source_defined_cursor


@pytest.mark.parametrize("fixture_name", [("calls_stream"), ("call_metrics_stream")])
def test_stream_checkpoint_interval(mocker, streams_dict, fixture_name):
    stream = streams_dict[fixture_name]
    expected_checkpoint_interval = None
    assert stream.state_checkpoint_interval == expected_checkpoint_interval


@pytest.mark.parametrize("fixture_name", [("calls_stream"), ("call_metrics_stream")])
def test_request_params(mocker, streams_dict, fixture_name):
    stream = streams_dict[fixture_name]
    inputs = {
        "stream_state": {},
        "next_page_token": {"page": "5"},
        "stream_slice": {"by_time[from]": "2022-03-04 18:27:40", "by_time[to]": "2022-03-09 18:27:39"},
    }
    expected_request_params = {"per_page": 1000, "page": "5", "by_time[from]": "2022-03-04 18:27:40", "by_time[to]": "2022-03-09 18:27:39"}
    if stream.path() == "calls":
        expected_request_params.update({"has_ancestry": "true"})
    assert stream.request_params(**inputs) == expected_request_params
