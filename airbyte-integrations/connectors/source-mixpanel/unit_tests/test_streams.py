#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import urllib.parse
from datetime import timedelta
from unittest import mock

import pendulum
import pytest
import responses
import source_mixpanel
from source_mixpanel import SourceMixpanel
from source_mixpanel.components import iter_dicts
from source_mixpanel.utils import read_full_refresh

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http.http_client import MessageRepresentationAirbyteTracedErrors
from airbyte_cdk.test.entrypoint_wrapper import read

from .utils import get_url_to_mock, init_stream, read_incremental, setup_response


logger = logging.getLogger("airbyte")

MIXPANEL_BASE_URL = "https://mixpanel.com/api/query/"


@pytest.fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep", lambda x: None)
    yield time_mock


@pytest.fixture
def cohorts_response():
    return setup_response(
        200,
        [
            {
                "count": 150,
                "is_visible": 1,
                "description": "This cohort is visible, has an id = 1000, and currently has 150 users.",
                "created": "2022-01-01 23:49:51",
                "project_id": 1,
                "id": 1000,
                "name": "Cohort One",
            },
            {
                "count": 25,
                "is_visible": 0,
                "description": "This cohort isn't visible, has an id = 2000, and currently has 25 users.",
                "created": "2023-01-01 23:22:01",
                "project_id": 1,
                "id": 2000,
                "name": "Cohort Two",
            },
        ],
    )


def test_cohorts_stream_incremental(requests_mock, cohorts_response, config_raw):
    """Filter 1 old value, 1 new record should be returned"""
    config_raw["start_date"] = "2022-01-01T00:00:00Z"
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "cohorts/list", cohorts_response)

    cohorts_stream = init_stream("cohorts", config=config_raw)

    records = read_incremental(cohorts_stream, stream_state={"created": "2022-04-19 23:22:01"}, cursor_field=["created"])

    assert len(list(records)) == 1


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
                        "$created": "2024-02-01T11:20:47",
                        "$last_seen": "2024-02-01T11:20:47",
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
                        "$created": "2024-03-01T11:20:47",
                        "$last_seen": "2024-03-01T11:20:47",
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


def test_engage_stream_incremental(requests_mock, engage_response, config_raw):
    """Filter 1 old value, 1 new record should be returned"""
    engage_properties = {"results": {"$browser": {"count": 124, "type": "string"}, "$browser_version": {"count": 124, "type": "string"}}}
    config_raw["start_date"] = "2022-02-01T00:00:00Z"
    config_raw["end_date"] = "2024-05-01T00:00:00Z"

    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "engage/properties", json=engage_properties)
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "engage?", engage_response)

    stream = init_stream("engage", config=config_raw)

    stream_state = {"last_seen": "2024-02-11T11:20:47"}
    records = list(read_incremental(stream, stream_state=stream_state, cursor_field=["last_seen"]))

    assert len(records) == 1
    assert stream.get_updated_state(current_stream_state=stream_state, latest_record=records[-1]) == {"last_seen": "2024-03-01T11:20:47"}


