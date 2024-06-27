# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, List, Mapping, MutableMapping, Optional, Union
from unittest.mock import MagicMock

import pytest
import requests_mock
from airbyte_cdk.models import (
    AirbyteMessage,
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
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource


def _run_read(
    manifest: Mapping[str, Any],
    config: Mapping[str, Any],
    stream_name: str,
    state: Optional[Union[List[AirbyteStateMessage], MutableMapping[str, Any]]] = None,
) -> List[AirbyteMessage]:
    source = ManifestDeclarativeSource(source_config=manifest)
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(name=stream_name, json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
                sync_mode=SyncMode.incremental,
                destination_sync_mode=DestinationSyncMode.append,
            )
        ]
    )
    logger = MagicMock()
    return list(source.read(logger, config, catalog, state))


@pytest.mark.parametrize(
    "test_name, manifest, mock_requests, expected_records, initial_state, expected_state",
    [
        (
            "test_incremental_parent_state",
            {
                "version": "0.51.42",
                "type": "DeclarativeSource",
                "check": {"type": "CheckStream", "stream_names": ["post_comment_votes"]},
                "definitions": {
                    "basic_authenticator": {
                        "type": "BasicHttpAuthenticator",
                        "username": "{{ config['credentials']['email'] + '/token' }}",
                        "password": "{{ config['credentials']['api_token'] }}",
                    },
                    "retriever": {
                        "type": "SimpleRetriever",
                        "requester": {
                            "type": "HttpRequester",
                            "url_base": "https://api.example.com",
                            "http_method": "GET",
                            "authenticator": "#/definitions/basic_authenticator",
                        },
                        "record_selector": {
                            "type": "RecordSelector",
                            "extractor": {
                                "type": "DpathExtractor",
                                "field_path": ["{{ parameters.get('data_path') or parameters['name'] }}"],
                            },
                            "schema_normalization": "Default",
                        },
                        "paginator": {
                            "type": "DefaultPaginator",
                            "page_size_option": {"type": "RequestOption", "field_name": "per_page", "inject_into": "request_parameter"},
                            "pagination_strategy": {
                                "type": "CursorPagination",
                                "page_size": 100,
                                "cursor_value": "{{ response.get('next_page', {}) }}",
                                "stop_condition": "{{ not response.get('next_page', {}) }}",
                            },
                            "page_token_option": {"type": "RequestPath"},
                        },
                    },
                    "cursor_incremental_sync": {
                        "type": "DatetimeBasedCursor",
                        "cursor_datetime_formats": ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"],
                        "datetime_format": "%Y-%m-%dT%H:%M:%SZ",
                        "cursor_field": "{{ parameters.get('cursor_field',  'updated_at') }}",
                        "start_datetime": {"datetime": "{{ config.get('start_date')}}"},
                        "start_time_option": {"inject_into": "request_parameter", "field_name": "start_time", "type": "RequestOption"},
                    },
                    "posts_stream": {
                        "type": "DeclarativeStream",
                        "name": "posts",
                        "primary_key": ["id"],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "updated_at": {"type": "string", "format": "date-time"},
                                    "title": {"type": "string"},
                                    "content": {"type": "string"},
                                },
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.example.com",
                                "path": "/community/posts",
                                "http_method": "GET",
                                "authenticator": "#/definitions/basic_authenticator",
                            },
                            "record_selector": "#/definitions/retriever/record_selector",
                            "paginator": "#/definitions/retriever/paginator",
                        },
                        "incremental_sync": "#/definitions/cursor_incremental_sync",
                        "$parameters": {
                            "name": "posts",
                            "path": "community/posts",
                            "data_path": "posts",
                            "cursor_field": "updated_at",
                            "primary_key": "id",
                        },
                    },
                    "post_comments_stream": {
                        "type": "DeclarativeStream",
                        "name": "post_comments",
                        "primary_key": ["id"],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "updated_at": {"type": "string", "format": "date-time"},
                                    "post_id": {"type": "integer"},
                                    "comment": {"type": "string"},
                                },
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.example.com",
                                "path": "/community/posts/{{ stream_slice.id }}/comments",
                                "http_method": "GET",
                                "authenticator": "#/definitions/basic_authenticator",
                            },
                            "record_selector": {
                                "type": "RecordSelector",
                                "extractor": {"type": "DpathExtractor", "field_path": ["comments"]},
                                "record_filter": {
                                    "condition": "{{ record['updated_at'] >= stream_state.get('updated_at', config.get('start_date')) }}"
                                },
                            },
                            "paginator": "#/definitions/retriever/paginator",
                            "partition_router": {
                                "type": "SubstreamPartitionRouter",
                                "parent_stream_configs": [
                                    {
                                        "stream": "#/definitions/posts_stream",
                                        "parent_key": "id",
                                        "partition_field": "id",
                                        "incremental_dependency": True,
                                    }
                                ],
                            },
                        },
                        "incremental_sync": {
                            "type": "DatetimeBasedCursor",
                            "cursor_datetime_formats": ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z"],
                            "datetime_format": "%Y-%m-%dT%H:%M:%SZ",
                            "cursor_field": "{{ parameters.get('cursor_field',  'updated_at') }}",
                            "start_datetime": {"datetime": "{{ config.get('start_date') }}"},
                        },
                        "$parameters": {
                            "name": "post_comments",
                            "path": "community/posts/{{ stream_slice.id }}/comments",
                            "data_path": "comments",
                            "cursor_field": "updated_at",
                            "primary_key": "id",
                        },
                    },
                    "post_comment_votes_stream": {
                        "type": "DeclarativeStream",
                        "name": "post_comment_votes",
                        "primary_key": ["id"],
                        "schema_loader": {
                            "type": "InlineSchemaLoader",
                            "schema": {
                                "$schema": "http://json-schema.org/schema#",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "created_at": {"type": "string", "format": "date-time"},
                                    "comment_id": {"type": "integer"},
                                    "vote": {"type": "number"},
                                },
                                "type": "object",
                            },
                        },
                        "retriever": {
                            "type": "SimpleRetriever",
                            "requester": {
                                "type": "HttpRequester",
                                "url_base": "https://api.example.com",
                                "path": "/community/posts/{{ stream_slice.parent_slice.id }}/comments/{{ stream_slice.id }}/votes",
                                "http_method": "GET",
                                "authenticator": "#/definitions/basic_authenticator",
                            },
                            "record_selector": "#/definitions/retriever/record_selector",
                            "paginator": "#/definitions/retriever/paginator",
                            "partition_router": {
                                "type": "SubstreamPartitionRouter",
                                "parent_stream_configs": [
                                    {
                                        "stream": "#/definitions/post_comments_stream",
                                        "parent_key": "id",
                                        "partition_field": "id",
                                        "incremental_dependency": True,
                                    }
                                ],
                            },
                        },
                        "incremental_sync": "#/definitions/cursor_incremental_sync",
                        "$parameters": {
                            "name": "post_comment_votes",
                            "path": "community/posts/{{ stream_slice.parent_slice.id }}/comments/{{ stream_slice.id }}/votes",
                            "data_path": "votes",
                            "cursor_field": "created_at",
                            "primary_key": "id",
                        },
                    },
                },
                "streams": [
                    {"$ref": "#/definitions/posts_stream"},
                    {"$ref": "#/definitions/post_comments_stream"},
                    {"$ref": "#/definitions/post_comment_votes_stream"},
                ],
            },
            [
                # Fetch the first page of posts
                (
                    "https://api.example.com/community/posts?per_page=100&start_time=2024-01-05T00:00:00Z",
                    {
                        "posts": [{"id": 1, "updated_at": "2024-01-30T00:00:00Z"}, {"id": 2, "updated_at": "2024-01-29T00:00:00Z"}],
                        "next_page": "https://api.example.com/community/posts?per_page=100&start_time=2024-01-05T00:00:00Z&page=2",
                    },
                ),
                # Fetch the second page of posts
                (
                    "https://api.example.com/community/posts?per_page=100&start_time=2024-01-05T00:00:00Z&page=2",
                    {"posts": [{"id": 3, "updated_at": "2024-01-28T00:00:00Z"}]},
                ),
                # Fetch the first page of comments for post 1
                (
                    "https://api.example.com/community/posts/1/comments?per_page=100",
                    {
                        "comments": [
                            {"id": 9, "post_id": 1, "updated_at": "2023-01-01T00:00:00Z"},
                            {"id": 10, "post_id": 1, "updated_at": "2024-01-25T00:00:00Z"},
                            {"id": 11, "post_id": 1, "updated_at": "2024-01-24T00:00:00Z"},
                        ],
                        "next_page": "https://api.example.com/community/posts/1/comments?per_page=100&page=2",
                    },
                ),
                # Fetch the second page of comments for post 1
                (
                    "https://api.example.com/community/posts/1/comments?per_page=100&page=2",
                    {"comments": [{"id": 12, "post_id": 1, "updated_at": "2024-01-23T00:00:00Z"}]},
                ),
                # Fetch the first page of votes for comment 10 of post 1
                (
                    "https://api.example.com/community/posts/1/comments/10/votes?per_page=100&start_time=2024-01-02T00:00:00Z",
                    {
                        "votes": [{"id": 100, "comment_id": 10, "created_at": "2024-01-15T00:00:00Z"}],
                        "next_page": "https://api.example.com/community/posts/1/comments/10/votes?per_page=100&page=2&start_time=2024-01-01T00:00:01Z",
                    },
                ),
                # Fetch the second page of votes for comment 10 of post 1
                (
                    "https://api.example.com/community/posts/1/comments/10/votes?per_page=100&page=2&start_time=2024-01-01T00:00:01Z",
                    {"votes": [{"id": 101, "comment_id": 10, "created_at": "2024-01-14T00:00:00Z"}]},
                ),
                # Fetch the first page of votes for comment 11 of post 1
                (
                    "https://api.example.com/community/posts/1/comments/11/votes?per_page=100&start_time=2024-01-03T00:00:00Z",
                    {"votes": [{"id": 102, "comment_id": 11, "created_at": "2024-01-13T00:00:00Z"}]},
                ),
                # Fetch the first page of votes for comment 12 of post 1
                ("https://api.example.com/community/posts/1/comments/12/votes?per_page=100&start_time=2024-01-01T00:00:01Z", {"votes": []}),
                # Fetch the first page of comments for post 2
                (
                    "https://api.example.com/community/posts/2/comments?per_page=100",
                    {
                        "comments": [{"id": 20, "post_id": 2, "updated_at": "2024-01-22T00:00:00Z"}],
                        "next_page": "https://api.example.com/community/posts/2/comments?per_page=100&page=2",
                    },
                ),
                # Fetch the second page of comments for post 2
                (
                    "https://api.example.com/community/posts/2/comments?per_page=100&page=2",
                    {"comments": [{"id": 21, "post_id": 2, "updated_at": "2024-01-21T00:00:00Z"}]},
                ),
                # Fetch the first page of votes for comment 20 of post 2
                (
                    "https://api.example.com/community/posts/2/comments/20/votes?per_page=100&start_time=2024-01-01T00:00:01Z",
                    {"votes": [{"id": 200, "comment_id": 20, "created_at": "2024-01-12T00:00:00Z"}]},
                ),
                # Fetch the first page of votes for comment 21 of post 2
                (
                    "https://api.example.com/community/posts/2/comments/21/votes?per_page=100&start_time=2024-01-01T00:00:01Z",
                    {"votes": [{"id": 201, "comment_id": 21, "created_at": "2024-01-12T00:00:15Z"}]},
                ),
                # Fetch the first page of comments for post 3
                (
                    "https://api.example.com/community/posts/3/comments?per_page=100",
                    {"comments": [{"id": 30, "post_id": 3, "updated_at": "2024-01-09T00:00:00Z"}]},
                ),
                # Fetch the first page of votes for comment 30 of post 3
                (
                    "https://api.example.com/community/posts/3/comments/30/votes?per_page=100",
                    {"votes": [{"id": 300, "comment_id": 30, "created_at": "2024-01-10T00:00:00Z"}]},
                ),
            ],
            # Expected records
            [
                {"id": 100, "comment_id": 10, "created_at": "2024-01-15T00:00:00Z"},
                {"id": 101, "comment_id": 10, "created_at": "2024-01-14T00:00:00Z"},
                {"id": 102, "comment_id": 11, "created_at": "2024-01-13T00:00:00Z"},
                {"id": 200, "comment_id": 20, "created_at": "2024-01-12T00:00:00Z"},
                {"id": 201, "comment_id": 21, "created_at": "2024-01-12T00:00:15Z"},
                {"id": 300, "comment_id": 30, "created_at": "2024-01-10T00:00:00Z"},
            ],
            # Initial state
            [
                AirbyteStateMessage(
                    type=AirbyteStateType.STREAM,
                    stream=AirbyteStreamState(
                        stream_descriptor=StreamDescriptor(name="post_comment_votes", namespace=None),
                        stream_state=AirbyteStateBlob.parse_obj(
                            {
                                "parent_state": {
                                    "post_comments": {
                                        "states": [
                                            {"partition": {"id": 1, "parent_slice": {}}, "cursor": {"updated_at": "2023-01-04T00:00:00Z"}}
                                        ],
                                        "parent_state": {"posts": {"updated_at": "2024-01-05T00:00:00Z"}},
                                    }
                                },
                                "states": [
                                    {
                                        "partition": {"id": 10, "parent_slice": {"id": 1, "parent_slice": {}}},
                                        "cursor": {"created_at": "2024-01-02T00:00:00Z"},
                                    },
                                    {
                                        "partition": {"id": 11, "parent_slice": {"id": 1, "parent_slice": {}}},
                                        "cursor": {"created_at": "2024-01-03T00:00:00Z"},
                                    },
                                ],
                            }
                        ),
                    ),
                )
            ],
            # Expected state
            {
                "states": [
                    {
                        "partition": {"id": 10, "parent_slice": {"id": 1, "parent_slice": {}}},
                        "cursor": {"created_at": "2024-01-15T00:00:00Z"},
                    },
                    {
                        "partition": {"id": 11, "parent_slice": {"id": 1, "parent_slice": {}}},
                        "cursor": {"created_at": "2024-01-13T00:00:00Z"},
                    },
                    {
                        "partition": {"id": 20, "parent_slice": {"id": 2, "parent_slice": {}}},
                        "cursor": {"created_at": "2024-01-12T00:00:00Z"},
                    },
                    {
                        "partition": {"id": 21, "parent_slice": {"id": 2, "parent_slice": {}}},
                        "cursor": {"created_at": "2024-01-12T00:00:15Z"},
                    },
                    {
                        "partition": {"id": 30, "parent_slice": {"id": 3, "parent_slice": {}}},
                        "cursor": {"created_at": "2024-01-10T00:00:00Z"},
                    },
                ],
                "parent_state": {
                    "post_comments": {
                        "states": [
                            {"partition": {"id": 1, "parent_slice": {}}, "cursor": {"updated_at": "2024-01-25T00:00:00Z"}},
                            {"partition": {"id": 2, "parent_slice": {}}, "cursor": {"updated_at": "2024-01-22T00:00:00Z"}},
                            {"partition": {"id": 3, "parent_slice": {}}, "cursor": {"updated_at": "2024-01-09T00:00:00Z"}},
                        ],
                        "parent_state": {"posts": {"updated_at": "2024-01-30T00:00:00Z"}},
                    }
                },
            },
        ),
    ],
)
def test_incremental_parent_state(test_name, manifest, mock_requests, expected_records, initial_state, expected_state):
    _stream_name = "post_comment_votes"
    config = {"start_date": "2024-01-01T00:00:01Z", "credentials": {"email": "email", "api_token": "api_token"}}

    with requests_mock.Mocker() as m:
        for url, response in mock_requests:
            m.get(url, json=response)

        output = _run_read(manifest, config, _stream_name, initial_state)
        output_data = [message.record.data for message in output if message.record]

        assert output_data == expected_records
        final_state = [message.state.stream.stream_state.dict() for message in output if message.state]
        print("final_state", final_state[-1])
        assert final_state[-1] == expected_state
