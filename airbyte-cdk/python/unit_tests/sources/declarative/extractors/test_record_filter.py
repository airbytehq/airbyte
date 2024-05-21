#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Mapping, List

import pytest
from airbyte_cdk.sources.declarative.extractors.record_filter import RecordFilter


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
