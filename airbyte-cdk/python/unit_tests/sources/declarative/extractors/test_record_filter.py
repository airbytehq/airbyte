#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import List, Mapping, Optional

import pytest
from airbyte_cdk.sources.declarative.extractors.record_filter import ClientSideIncrementalRecordFilterDecorator, RecordFilter
from sources.declarative.datetime import MinMaxDatetime
from sources.declarative.incremental import DatetimeBasedCursor
from sources.declarative.interpolation import InterpolatedString


@pytest.mark.parametrize(
    "filter_template, records, expected_records",
    [
        (
                "{{ record['created_at'] > stream_state['created_at'] }}",
                [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
                [{"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
        ),
        (
                "{{ record['last_seen'] >= stream_slice['last_seen'] }}",
                [{"id": 1, "last_seen": "06-06-21"}, {"id": 2, "last_seen": "06-07-21"}, {"id": 3, "last_seen": "06-10-21"}],
                [{"id": 3, "last_seen": "06-10-21"}],
        ),
        (
                "{{ record['id'] >= next_page_token['last_seen_id'] }}",
                [{"id": 11}, {"id": 12}, {"id": 13}, {"id": 14}, {"id": 15}],
                [{"id": 14}, {"id": 15}],
        ),
        (
                "{{ record['id'] >= next_page_token['path_to_nowhere'] }}",
                [{"id": 11}, {"id": 12}, {"id": 13}, {"id": 14}, {"id": 15}],
                [],
        ),
        (
                "{{ record['created_at'] > parameters['created_at'] }}",
                [{"id": 1, "created_at": "06-06-21"}, {"id": 2, "created_at": "06-07-21"}, {"id": 3, "created_at": "06-08-21"}],
                [{"id": 3, "created_at": "06-08-21"}],
        ),
    ],
    ids=["test_using_state_filter", "test_with_slice_filter", "test_with_next_page_token_filter",
         "test_missing_filter_fields_return_no_results", "test_using_parameters_filter", ]
)
def test_record_filter(filter_template: str, records: List[Mapping], expected_records: List[Mapping]):
    config = {"response_override": "stop_if_you_see_me"}
    parameters = {"created_at": "06-07-21"}
    stream_state = {"created_at": "06-06-21"}
    stream_slice = {"last_seen": "06-10-21"}
    next_page_token = {"last_seen_id": 14}
    record_filter = RecordFilter(config=config, condition=filter_template, parameters=parameters)

    actual_records = list(record_filter.filter_records(
        records, stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token
    ))
    assert actual_records == expected_records


@pytest.mark.parametrize(
    "stream_state, count_expected_records",
    [
        ({}, 2),
        ({"created_at": "2021-01-03"}, 1),
    ],
    ids=["no_stream_state", "with_stream_state"]
)
def test_client_side_record_filter_decorator_no_record_filter_no_parent_stream(stream_state: Optional[Mapping], count_expected_records: int):
    records_to_filter = [
        {"id": 1, "created_at": "2020-01-03"},
        {"id": 2, "created_at": "2021-01-03"},
        {"id": 3, "created_at": "2021-01-04"},
        {"id": 4, "created_at": "2021-02-01"},
    ]
    date_time_based_cursor = DatetimeBasedCursor(
                        start_datetime=MinMaxDatetime(datetime="2021-01-01", datetime_format="%Y-%m-%d", parameters={}),
                        end_datetime=MinMaxDatetime(datetime="2021-01-05", datetime_format="%Y-%m-%d", parameters={}),
                        step="P10Y",
                        cursor_field=InterpolatedString.create("created_at", parameters={}),
                        datetime_format="%Y-%m-%d",
                        cursor_granularity="P1D",
                        config={},
                        parameters={},
                    )
    record_filter = ClientSideIncrementalRecordFilterDecorator(
        date_time_based_cursor=date_time_based_cursor,
        record_filter=None,
        per_partition_cursor=None
    )

    filtered_records = list(
        record_filter.filter_records(records=records_to_filter, stream_state=stream_state, stream_slice={}, next_page_token=None)
    )

    assert len(filtered_records) == count_expected_records

