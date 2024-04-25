#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_notion.components import *


def test_users_stream_transformation():
    input_record = {
        "object": "user", "id": "123", "name": "Airbyte", "avatar_url": "some url", "type": "bot",
        "bot": {"owner": {"type": "user", "user": {"object": "user", "id": "id", "name": "Test User", "avatar_url": None, "type": "person",
                                                   "person": {"email": "email"}}}, "workspace_name": "test"}
    }
    output_record = {
        "object": "user", "id": "123", "name": "Airbyte", "avatar_url": "some url", "type": "bot",
        "bot": {"owner": {"type": "user", "info": {"object": "user", "id": "id", "name": "Test User", "avatar_url": None, "type": "person",
                                                   "person": {"email": "email"}}}, "workspace_name": "test"}
    }
    assert NotionUserTransformation().transform(input_record) == output_record


def test_notion_properties_transformation():
    input_record = {
        "id": "123", "properties": {
            "Due date": {
                "id": "M%3BBw", "type": "date", "date": {
                    "start": "2023-02-23", "end": None, "time_zone": None
                }
            },
            "Status": {
                "id": "Z%3ClH", "type": "status", "status": {
                    "id": "86ddb6ec-0627-47f8-800d-b65afd28be13", "name": "Not started", "color": "default"
                }
            }
        }
    }

    output_record = {
        "id": "123", "properties": [
            {
                "name": "Due date", "value": {
                    "id": "M%3BBw", "type": "date", "date": {
                        "start": "2023-02-23", "end": None, "time_zone": None
                    }
                }
            },
            {
                "name": "Status",
                "value": {
                    "id": "Z%3ClH", "type": "status", "status": {
                        "id": "86ddb6ec-0627-47f8-800d-b65afd28be13", "name": "Not started", "color": "default"
                    }
                }
            }
        ]
    }
    assert NotionPropertiesTransformation().transform(input_record) == output_record


state_test_records = [
    {"id": "1", "last_edited_time": "2022-01-02T00:00:00.000Z"},
    {"id": "2", "last_edited_time": "2022-01-03T00:00:00.000Z"},
    {"id": "3", "last_edited_time": "2022-01-04T00:00:00.000Z"},
]

@pytest.fixture
def data_feed_config():
    return NotionDataFeedFilter(parameters={}, config={"start_date": "2021-01-01T00:00:00.000Z"})

@pytest.mark.parametrize(
    "state_value, expected_return",
    [
        (
            "2021-02-01T00:00:00.000Z", "2021-02-01T00:00:00.000Z"
        ),
        (
            "2020-01-01T00:00:00.000Z", "2021-01-01T00:00:00.000Z"
        ),
        (
            {}, "2021-01-01T00:00:00.000Z"
        )       
    ],
    ids=["State value is greater than start_date", "State value is less than start_date", "Empty state, default to start_date"]
)
def test_data_feed_get_filter_date(data_feed_config, state_value, expected_return):
    start_date = data_feed_config.config["start_date"]
    
    result = data_feed_config._get_filter_date(start_date, state_value)
    assert result == expected_return, f"Expected {expected_return}, but got {result}."


@pytest.mark.parametrize("stream_state,stream_slice,expected_records", [
    (
        {"last_edited_time": "2022-01-01T00:00:00.000Z"},
        {"id": "some_id"},
        state_test_records
    ),
    (
        {"last_edited_time": "2022-01-03T00:00:00.000Z"},
        {"id": "some_id"},
        [state_test_records[-2], state_test_records[-1]]
    ),
    (
        {"last_edited_time": "2022-01-05T00:00:00.000Z"},
        {"id": "some_id"},
        []
    ),
    (
        {},
        {"id": "some_id"},
        state_test_records
    )
],
ids=["No records filtered", "Some records filtered", "All records filtered", "Empty state: no records filtered"])
def test_data_feed_filter_records(data_feed_config, stream_state, stream_slice, expected_records):
    filtered_records = data_feed_config.filter_records(state_test_records, stream_state, stream_slice)
    assert filtered_records == expected_records, "Filtered records do not match the expected records."


@pytest.fixture
def semi_incremental_config_start_date():
    return NotionSemiIncrementalFilter(parameters={}, config={"start_date": "2021-01-01T00:00:00.000Z"})

@pytest.mark.parametrize(
    "state_value, expected_return",
    [
        (
            [{"cursor": {"last_edited_time": "2021-02-01T00:00:00.000Z"}}], "2021-02-01T00:00:00.000Z"
        ),
        (
            [{"cursor": {"last_edited_time": "2020-01-01T00:00:00.000Z"}}], "2021-01-01T00:00:00.000Z"
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


@pytest.mark.parametrize("stream_state,stream_slice,expected_records", [
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"last_edited_time": "2022-01-01T00:00:00.000Z"}}]},
        {"id": "some_id"},
        state_test_records
    ),
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"last_edited_time": "2022-01-03T00:00:00.000Z"}}]},
        {"id": "some_id"},
        [state_test_records[-2], state_test_records[-1]]
    ),
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"last_edited_time": "2022-01-05T00:00:00.000Z"}}]},
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
