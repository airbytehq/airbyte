#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_notion.components import *
from source_notion.source import SourceNotion


def test_streams():
    source = SourceNotion()
    config_mock = {"start_date": "2020-01-01T00:00:00.000Z",
                   "credentials": {"auth_type": "token", "token": "abcd"}}
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


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


@pytest.fixture
def config_start_date():
    return NotionSemiIncrementalFilter(parameters={}, config={"start_date": "2021-01-01T00:00:00.000Z"})

@pytest.mark.parametrize(
    "state_value, expected_return",
    [
        (
            [{"cursor": {"last_edited_time": "2021-02-01T00:00:00Z"}}], "2021-02-01T00:00:00Z"
        ),
        (
            [{"cursor": {"last_edited_time": "2020-01-01T00:00:00Z"}}], "2021-01-01T00:00:00Z"
        ),
        (
            [], "2021-01-01T00:00:00Z"
        )       
    ],
    ids=["State value is greater than start_date", "State value is less than start_date", "Empty state, default to start_date"]
)
def test_semi_incremental_get_filter_date(config_start_date, state_value, expected_return):
    start_date = config_start_date.config["start_date"]
    
    result = config_start_date.get_filter_date(start_date, state_value)
    assert result == expected_return, f"Expected {expected_return}, but got {result}."


semi_incremental_records = [
    {"id": "1", "last_edited_time": "2022-01-02T00:00:00Z"},
    {"id": "2", "last_edited_time": "2022-01-03T00:00:00Z"},
    {"id": "3", "last_edited_time": "2022-01-04T00:00:00Z"},
]

@pytest.mark.parametrize("stream_state,stream_slice,expected_records", [
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"last_edited_time": "2022-01-01T00:00:00Z"}}]},
        {"id": "some_id"},
        semi_incremental_records
    ),
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"last_edited_time": "2022-01-03T00:00:00Z"}}]},
        {"id": "some_id"},
        [semi_incremental_records[-1]]
    ),
    (
        {"states": [{"partition": {"id": "some_id"}, "cursor": {"last_edited_time": "2022-01-04T00:00:00Z"}}]},
        {"id": "some_id"},
        []
    ),
    (
        {"states": []},
        {"id": "some_id"},
        semi_incremental_records
    )
],
ids=["No records filtered", "Some records filtered", "All records filtered", "Empty state: no records filtered"])
def test_filter_records(config_start_date, stream_state, stream_slice, expected_records):
    filtered_records = config_start_date.filter_records(semi_incremental_records, stream_state, stream_slice)
    assert filtered_records == expected_records, "Filtered records do not match the expected records."
