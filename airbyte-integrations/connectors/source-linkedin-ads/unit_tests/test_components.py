#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import pytest
from source_linkedin_ads.components import *

state_test_records = [
    {"id": "1", "lastModified": "2022-01-02T00:00:00.000Z"},
    {"id": "2", "lastModified": "2022-01-03T00:00:00.000Z"},
    {"id": "3", "lastModified": "2022-01-04T00:00:00.000Z"},
]

@pytest.fixture
def semi_incremental_config_start_date():
    return LinkedInSemiIncrementalFilter(parameters={}, config={"start_date": "2021-01-01T00:00:00.000Z"})


@pytest.mark.parametrize(
    "state_value, expected_return",
    [
        (
                [{"cursor": {"lastModified": "2021-02-01T00:00:00.000Z"}}], "2021-02-01T00:00:00.000Z"
        ),
        (
                [{"cursor": {"lastModified": "2020-01-01T00:00:00.000Z"}}], "2021-01-01T00:00:00.000Z"
        ),
        (
                [], "2021-01-01T00:00:00.000Z"
        )
    ],
    ids=["State value is greater than start_date", "State value is less than start_date", "Empty state, default to start_date"]
)
def test_semi_incremental_get_filter_date(semi_incremental_config_start_date, state_value, expected_return):
    start_date = semi_incremental_config_start_date.config["start_date"]

    result = semi_incremental_config_start_date._get_filter_date(start_date, state_value)
    assert result == expected_return, f"Expected {expected_return}, but got {result}."

    semi_incremental_config_start_date.filter_records


@pytest.mark.parametrize("stream_state,stream_slice,expected_records", [
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"lastModified": "2022-01-01T00:00:00.000Z"}}]},
        {"id": "some_id"},
        state_test_records
    ),
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"lastModified": "2022-01-03T00:00:00.000Z"}}]},
        {"id": "some_id"},
        [state_test_records[-2], state_test_records[-1]]
    ),
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"lastModified": "2022-01-05T00:00:00.000Z"}}]},
        {"id": "some_id"},
        []
    ),
    (
        {"states": []},
        {"id": "some_id"},
        state_test_records
    )
],
ids=["No records filtered", "Some records filtered", "All records filtered", "Empty state: no records filtered"])
def test_semi_incremental_filter_records(semi_incremental_config_start_date, stream_state, stream_slice, expected_records):
    filtered_records = semi_incremental_config_start_date.filter_records(state_test_records, stream_state, stream_slice)
    assert filtered_records == expected_records, "Filtered records do not match the expected records."