@pytest.mark.parametrize(
    "test_name, state, record_count, updated_state",
    (
        (
            "empty_state",
            {},
            2,
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-03-01T11:20:47"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
        ),
        (
            "abnormal_state",
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2030-01-01T00:00:00"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
            0,
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2030-01-01T00:00:00"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
        ),
        (
            "medium_state",
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-03-01T11:20:00"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
            1,
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-03-01T11:20:47"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
        ),
        (
            "early_state",
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-02-01T00:00:00"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
            2,
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-03-01T11:20:47"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    }
                ]
            },
        ),
        (
            "state_for_different_partition",
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-02-01T00:00:00"},
                        "partition": {"id": 2222, "parent_slice": {}},
                    }
                ]
            },
            2,
            {
                "states": [
                    {
                        "cursor": {"last_seen": "2024-02-01T00:00:00"},
                        "partition": {"id": 2222, "parent_slice": {}},
                    },
                    {
                        "cursor": {"last_seen": "2024-03-01T11:20:47"},
                        "partition": {"id": 1111, "parent_slice": {}},
                    },
                ]
            },
        ),
    ),
)
def test_cohort_members_stream_incremental(requests_mock, engage_response, config_raw, test_name, state, record_count, updated_state):
    """Cohort_members stream has legacy state but actually it should always return all records
    because members in cohorts can be updated at any time
    """
    engage_properties = {"results": {"$browser": {"count": 124, "type": "string"}, "$browser_version": {"count": 124, "type": "string"}}}
    config_raw["start_date"] = "2024-02-01T00:00:00Z"
    config_raw["end_date"] = "2024-03-01T00:00:00Z"

    requests_mock.register_uri(
        "GET", MIXPANEL_BASE_URL + "cohorts/list", json=[{"id": 1111, "name": "bla", "created": "2024-02-02T00:00:00Z"}]
    )
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "engage/properties", json=engage_properties)
    requests_mock.register_uri("POST", MIXPANEL_BASE_URL + "engage?", engage_response)

    stream = init_stream("cohort_members", config=config_raw)

    records = list(read_incremental(stream, stream_state=state, cursor_field=["last_seen"]))

    assert len(records) == record_count
    new_updated_state = stream.get_updated_state(current_stream_state=state, latest_record=records[-1] if records else None)
    assert new_updated_state["states"] == updated_state["states"]


def test_cohort_members_stream_pagination(requests_mock, engage_response, config_raw):
    """Cohort_members pagination"""
    engage_properties = {"results": {"$browser": {"count": 124, "type": "string"}, "$browser_version": {"count": 124, "type": "string"}}}
    config_raw["start_date"] = "2024-02-01T00:00:00Z"
    config_raw["end_date"] = "2024-03-01T00:00:00Z"

    requests_mock.register_uri(
        "GET",
        MIXPANEL_BASE_URL + "cohorts/list",
        json=[
            {"id": 71000, "name": "bla", "created": "2024-02-01T00:00:00Z"},
            {"id": 71111, "name": "bla", "created": "2024-02-02T00:00:00Z"},
            {"id": 72222, "name": "bla", "created": "2024-02-01T00:00:00Z"},
            {"id": 73333, "name": "bla", "created": "2024-02-03T00:00:00Z"},
        ],
    )
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "engage/properties", json=engage_properties)
    requests_mock.register_uri(
        "POST",
        MIXPANEL_BASE_URL + "engage",
        [
            {  # initial request for 71000 cohort
                "status_code": 200,
                "json": {"page": 0, "page_size": 1000, "session_id": "1234567890", "status": "ok", "total": 0, "results": []},
            },
            {  # initial request for 71111 cohort and further pagination
                "status_code": 200,
                "json": {
                    "page": 0,
                    "page_size": 1000,
                    "session_id": "1234567890",
                    "status": "ok",
                    "total": 2002,
                    "results": [
                        {
                            "$distinct_id": "71111_1",
                            "$properties": {
                                "$created": "2024-03-01T11:20:47",
                                "$last_seen": "2024-03-01T11:20:47",
                            },
                        },
                        {
                            "$distinct_id": "71111_2",
                            "$properties": {
                                "$created": "2024-02-01T11:20:47",
                                "$last_seen": "2024-02-01T11:20:47",
                            },
                        },
                    ],
                },
            },
            {  # initial request for 72222 cohort without further pagination
                "status_code": 200,
                "json": {
                    "page": 0,
                    "page_size": 1000,
                    "session_id": "1234567890",
                    "status": "ok",
                    "total": 1,
                    "results": [
                        {
                            "$distinct_id": "72222_1",
                            "$properties": {
                                "$created": "2024-02-01T11:20:47",
                                "$last_seen": "2024-02-01T11:20:47",
                            },
                        }
                    ],
                },
            },
            {  # initial request for 73333 cohort
                "status_code": 200,
                "json": {"page": 0, "page_size": 1000, "session_id": "1234567890", "status": "ok", "total": 0, "results": []},
            },
        ],
    )
    # request for 1 page for 71111 cohort
    requests_mock.register_uri(
        "POST",
        MIXPANEL_BASE_URL + "engage?page_size=1000&session_id=1234567890&page=1",
        json={
            "page": 1,
            "session_id": "1234567890",
            "status": "ok",
            "results": [
                {
                    "$distinct_id": "71111_3",
                    "$properties": {
                        "$created": "2024-02-01T11:20:47",
                        "$last_seen": "2024-02-01T11:20:47",
                    },
                }
            ],
        },
    )
    # request for 2 page for 71111 cohort
    requests_mock.register_uri(
        "POST",
        MIXPANEL_BASE_URL + "engage?page_size=1000&session_id=1234567890&page=2",
        json={
            "page": 2,
            "session_id": "1234567890",
            "status": "ok",
            "results": [
                {
                    "$distinct_id": "71111_4",
                    "$properties": {
                        "$created": "2024-02-01T11:20:47",
                        "$last_seen": "2024-02-01T11:20:47",
                    },
                }
            ],
        },
    )

    stream = init_stream("cohort_members", config=config_raw)

    records = list(read_incremental(stream, stream_state={}, cursor_field=["last_seen"]))
    assert len(records) == 5
    new_updated_state = stream.get_updated_state(current_stream_state={}, latest_record=records[-1] if records else None)
    assert new_updated_state["states"] == [
        {"cursor": {"last_seen": "2024-03-01T11:20:47"}, "partition": {"id": 71111, "parent_slice": {}}},
        {"cursor": {"last_seen": "2024-02-01T11:20:47"}, "partition": {"id": 72222, "parent_slice": {}}},
    ]


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


