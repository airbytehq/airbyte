#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_notion.source import SourceNotion
from source_notion.components import *


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


def test_block_record_transformer():
    response_record = {
        "object": "block", "id": "id", "parent": {"type": "page_id", "page_id": "id"}, "created_time": "2021-10-19T13:33:00.000Z", "last_edited_time": "2021-10-19T13:33:00.000Z",
        "created_by": {"object": "user", "id": "id"}, "last_edited_by": {"object": "user", "id": "id"}, "has_children": False, "archived": False, "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "test", "link": None}, "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"}, "plain_text": "test", "href": None},
                                    {"type": "text", "text": {"content": "@", "link": None}, "annotations": {"bold": False, "italic": False,
                                                                                                             "strikethrough": False, "underline": False, "code": True, "color": "default"}, "plain_text": "@", "href": None},
                                    {"type": "text", "text": {"content": "test", "link": None}, "annotations": {"bold": False, "italic": False,
                                                                                                                "strikethrough": False, "underline": False, "code": False, "color": "default"}, "plain_text": "test", "href": None},
                                    {"type": "mention", "mention": {"type": "page", "page": {"id": "id"}}, "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"},
                                     "plain_text": "test", "href": "https://www.notion.so/id"}], "color": "default"}
    }
    expected_record = {
        "object": "block", "id": "id", "parent": {"type": "page_id", "page_id": "id"}, "created_time": "2021-10-19T13:33:00.000Z", "last_edited_time": "2021-10-19T13:33:00.000Z",
        "created_by": {"object": "user", "id": "id"}, "last_edited_by": {"object": "user", "id": "id"}, "has_children": False, "archived": False, "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "test", "link": None}, "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"}, "plain_text": "test", "href": None},
                                    {"type": "text", "text": {"content": "@", "link": None}, "annotations": {"bold": False, "italic": False,
                                                                                                             "strikethrough": False, "underline": False, "code": True, "color": "default"}, "plain_text": "@", "href": None},
                                    {"type": "text", "text": {"content": "test", "link": None}, "annotations": {"bold": False, "italic": False,
                                                                                                                "strikethrough": False, "underline": False, "code": False, "color": "default"}, "plain_text": "test", "href": None},
                                    {"type": "mention", "mention": {"type": "page", "info": {"id": "id"}}, "annotations": {"bold": False, "italic": False, "strikethrough": False, "underline": False, "code": False, "color": "default"}, "plain_text": "test", "href": "https://www.notion.so/id"}],
                      "color": "default"}
    }
    assert NotionBlocksTransformation().transform(
        response_record) == expected_record

# TODO: Add tests for CustomRecordFilter and CustomRetriever
