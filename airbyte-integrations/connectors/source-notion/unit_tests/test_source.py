#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_notion.source import SourceNotion
from source_notion.components import *
import pytest

def test_streams():
    source = SourceNotion()
    config_mock = {"start_date": "2020-01-01T00:00:00.000Z",
                   "credentials": {"auth_type": "token", "token": "abcd"}}
    streams = source.streams(config_mock)
    expected_streams_number = 5
    assert len(streams) == expected_streams_number


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
        "id": "123",
        "properties": {
            "Due date": {
                "id": "M%3BBw",
                "type": "date",
                "date": {
                    "start": "2023-02-23",
                    "end": None,
                    "time_zone": None
                }
            },
            "Status": {
                "id": "Z%3ClH",
                "type": "status",
                "status": {
                    "id": "86ddb6ec-0627-47f8-800d-b65afd28be13",
                    "name": "Not started",
                    "color": "default"
                }
            }
        }
    }

    output_record = {
        "id": "123",
        "properties": [
            {
                "name": "Due date",
                "value": {
                    "id": "M%3BBw",
                    "type": "date",
                    "date": {
                        "start": "2023-02-23",
                        "end": None,
                        "time_zone": None
                    }
                }
            },
            {
                "name": "Status",
                "value": {
                    "id": "Z%3ClH",
                    "type": "status",
                    "status": {
                        "id": "86ddb6ec-0627-47f8-800d-b65afd28be13",
                        "name": "Not started",
                        "color": "default"
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
    ]
)
def test_get_filter_date_with_later_state_date(config_start_date, state_value, expected_return):
    start_date = config_start_date.config["start_date"]
    
    result = config_start_date.get_filter_date(start_date, state_value)
    assert result == expected_return, f"Expected {expected_return}, but got {result}."