@pytest.fixture
def funnel_ids_response(start_date):
    return setup_response(200, [{"funnel_id": 36152117, "name": "test"}])


def test_funnels_stream(requests_mock, config, funnels_response, funnel_ids_response, config_raw):
    config_raw["start_date"] = "2024-01-01T00:00:00Z"
    config_raw["end_date"] = "2024-04-01T00:00:00Z"
    stream = init_stream("funnels", config=config_raw)
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels/list", funnel_ids_response)
    requests_mock.register_uri("GET", MIXPANEL_BASE_URL + "funnels", funnels_response)

    stream_slices = list(stream.stream_slices(sync_mode=SyncMode.incremental))
    assert len(stream_slices) > 3
    assert {"funnel_id": stream_slices[0]["funnel_id"], "name": stream_slices[0]["funnel_name"]} == {
        "funnel_id": "36152117",
        "name": "test",
    }
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slices[0])
    records = list(records)
    assert len(records) == 2


@pytest.fixture
def engage_schema_response():
    return setup_response(
        200,
        {
            "results": {
                "$created": {"count": 124, "type": "string"},
                "$is_active": {"count": 412, "type": "boolean"},
                "$CreatedDateTimestamp": {"count": 300, "type": "number"},
                "$CreatedDate": {"count": 11, "type": "datetime"},
                "$properties": {"count": 2, "type": "object"},
                "$tags": {"count": 131, "type": "list"},
            }
        },
    )


def _minimize_schema(fill_schema, schema_original):
    keep = ["items", "properties", "type", "$schema", "additionalProperties", "required", "format", "multipleOf"]
    for key, value in schema_original.items():
        if isinstance(value, dict):
            fill_schema[key] = {}
            _minimize_schema(fill_schema[key], value)
        elif key in keep:
            fill_schema[key] = value


