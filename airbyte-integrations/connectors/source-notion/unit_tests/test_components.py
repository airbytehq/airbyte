#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.models import ConfiguredAirbyteCatalogSerializer
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.state_builder import StateBuilder
from unit_tests.conftest import get_source


def test_users_stream_transformation(components_module):
    input_record = {
        "object": "user",
        "id": "123",
        "name": "Airbyte",
        "avatar_url": "some url",
        "type": "bot",
        "bot": {
            "owner": {
                "type": "user",
                "user": {
                    "object": "user",
                    "id": "id",
                    "name": "Test User",
                    "avatar_url": None,
                    "type": "person",
                    "person": {"email": "email"},
                },
            },
            "workspace_name": "test",
        },
    }
    output_record = {
        "object": "user",
        "id": "123",
        "name": "Airbyte",
        "avatar_url": "some url",
        "type": "bot",
        "bot": {
            "owner": {
                "type": "user",
                "info": {
                    "object": "user",
                    "id": "id",
                    "name": "Test User",
                    "avatar_url": None,
                    "type": "person",
                    "person": {"email": "email"},
                },
            },
            "workspace_name": "test",
        },
    }
    assert components_module.NotionUserTransformation().transform(input_record) == output_record


def test_notion_properties_transformation(components_module):
    input_record = {
        "id": "123",
        "properties": {
            "Due date": {"id": "M%3BBw", "type": "date", "date": {"start": "2023-02-23", "end": None, "time_zone": None}},
            "Status": {
                "id": "Z%3ClH",
                "type": "status",
                "status": {"id": "86ddb6ec-0627-47f8-800d-b65afd28be13", "name": "Not started", "color": "default"},
            },
        },
    }

    output_record = {
        "id": "123",
        "properties": [
            {
                "name": "Due date",
                "value": {"id": "M%3BBw", "type": "date", "date": {"start": "2023-02-23", "end": None, "time_zone": None}},
            },
            {
                "name": "Status",
                "value": {
                    "id": "Z%3ClH",
                    "type": "status",
                    "status": {"id": "86ddb6ec-0627-47f8-800d-b65afd28be13", "name": "Not started", "color": "default"},
                },
            },
        ],
    }
    assert components_module.NotionPropertiesTransformation().transform(input_record) == output_record


state_test_records = [
    {"id": "1", "last_edited_time": "2022-01-02T00:00:00.000Z"},
    {"id": "2", "last_edited_time": "2022-01-03T00:00:00.000Z"},
    {"id": "3", "last_edited_time": "2022-01-04T00:00:00.000Z"},
]


def test_blocks_retriever(requests_mock):
    page_response_data = {
        "object": "list",
        "results": [
            {
                "object": "page",
                "id": "page-1",
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-10-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "fuser-1"},
                "cover": None,
                "icon": None,
                "parent": {"type": "database_id", "database_id": "database-id"},
                "archived": False,
                "in_trash": False,
                "properties": {
                    "Name": {
                        "id": "title",
                        "type": "title",
                        "title": [
                            {
                                "type": "text",
                                "text": {"content": "Test Data 1", "link": None},
                                "annotations": {
                                    "bold": False,
                                    "italic": False,
                                    "strikethrough": False,
                                    "underline": False,
                                    "code": False,
                                    "color": "default",
                                },
                                "plain_text": "Test Data 1",
                                "href": None,
                            }
                        ],
                    }
                },
                "url": "https://www.notion.so/url-1",
                "public_url": None,
            }
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "page_or_database",
        "page_or_database": {},
        "request_id": "request-1",
    }
    requests_mock.register_uri(
        "POST",
        "https://api.notion.com/v1/search",
        [{"json": page_response_data}],
    )

    page_blocks_response_data = {
        "object": "list",
        "results": [
            {
                "object": "block",
                "id": "block-id-1",
                "parent": {"type": "page_id", "page_id": "page-1"},
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-10-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "user-1"},
                "has_children": False,
                "archived": False,
                "in_trash": False,
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion Tip: ", "link": None},
                            "annotations": {
                                "bold": True,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Notion Tip: ",
                            "href": None,
                        }
                    ],
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            },
            {
                "object": "block",
                "id": "block-id-2",
                "parent": {"type": "page_id", "page_id": "page-1"},
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-11-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "user-1"},
                "has_children": True,
                "archived": False,
                "in_trash": False,
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion Tip: ", "link": None},
                            "annotations": {
                                "bold": True,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Notion Tip: ",
                            "href": None,
                        }
                    ],
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            },
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "block",
        "block": {},
        "request_id": "request-id-2",
    }
    requests_mock.register_uri(
        "GET",
        "https://api.notion.com/v1/blocks/page-1/children?page_size=100",
        [{"json": page_blocks_response_data}],
    )

    block_children_response_data = {
        "object": "list",
        "results": [
            {
                "object": "block",
                "id": "block-id-3",
                "parent": {"type": "page_id", "page_id": "page-1"},
                "created_time": "2021-10-19T13:33:00.000Z",
                "last_edited_time": "2021-11-19T13:33:00.000Z",
                "created_by": {"object": "user", "id": "user-1"},
                "last_edited_by": {"object": "user", "id": "user-1"},
                "has_children": False,
                "archived": False,
                "in_trash": False,
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Notion Tip: ", "link": None},
                            "annotations": {
                                "bold": True,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "default",
                            },
                            "plain_text": "Notion Tip: ",
                            "href": None,
                        }
                    ],
                    "icon": {"type": "emoji", "emoji": "💡"},
                    "color": "gray_background",
                },
            }
        ],
        "next_cursor": None,
        "has_more": False,
        "type": "block",
        "block": {},
        "request_id": "request-id-2",
    }
    requests_mock.register_uri(
        "GET",
        "https://api.notion.com/v1/blocks/block-id-2/children?page_size=100",
        [{"json": block_children_response_data}],
    )

    config_mock = {"start_date": "2020-01-01T00:00:00.000Z", "credentials": {"auth_type": "token", "token": "abcd"}}
    blocks_stream_name = "blocks"
    catalog = ConfiguredAirbyteCatalogSerializer.load(
        {
            "streams": [
                {
                    "stream": {"name": blocks_stream_name, "json_schema": {}, "supported_sync_modes": ["full_refresh", "incremental"]},
                    "sync_mode": "incremental",
                    "destination_sync_mode": "append",
                }
            ]
        }
    )
    state = StateBuilder().with_stream_state(blocks_stream_name, {}).build()
    source = get_source(config_mock, state)
    output = read(source, config=config_mock, catalog=catalog, state=state)
    assert len(output.records) == 3
