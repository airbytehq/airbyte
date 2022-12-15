#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from datetime import timedelta
from unittest.mock import MagicMock

import pendulum
import pytest
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from source_mixpanel.streams import (
    Annotations,
    CohortMembers,
    Cohorts,
    Engage,
    EngageSchema,
    Export,
    ExportSchema,
    Funnels,
    FunnelsList,
    IncrementalMixpanelStream,
    MixpanelStream,
    Revenue,
)
from source_mixpanel.utils import read_full_refresh

from .utils import get_url_to_mock, read_incremental, setup_response

logger = AirbyteLogger()

MIXPANEL_BASE_URL = "https://mixpanel.com/api/2.0/"


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


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


def test_url_base(patch_base_class, config):
    stream = MixpanelStream(authenticator=MagicMock(), **config)

    assert stream.url_base == "https://mixpanel.com/api/2.0/"


def test_request_headers(patch_base_class, config):
    stream = MixpanelStream(authenticator=MagicMock(), **config)

    assert stream.request_headers(stream_state={}) == {"Accept": "application/json"}


def test_updated_state(patch_incremental_base_class, config):
    stream = IncrementalMixpanelStream(authenticator=MagicMock(), **config)

    updated_state = stream.get_updated_state(
        current_stream_state={"date": "2021-01-25T00:00:00Z"}, latest_record={"date": "2021-02-25T00:00:00Z"}
    )

    assert updated_state == {"date": "2021-02-25T00:00:00Z"}


@pytest.fixture
def cohorts_response():
    return setup_response(
        200,
        [
            {
                "count": 150,
                "is_visible": 1,
                "description": "This cohort is visible, has an id = 1000, and currently has 150 users.",
                "created": "2019-03-19 23:49:51",
                "project_id": 1,
                "id": 1000,
                "name": "Cohort One",
            },
            {
                "count": 25,
                "is_visible": 0,
                "description": "This cohort isn't visible, has an id = 2000, and currently has 25 users.",
                "created": "2019-04-02 23:22:01",
                "project_id": 1,
                "id": 2000,
                "name": "Cohort Two",
            },
        ],
    )


def test_cohorts_stream_incremental(requests_mock, cohorts_response, config):
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "cohorts/list", cohorts_response)

    stream = Cohorts(authenticator=MagicMock(), **config)

    records = read_incremental(stream, stream_state={"created": "2019-04-02 23:22:01"}, cursor_field=["created"])

    records_length = sum(1 for _ in records)
    assert records_length == 1


@pytest.fixture
def engage_response():
    return setup_response(
        200,
        {
            "page": 0,
            "page_size": 1000,
            "session_id": "1234567890-EXAMPL",
            "status": "ok",
            "total": 2,
            "results": [
                {
                    "$distinct_id": "9d35cd7f-3f06-4549-91bf-198ee58bb58a",
                    "$properties": {
                        "$created": "2008-12-12T11:20:47",
                        "$browser": "Chrome",
                        "$browser_version": "83.0.4103.116",
                        "$email": "clark@asw.com",
                        "$first_name": "Clark",
                        "$last_name": "Kent",
                        "$name": "Clark Kent",
                    },
                },
                {
                    "$distinct_id": "cd9d357f-3f06-4549-91bf-158bb598ee8a",
                    "$properties": {
                        "$created": "2008-11-12T11:20:47",
                        "$browser": "Firefox",
                        "$browser_version": "83.0.4103.116",
                        "$email": "bruce@asw.com",
                        "$first_name": "Bruce",
                        "$last_name": "Wayne",
                        "$name": "Bruce Wayne",
                    },
                },
            ],
        },
    )


def test_engage_stream_incremental(requests_mock, engage_response, config):
    requests_mock.register_uri("POST", MIXPANEL_BASE_URL + "engage?page_size=1000", engage_response)

    stream = Engage(authenticator=MagicMock(), **config)

    stream_state = {"created": "2008-12-12T11:20:47"}
    records = list(read_incremental(stream, stream_state, cursor_field=["created"]))

    assert len(records) == 1
    assert stream.get_updated_state(current_stream_state=stream_state, latest_record=records[-1]) == {"created": "2008-12-12T11:20:47"}