def test_engage_schema(requests_mock, engage_schema_response, config_raw):
    stream = init_stream("engage", config=config_raw)
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/properties", engage_schema_response)
    type_schema = {}
    _minimize_schema(type_schema, stream.get_json_schema())

    assert type_schema == {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "properties": {
            "CreatedDate": {"type": ["null", "string"]},
            "CreatedDateTimestamp": {"type": ["null", "number"]},
            "browser": {"type": ["null", "string"]},
            "browser_version": {"type": ["null", "string"]},
            "city": {"type": ["null", "string"]},
            "country_code": {"type": ["null", "string"]},
            "created": {"type": ["null", "string"]},
            "distinct_id": {"type": ["null", "string"]},
            "email": {"type": ["null", "string"]},
            "first_name": {"type": ["null", "string"]},
            "id": {"type": ["null", "string"]},
            "is_active": {"type": ["null", "boolean"]},
            "last_name": {"type": ["null", "string"]},
            "last_seen": {"format": "date-time", "type": ["null", "string"]},
            "name": {"type": ["null", "string"]},
            "properties": {"type": ["null", "object"]},
            "region": {"type": ["null", "string"]},
            "tags": {"type": ["null", "array"]},
            "timezone": {"type": ["null", "string"]},
            "unblocked": {"type": ["null", "string"]},
        },
        "type": "object",
    }


def test_update_engage_schema(requests_mock, config, config_raw):
    requests_mock.register_uri(
        "GET",
        "https://mixpanel.com/api/query/engage/properties",
        setup_response(
            200,
            {
                "results": {
                    "$someNewSchemaField": {"count": 124, "type": "string"},
                }
            },
        ),
    )
    engage_stream = init_stream("engage", config=config_raw)
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


def test_annotations_stream(requests_mock, annotations_response, config_raw):
    stream = init_stream("annotations", config=config_raw)
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/annotations", annotations_response)

    stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2021-01-25", "end_time": "2021-07-25"})
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
    records = list(records)
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


def test_revenue_stream(requests_mock, revenue_response, config_raw):
    stream = init_stream("revenue", config=config_raw)
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/engage/revenue", revenue_response)
    stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2021-01-25", "end_time": "2021-07-25"})
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
    records = list(records)

    assert len(records) == 2


@pytest.fixture
def export_schema_response():
    return setup_response(
        200,
        {
            "$DYNAMIC_FIELD": {"count": 6},
            "$dynamic_field": {"count": 6},
            "$browser_version": {"count": 6},
        },
    )


def test_export_schema(requests_mock, export_schema_response, config_raw):
    stream = init_stream("export", config_raw)
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", export_schema_response)

    schema = stream.get_json_schema()

    assert "DYNAMIC_FIELD" in schema["properties"]
    assert schema["properties"]["DYNAMIC_FIELD"]["type"] == ["null", "string"]
    assert "_dynamic_field" in schema["properties"]
    assert schema["properties"]["_dynamic_field"]["type"] == ["null", "string"]
    assert "browser_version" in schema["properties"]
    assert schema["properties"]["browser_version"]["type"] == ["null", "string"]


def test_export_get_json_schema(requests_mock, export_schema_response, config_raw):
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", export_schema_response)

    stream = init_stream("export", config_raw)
    schema = stream.get_json_schema()

    assert "DYNAMIC_FIELD" in schema["properties"]


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


def test_export_stream(requests_mock, export_response, config_raw):
    stream = init_stream("export", config_raw)

    requests_mock.register_uri("GET", get_url_to_mock(stream), export_response)
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", json={})
    stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2017-01-25T00:00:00Z", "end_time": "2017-02-25T00:00:00Z"})
    # read records for single slice
    records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)

    records_length = sum(1 for _ in records)
    assert records_length == 1


def test_export_stream_fail(requests_mock, export_response, config_raw):
    stream = init_stream("export", config_raw)
    error_message = ""
    requests_mock.register_uri("GET", get_url_to_mock(stream), status_code=400, text="Unable to authenticate request")
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", json={})
    stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2017-01-25T00:00:00Z", "end_time": "2017-01-25T00:00:00Z"})
    try:
        records = stream.read_records(sync_mode=SyncMode.incremental, stream_slice=stream_slice)
        records = list(records)
    except Exception as e:
        error_message = str(e)
    assert "Authentication has failed. Please update your config with valid credentials." in error_message


