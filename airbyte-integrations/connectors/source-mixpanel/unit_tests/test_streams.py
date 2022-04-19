#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_mixpanel.source import (
    Annotations,
    EngageSchema,
    Export,
    ExportSchema,
    Funnels,
    FunnelsList,
    IncrementalMixpanelStream,
    MixpanelStream,
    Revenue,
)

from .utils import get_url_to_mock, setup_response

logger = AirbyteLogger()


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(MixpanelStream, "path", "v0/example_endpoint")
    mocker.patch.object(MixpanelStream, "primary_key", "test_primary_key")
    mocker.patch.object(MixpanelStream, "__abstractmethods__", set())


@pytest.fixture
def patch_incremental_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(IncrementalMixpanelStream, "path", "v0/example_endpoint")
    mocker.patch.object(IncrementalMixpanelStream, "primary_key", "test_primary_key")
    mocker.patch.object(IncrementalMixpanelStream, "cursor_field", "date")
    mocker.patch.object(IncrementalMixpanelStream, "__abstractmethods__", set())


def test_url_base(patch_base_class):
    stream = MixpanelStream(authenticator=MagicMock())

    assert stream.url_base == "https://mixpanel.com/api/2.0/"


def test_request_headers(patch_base_class):
    stream = MixpanelStream(authenticator=MagicMock())

    assert stream.request_headers(stream_state={}) == {"Accept": "application/json"}


def test_updated_state(patch_incremental_base_class):
    stream = IncrementalMixpanelStream(authenticator=MagicMock())

    updated_state = stream.get_updated_state(
        current_stream_state={"date": "2021-01-25T00:00:00Z"}, latest_record={"date": "2021-02-25T00:00:00Z"}
    )

    assert updated_state == {"date": "2021-02-25T00:00:00Z"}


def test_cohorts_stream():
    # tested in itaseskii:mixpanel-incremental-syncs
    return None


@pytest.fixture
def funnels_list_response():
    return setup_response(200, [{"funnel_id": 1, "name": "Signup funnel"}])


def test_funnels_list_stream(requests_mock, config, funnels_list_response):
    stream = FunnelsList(authenticator=MagicMock(), **config)
    requests_mock.register_uri("GET", get_url_to_mock(stream), funnels_list_response)

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 1


@pytest.fixture
def funnels_list_url(config):
    funnel_list = FunnelsList(authenticator=MagicMock(), **config)
    return get_url_to_mock(funnel_list)


@pytest.fixture
def funnels_response():
    return setup_response(
        200,
        {
            "meta": {"dates": ["2016-09-12" "2016-09-19" "2016-09-26"]},
            "data": {
                "2016-09-12": {
                    "steps": [],
                    "analysis": {
                        "completion": 20524,
                        "starting_amount": 32688,
                        "steps": 2,
                        "worst": 1,
                    },
                },
                "2016-09-19": {
                    "steps": [],
                    "analysis": {
                        "completion": 20500,
                        "starting_amount": 34750,
                        "steps": 2,
                        "worst": 1,
                    },
                },
            },
        },
    )


def test_funnels_stream(requests_mock, config, funnels_response, funnels_list_response, funnels_list_url):
    stream = Funnels(authenticator=MagicMock(), **config)
    requests_mock.register_uri("GET", funnels_list_url, funnels_list_response)
    requests_mock.register_uri("GET", get_url_to_mock(stream), funnels_response)

    stream_slices = stream.stream_slices(sync_mode=SyncMode.incremental)

    records_arr = []
    for stream_slice in stream_slices:
        records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)
        for record in records:
            records_arr.append(record)

    assert len(records_arr) == 4


@pytest.fixture
def engage_schema_response():
    return setup_response(
        200,
        {
            "results": {
                "$browser": {"count": 124, "type": "string"},
                "$browser_version": {"count": 124, "type": "string"},
                "$created": {"count": 124, "type": "string"},
            }
        },
    )


def test_engage_schema(requests_mock, engage_schema_response):

    stream = EngageSchema(authenticator=MagicMock())
    requests_mock.register_uri("GET", get_url_to_mock(stream), engage_schema_response)

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 3


@pytest.fixture
def annotations_response():
    return setup_response(
        200,
        {
            "annotations": [
                {"id": 640999, "project_id": 2117889, "date": "2021-06-16 00:00:00", "description": "Looks good"},
                {"id": 640000, "project_id": 2117889, "date": "2021-06-16 00:00:00", "description": "Looks bad"},
            ]
        },
    )


def test_annotations_stream(requests_mock, annotations_response):

    stream = Annotations(authenticator=MagicMock())
    requests_mock.register_uri("GET", get_url_to_mock(stream), annotations_response)

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 2


@pytest.fixture
def revenue_response():
    return setup_response(
        200,
        {
            "computed_at": "2021-07-03T12:43:48.889421+00:00",
            "results": {
                "$overall": {"amount": 0.0, "count": 124, "paid_count": 0},
                "2021-06-01": {"amount": 0.0, "count": 124, "paid_count": 0},
                "2021-06-02": {"amount": 0.0, "count": 124, "paid_count": 0},
            },
            "session_id": "162...",
            "status": "ok",
        },
    )


def test_revenue_stream(requests_mock, revenue_response):

    stream = Revenue(authenticator=MagicMock())
    requests_mock.register_uri("GET", get_url_to_mock(stream), revenue_response)

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 2


@pytest.fixture
def export_schema_response():
    return setup_response(
        200,
        {
            "$browser": {"count": 6},
            "$browser_version": {"count": 6},
            "$current_url": {"count": 6},
            "mp_lib": {"count": 6},
            "noninteraction": {"count": 6},
            "$event_name": {"count": 6},
            "$duration_s": {},
            "$event_count": {},
            "$origin_end": {},
            "$origin_start": {},
        },
    )


def test_export_schema(requests_mock, export_schema_response):

    stream = ExportSchema(authenticator=MagicMock())
    requests_mock.register_uri("GET", get_url_to_mock(stream), export_schema_response)

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 10


@pytest.fixture
def export_response():
    return setup_response(
        200,
        {
            "event": "Viewed E-commerce Page",
            "properties": {
                "time": 1623860880,
                "distinct_id": "1d694fd9-31a5-4b99-9eef-ae63112063ed",
                "$browser": "Chrome",
                "$browser_version": "91.0.4472.101",
                "$current_url": "https://unblockdata.com/solutions/e-commerce/",
                "$insert_id": "c5eed127-c747-59c8-a5ed-d766f48e39a4",
                "$mp_api_endpoint": "api.mixpanel.com",
                "mp_lib": "Segment: analytics-wordpress",
                "mp_processing_time_ms": 1623886083321,
                "noninteraction": True,
            },
        },
    )


def test_export_stream(requests_mock, export_response):

    stream = Export(authenticator=MagicMock())
    requests_mock.register_uri("GET", get_url_to_mock(stream), export_response)

    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 1