def test_cohort_members_stream_incremental(requests_mock, engage_response, cohorts_response, config):
    requests_mock.register_uri("POST", MIXPANEL_BASE_URL + "engage?page_size=1000", engage_response)
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "cohorts/list", cohorts_response)

    stream = CohortMembers(authenticator=MagicMock(), **config)
    stream.set_cursor(["created"])
    stream_state = {"created": "2008-12-12T11:20:47"}
    records = stream.read_records(
        sync_mode=SyncMode.incremental, cursor_field=["created"], stream_state=stream_state, stream_slice={"id": 1000}
    )

    records = [item for item in records]
    assert len(records) == 1
    assert stream.get_updated_state(current_stream_state=stream_state, latest_record=records[-1]) == {"created": "2008-12-12T11:20:47"}


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
def funnels_response(start_date):
    first_date = start_date + timedelta(days=1)
    second_date = start_date + timedelta(days=10)
    return setup_response(
        200,
        {
            "meta": {"dates": [str(first_date), str(second_date)]},
            "data": {
                str(first_date): {
                    "steps": [],
                    "analysis": {
                        "completion": 20524,
                        "starting_amount": 32688,
                        "steps": 2,
                        "worst": 1,
                    },
                },
                str(second_date): {
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
    last_record = records_arr[-1]
    # Test without current state date
    new_state = stream.get_updated_state(current_stream_state={}, latest_record=records_arr[-1])
    assert new_state == {str(last_record["funnel_id"]): {"date": last_record["date"]}}

    # Test with current state, that lesser than last record date
    last_record_date = pendulum.parse(last_record["date"]).date()
    new_state = stream.get_updated_state(
        current_stream_state={str(last_record["funnel_id"]): {"date": str(last_record_date - timedelta(days=1))}},
        latest_record=records_arr[-1],
    )
    assert new_state == {str(last_record["funnel_id"]): {"date": last_record["date"]}}

    # Test with current state, that is greater, than last record date
    new_state = stream.get_updated_state(
        current_stream_state={str(last_record["funnel_id"]): {"date": str(last_record_date + timedelta(days=1))}},
        latest_record=records_arr[-1],
    )
    assert new_state == {str(last_record["funnel_id"]): {"date": str(last_record_date + timedelta(days=1))}}


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


def test_engage_schema(requests_mock, engage_schema_response, config):

    stream = EngageSchema(authenticator=MagicMock(), **config)
    requests_mock.register_uri("GET", get_url_to_mock(stream), engage_schema_response)

    records = stream.read_records(sync_mode=SyncMode.full_refresh)

    records_length = sum(1 for _ in records)
    assert records_length == 3


def test_update_engage_schema(requests_mock, config):
    stream = EngageSchema(authenticator=MagicMock(), **config)
    requests_mock.register_uri(
        "GET",
        get_url_to_mock(stream),
        setup_response(
            200,
            {
                "results": {
                    "$someNewSchemaField": {"count": 124, "type": "string"},
                }
            },
        ),
    )
    engage_stream = Engage(authenticator=MagicMock(), **config)
    engage_schema = engage_stream.get_json_schema()
    assert "someNewSchemaField" in engage_schema["properties"]


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


def test_annotations_stream(requests_mock, annotations_response, config):

    stream = Annotations(authenticator=MagicMock(), **config)
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


def test_revenue_stream(requests_mock, revenue_response, config):

    stream = Revenue(authenticator=MagicMock(), **config)
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


def test_export_schema(requests_mock, export_schema_response, config):

    stream = ExportSchema(authenticator=MagicMock(), **config)
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
                "time": 1623860880,  # 2021-06-16T16:28:00
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


def test_export_stream(requests_mock, export_response, config):

    stream = Export(authenticator=MagicMock(), **config)
    requests_mock.register_uri("GET", get_url_to_mock(stream), export_response)
    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 1


def test_export_stream_request_params(config):
    stream = Export(authenticator=MagicMock(), **config)
    stream_slice = {"start_date": "2017-01-25T00:00:00Z", "end_date": "2017-02-25T00:00:00Z"}
    stream_state = {"date": "2021-06-16T17:00:00"}

    request_params = stream.request_params(stream_state=None, stream_slice=stream_slice)
    assert "where" not in request_params

    request_params = stream.request_params(stream_state={}, stream_slice=stream_slice)
    assert "where" not in request_params

    request_params = stream.request_params(stream_state=stream_state, stream_slice=stream_slice)
    assert "where" in request_params
    timestamp = int(pendulum.parse("2021-06-16T17:00:00Z").timestamp())
    assert request_params.get("where") == f'properties["$time"]>=datetime({timestamp})'


def test_export_terminated_early(requests_mock, config):
    stream = Export(authenticator=MagicMock(), **config)
    requests_mock.register_uri("GET", get_url_to_mock(stream), text="terminated early\n")
    assert list(read_full_refresh(stream)) == []


def test_export_iter_dicts(config):
    stream = Export(authenticator=MagicMock(), **config)
    record = {"key1": "value1", "key2": "value2"}
    record_string = json.dumps(record)
    assert list(stream.iter_dicts([record_string, record_string])) == [record, record]
    # combine record from 2 standing nearby parts
    assert list(stream.iter_dicts([record_string, record_string[:2], record_string[2:], record_string])) == [record, record, record]
    # drop record parts because they are not standing nearby
    assert list(stream.iter_dicts([record_string, record_string[:2], record_string, record_string[2:]])) == [record, record]