def test_handle_time_zone_mismatch(requests_mock, export_config, caplog):
    stream = init_stream("export", export_config)
    requests_mock.register_uri("GET", get_url_to_mock(stream), status_code=400, text="to_date cannot be later than today")
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", json={})
    records = []
    try:
        for slice_ in stream.stream_slices(sync_mode=SyncMode.full_refresh):
            records.extend(stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice_))
    except MessageRepresentationAirbyteTracedErrors as airbyte_error:
        assert (
            "Your project timezone must be misconfigured. Please set it to the one defined in your Mixpanel project settings."
        ) in airbyte_error.message


def test_export_terminated_early(requests_mock, export_config):
    stream = init_stream("export", export_config)
    requests_mock.register_uri("GET", get_url_to_mock(stream), text="terminated early\n")
    requests_mock.register_uri("GET", "https://mixpanel.com/api/query/events/properties/top", json={})
    assert list(read_full_refresh(stream)) == []


def test_export_iter_dicts():
    record = {"key1": "value1", "key2": "value2"}
    record_string = json.dumps(record)
    assert list(iter_dicts([record_string, record_string])) == [record, record]
    # combine record from 2 standing nearby parts
    assert list(iter_dicts([record_string, record_string[:2], record_string[2:], record_string])) == [record, record, record]
    # drop record parts because they are not standing nearby
    assert list(iter_dicts([record_string, record_string[:2], record_string, record_string[2:]])) == [record, record]


@responses.activate
def test_export_full_refresh_read(export_config, engage_response):
    config = export_config.copy()
    config["start_date"] = "2022-01-01T00:00:00Z"
    config["end_date"] = "2022-06-01T00:00:00Z"
    config["attribution_window"] = 5
    config["export_lookback_window"] = 60
    config["date_window_size"] = 90
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(name="export", json_schema={}, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]),
            )
        ]
    )

    responses.add(
        responses.GET,
        url="https://mixpanel.com/api/query/engage/properties",
        json={
            "computed_at": "time",
            "results": {
                "$email": {"count": 2, "type": "string"},
                "$last_seen": {"count": 3, "type": "datetime"},
                "$name": {"count": 3, "type": "string"},
            },
            "session_id": "session",
            "status": "ok",
        },
        status=200,
    )
    responses.add(responses.GET, url="https://mixpanel.com/api/query/events/properties/top", json={}, status=200)

    request_params = [
        ({"from_date": "2022-01-01T00:00:00Z", "to_date": "2022-03-31T00:00:00Z"}, {"properties": {"time": "2022-03-18T21:59:59Z"}}),
        ({"from_date": "2022-04-01T00:00:00Z", "to_date": "2022-06-01T00:00:00Z"}, {"properties": {"time": "2022-05-18T21:59:59Z"}}),
    ]

    for params, json_data in request_params:
        responses.add(
            responses.GET, url="https://data.mixpanel.com/api/2.0/export?" + urllib.parse.urlencode(params), json=json_data, status=200
        )

    output = read(SourceMixpanel(config=config, catalog=catalog, state={}), config, catalog, {})
    assert len(output.records) == 2
    assert output.state_messages[-1].state.stream.stream_state.time == "2022-05-18T21:59:59Z"


