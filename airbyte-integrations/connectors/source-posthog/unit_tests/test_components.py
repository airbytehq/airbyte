#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from source_posthog.components import EventsCartesianProductStreamSlicer, EventsV2CartesianProductStreamSlicer, EventsV2Retriever

from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.partition_routers.list_partition_router import ListPartitionRouter
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption


stream_slicers = [
    ListPartitionRouter(values=[2331], cursor_field="project_id", config={}, parameters={}),
    DatetimeBasedCursor(
        start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
        end_datetime=MinMaxDatetime(datetime="2021-02-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
        step="P10D",
        cursor_field="timestamp",
        datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
        cursor_granularity="PT0.000001S",
        start_time_option=RequestOption(inject_into="request_parameter", field_name="after", parameters={}),
        end_time_option=RequestOption(inject_into="request_parameter", field_name="before", parameters={}),
        config={},
        parameters={},
    ),
]


@pytest.mark.parametrize(
    "test_name, initial_state, stream_slice, last_record, expected_state",
    [
        ("test_empty", {}, {}, {}, {}),
        (
            "test_set_initial_state",
            {"2331": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
            {},
            {},
            {"2331": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
        ),
        (
            "test_update_empty_state",
            {},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state",
            {"2331": {"timestamp": "2021-01-01T10:00:00.00+0000"}},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state_newly",
            {"2331": {"timestamp": "2021-01-01T22:00:00.00+0000"}},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T22:00:00.00+0000"}},
        ),
        (
            "test_update_of_initial_state_old_style",
            {"timestamp": "2021-01-01T10:00:00.00+0000"},
            {"project_id": "2331", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"2331": {"timestamp": "2021-01-01T11:00:00.00+0000"}, "timestamp": "2021-01-01T10:00:00.00+0000"},
        ),
    ],
)
def test_update_cursor(test_name, initial_state, stream_slice, last_record, expected_state):
    slicer = EventsCartesianProductStreamSlicer(stream_slicers=stream_slicers, parameters={})
    # set initial state
    slicer.set_initial_state(initial_state)

    if last_record:
        slicer.close_slice(stream_slice, last_record)

    updated_state = slicer.get_stream_state()
    assert updated_state == expected_state


@pytest.mark.parametrize(
    "test_name, stream_state, expected_stream_slices",
    [
        (
            "test_empty_state",
            {},
            [
                {"end_time": "2021-01-10T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T00:00:00.000000+0000"},
                {"end_time": "2021-01-20T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-10T23:59:59.999999+0000"},
                {"end_time": "2021-01-30T23:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-20T23:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-30T23:59:59.999999+0000"},
            ],
        ),
        (
            "test_state",
            {"2331": {"timestamp": "2021-01-01T17:00:00.000000+0000"}},
            [
                {"end_time": "2021-01-11T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T17:00:00.000000+0000"},
                {"end_time": "2021-01-21T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-11T16:59:59.999999+0000"},
                {"end_time": "2021-01-31T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-21T16:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-31T16:59:59.999999+0000"},
            ],
        ),
        (
            "test_old_stype_state",
            {"timestamp": "2021-01-01T17:00:00.000000+0000"},
            [
                {"end_time": "2021-01-11T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-01T17:00:00.000000+0000"},
                {"end_time": "2021-01-21T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-11T16:59:59.999999+0000"},
                {"end_time": "2021-01-31T16:59:59.999999+0000", "project_id": "2331", "start_time": "2021-01-21T16:59:59.999999+0000"},
                {"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-31T16:59:59.999999+0000"},
            ],
        ),
        (
            "test_state_for_one_slice",
            {"2331": {"timestamp": "2021-01-27T17:00:00.000000+0000"}},
            [{"end_time": "2021-02-01T00:00:00.000000+0000", "project_id": "2331", "start_time": "2021-01-27T17:00:00.000000+0000"}],
        ),
    ],
)
def test_stream_slices(test_name, stream_state, expected_stream_slices):
    slicer = EventsCartesianProductStreamSlicer(stream_slicers=stream_slicers, parameters={})
    slicer.set_initial_state(stream_state)
    stream_slices = slicer.stream_slices()
    assert list(stream_slices) == expected_stream_slices


# =============================================================================
# EventsV2CartesianProductStreamSlicer Tests
# =============================================================================

@pytest.mark.parametrize(
    "test_name, initial_state, stream_slice, last_record, expected_state",
    [
        ("test_v2_empty", {}, {}, {}, {}),
        (
            "test_v2_set_initial_state",
            {"116435": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
            {},
            {},
            {"116435": {"timestamp": "2021-01-01T00:00:00.00+0000"}},
        ),
        (
            "test_v2_update_empty_state",
            {},
            {"project_id": "116435", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"116435": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
        (
            "test_v2_update_of_initial_state",
            {"116435": {"timestamp": "2021-01-01T10:00:00.00+0000"}},
            {"project_id": "116435", "start_time": "2021-01-01T00:00:00.00+0000", "end_time": "2021-01-03T00:00:00.00+0000"},
            {"timestamp": "2021-01-01T11:00:00.00+0000"},
            {"116435": {"timestamp": "2021-01-01T11:00:00.00+0000"}},
        ),
    ],
)
def test_v2_update_cursor(test_name, initial_state, stream_slice, last_record, expected_state):
    v2_stream_slicers = [
        ListPartitionRouter(values=[116435], cursor_field="project_id", config={}, parameters={}),
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
            end_datetime=MinMaxDatetime(datetime="2021-02-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
            step="P10D",
            cursor_field="timestamp",
            datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
            cursor_granularity="PT0.000001S",
            start_time_option=RequestOption(inject_into="request_parameter", field_name="after", parameters={}),
            end_time_option=RequestOption(inject_into="request_parameter", field_name="before", parameters={}),
            config={},
            parameters={},
        ),
    ]
    slicer = EventsV2CartesianProductStreamSlicer(stream_slicers=v2_stream_slicers, config={}, parameters={})
    slicer.set_initial_state(initial_state)

    if last_record:
        slicer.close_slice(stream_slice, last_record)

    updated_state = slicer.get_stream_state()
    assert updated_state == expected_state


def test_v2_stream_slices_with_config_project_id():
    """Test that project_id from config is used instead of fetching from API."""
    v2_stream_slicers = [
        ListPartitionRouter(values=[9999], cursor_field="project_id", config={}, parameters={}),
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
            end_datetime=MinMaxDatetime(datetime="2021-01-11T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
            step="P10D",
            cursor_field="timestamp",
            datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
            cursor_granularity="PT0.000001S",
            start_time_option=RequestOption(inject_into="request_parameter", field_name="after", parameters={}),
            end_time_option=RequestOption(inject_into="request_parameter", field_name="before", parameters={}),
            config={},
            parameters={},
        ),
    ]

    config = {"project_id": "116435"}
    slicer = EventsV2CartesianProductStreamSlicer(stream_slicers=v2_stream_slicers, config=config, parameters={})

    slices = list(slicer.stream_slices())

    # All slices should use the config project_id (116435), not the router value (9999)
    assert len(slices) > 0
    for s in slices:
        assert s["project_id"] == "116435"


def test_v2_stream_slices_without_config_project_id():
    """Test that project_id from router is used when config.project_id is not set."""
    v2_stream_slicers = [
        ListPartitionRouter(values=[9999], cursor_field="project_id", config={}, parameters={}),
        DatetimeBasedCursor(
            start_datetime=MinMaxDatetime(datetime="2021-01-01T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
            end_datetime=MinMaxDatetime(datetime="2021-01-11T00:00:00.00+0000", datetime_format="%Y-%m-%dT%H:%M:%S.%f%z", parameters={}),
            step="P10D",
            cursor_field="timestamp",
            datetime_format="%Y-%m-%dT%H:%M:%S.%f%z",
            cursor_granularity="PT0.000001S",
            start_time_option=RequestOption(inject_into="request_parameter", field_name="after", parameters={}),
            end_time_option=RequestOption(inject_into="request_parameter", field_name="before", parameters={}),
            config={},
            parameters={},
        ),
    ]

    config = {}
    slicer = EventsV2CartesianProductStreamSlicer(stream_slicers=v2_stream_slicers, config=config, parameters={})

    slices = list(slicer.stream_slices())

    # All slices should use the router project_id (9999) when config doesn't have one
    assert len(slices) > 0
    for s in slices:
        assert s["project_id"] == "9999"


# =============================================================================
# EventsV2Retriever Tests
# =============================================================================

class TestEventsV2Retriever:
    def test_validate_datetime_valid_formats(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        assert retriever._validate_datetime("2021-01-01T00:00:00.000000+0000") == "2021-01-01T00:00:00.000000+0000"
        assert retriever._validate_datetime("2021-01-01T00:00:00Z") == "2021-01-01T00:00:00Z"
        assert retriever._validate_datetime("2021-01-01T00:00:00+00:00") == "2021-01-01T00:00:00+00:00"
        assert retriever._validate_datetime("2021-01-01T00:00:00-05:00") == "2021-01-01T00:00:00-05:00"

    def test_validate_datetime_invalid_formats(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        with pytest.raises(ValueError, match="Empty datetime string"):
            retriever._validate_datetime("")

        with pytest.raises(ValueError, match="Invalid datetime format"):
            retriever._validate_datetime("invalid-date")

        with pytest.raises(ValueError, match="Invalid datetime format"):
            retriever._validate_datetime("2021-01-01")

    def test_build_hogql_query(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        stream_slice = {
            "start_time": "2021-01-01T00:00:00.000000+0000",
            "end_time": "2021-01-10T23:59:59.999999+0000",
            "project_id": "116435"
        }

        query = retriever._build_hogql_query(stream_slice, offset=0)

        assert "FROM events e" in query
        assert "LEFT JOIN persons p ON p.id = e.person.id" in query
        assert "e.timestamp >= toDateTime('2021-01-01T00:00:00.000000+0000')" in query
        assert "e.timestamp < toDateTime('2021-01-10T23:59:59.999999+0000')" in query
        assert "LIMIT 10000" in query
        assert "OFFSET 0" in query

    def test_build_hogql_query_with_offset(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        stream_slice = {
            "start_time": "2021-01-01T00:00:00Z",
            "end_time": "2021-01-10T23:59:59Z",
            "project_id": "116435"
        }

        query = retriever._build_hogql_query(stream_slice, offset=10000)

        assert "OFFSET 10000" in query

    def test_extract_records_from_response(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        response_body = {
            "columns": [
                "uuid", "event", "properties", "timestamp", "distinct_id",
                "elements_chain", "created_at", "person_id", "person_properties", "person_is_identified"
            ],
            "results": [
                [
                    "abc-123", "$pageview", {"$current_url": "http://example.com"}, "2021-01-01T10:00:00Z",
                    "user-123", None, "2021-01-01T10:00:00Z", "person-456", {"email": "test@example.com"}, True
                ]
            ]
        }

        records = retriever._extract_records_from_response(response_body)

        assert len(records) == 1
        record = records[0]
        assert record["id"] == "abc-123"
        assert record["event"] == "$pageview"
        assert record["properties"]["$current_url"] == "http://example.com"
        assert record["timestamp"] == "2021-01-01T10:00:00Z"
        assert record["distinct_id"] == "user-123"
        assert record["person"]["id"] == "person-456"
        assert record["person"]["properties"]["email"] == "test@example.com"
        assert record["person"]["is_identified"] is True
        assert record["person"]["distinct_ids"] == ["user-123"]

    def test_extract_records_from_response_empty(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        response_body = {"columns": [], "results": []}
        records = retriever._extract_records_from_response(response_body)
        assert records == []

    def test_extract_records_handles_null_person_data(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        response_body = {
            "columns": [
                "uuid", "event", "properties", "timestamp", "distinct_id",
                "elements_chain", "created_at", "person_id", "person_properties", "person_is_identified"
            ],
            "results": [
                [
                    "abc-123", "$pageview", {}, "2021-01-01T10:00:00Z",
                    "user-123", None, None, None, None, None
                ]
            ]
        }

        records = retriever._extract_records_from_response(response_body)

        assert len(records) == 1
        record = records[0]
        assert record["person"]["id"] is None
        assert record["person"]["properties"] == {}
        assert record["person"]["is_identified"] is False

    def test_get_base_url_default(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        assert retriever._get_base_url() == "https://app.posthog.com"

    def test_get_base_url_custom(self):
        config = {"api_key": "test", "start_date": "2021-01-01T00:00:00Z", "base_url": "https://us.posthog.com"}
        retriever = EventsV2Retriever(config=config, stream_slicer=None, parameters={})

        assert retriever._get_base_url() == "https://us.posthog.com"