@responses.activate
def test_export_incremental_read(export_config, engage_response):
    config = export_config.copy()
    config["start_date"] = "2022-01-01T00:00:00Z"
    config["end_date"] = "2022-06-01T00:00:00Z"
    config["attribution_window"] = 5
    config["export_lookback_window"] = 60
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(name="export", json_schema={}, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]),
            )
        ]
    )
    state_value = "2022-03-25T00:00:00Z"
    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="export"), stream_state=AirbyteStateBlob(**{"time": state_value})
            ),
        )
    ]

    responses.add(
        responses.GET,
        url="https://mixpanel.com/api/query/engage/properties",
        json={
            "computed_at": "time",
            "results": {
                "$email": {"count": 2, "type": "string"},
                "$last_seen": {"count": 3, "type": "datetime"},
                "$name": {"count": 3, "type": "string"},
            },
            "session_id": "session",
            "status": "ok",
        },
        status=200,
    )
    responses.add(responses.GET, url="https://mixpanel.com/api/query/events/properties/top", json={}, status=200)

    start_from_date = (pendulum.parse(state_value) - timedelta(days=config["attribution_window"])).format("YYYY-MM-DD")
    request_params = [
        ({"from_date": start_from_date, "to_date": "2022-06-01"}, {"properties": {"time": "2022-04-18T21:59:59Z"}}),
    ]

    time_ts = (pendulum.parse(state_value) - timedelta(seconds=config["export_lookback_window"])).timestamp()

    for params, json_data in request_params:
        params.update({"where": f'properties["$time"]>=datetime({int(time_ts)})'})
        responses.add(
            responses.GET, url="https://data.mixpanel.com/api/2.0/export?" + urllib.parse.urlencode(params), json=json_data, status=200
        )

    output = read(SourceMixpanel(config=config, catalog=catalog, state=state), config, catalog, state)
    assert len(output.records) == 1
    assert output.state_messages[-1].state.stream.stream_state.time == "2022-04-18T21:59:59Z"


@responses.activate
def test_export_lookback_window(export_config):
    """Test that export_lookback_window correctly adjusts the start date during incremental sync and verifies slice parameters"""
    config = export_config.copy()
    config["export_lookback_window"] = 7200  # 1 hour lookback
    config["start_date"] = "2021-06-01T00:00:00Z"
    config["end_date"] = "2021-07-10T00:00:00Z"

    responses.add(
        responses.GET,
        url="https://mixpanel.com/api/query/engage/properties",
        json={
            "computed_at": "time",
            "results": {
                "$email": {"count": 2, "type": "string"},
                "$last_seen": {"count": 3, "type": "datetime"},
                "$name": {"count": 3, "type": "string"},
            },
            "session_id": "session",
            "status": "ok",
        },
        status=200,
    )
    responses.add(responses.GET, url="https://mixpanel.com/api/query/events/properties/top", json={}, status=200)

    state_value = "2021-06-16T16:28:00Z"

    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append_dedup,
                stream=AirbyteStream(name="export", json_schema={}, supported_sync_modes=[SyncMode.incremental, SyncMode.full_refresh]),
            )
        ]
    )

    state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="export"), stream_state=AirbyteStateBlob(**{"time": state_value})
            ),
        )
    ]

    # Verify slice parameters
    expected_end = pendulum.parse("2021-07-10T00:00:00Z").format("YYYY-MM-DD")  # From config end_date
    expected_start = (pendulum.parse(state_value) - timedelta(days=config["attribution_window"])).format(
        "YYYY-MM-DD"
    )  # 16:28:00 - 2 hours due to lookback

    # Mock response with two records at different times in JSONL format
    export_response_multiple = (
        b'{"event": "Viewed Page", "properties": {"time": 1623860880, "distinct_id": "user1", "$insert_id": "insert1"}}\n'
        b'{"event": "Clicked Button", "properties": {"time": 1623864480, "distinct_id": "user2", "$insert_id": "insert2"}}'
    )

    request_params = [
        ({"from_date": expected_start, "to_date": expected_end}, export_response_multiple),
    ]

    time_ts = (pendulum.parse(state_value) - timedelta(seconds=config["export_lookback_window"])).timestamp()

    for params, body_data in request_params:
        params.update({"where": f'properties["$time"]>=datetime({int(time_ts)})'})
        responses.add(
            responses.GET, url="https://data.mixpanel.com/api/2.0/export?" + urllib.parse.urlencode(params), body=body_data, status=200
        )

    output = read(SourceMixpanel(config=config, catalog=catalog, state=state), config, catalog, state)
    # Verify updated state is set to the latest record time
    assert output.state_messages[-1].state.stream.stream_state.time == "2021-06-16T17:28:00Z"
