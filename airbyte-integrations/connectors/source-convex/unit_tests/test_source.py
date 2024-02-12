#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_convex.source import SourceConvex


def setup_responses():
    sample_shapes_resp = {
        "posts": {
            "type": "object",
            "properties": {
                "_creationTime": {"type": "number"},
                "_id": {"$description": "Id(posts)", "type": "object", "properties": {"$id": {"type": "string"}}},
                "author": {"$description": "Id(users)", "type": "object", "properties": {"$id": {"type": "string"}}},
                "body": {"type": "string"},
                "_ts": {"type": "integer"},
                "_deleted": {"type": "boolean"},
            },
            "$schema": "http://json-schema.org/draft-07/schema#",
        },
        "users": {
            "type": "object",
            "properties": {
                "_creationTime": {"type": "number"},
                "_id": {"$description": "Id(users)", "type": "object", "properties": {"$id": {"type": "string"}}},
                "name": {"type": "string"},
                "tokenIdentifier": {"type": "string"},
                "_ts": {"type": "integer"},
                "_deleted": {"type": "boolean"},
            },
            "$schema": "http://json-schema.org/draft-07/schema#",
        },
    }
    responses.add(
        responses.GET,
        "https://murky-swan-635.convex.cloud/api/json_schemas?deltaSchema=true&format=json",
        json=sample_shapes_resp,
    )
    responses.add(
        responses.GET,
        "https://curious-giraffe-964.convex.cloud/api/json_schemas?deltaSchema=true&format=json",
        json={"code": "Error code", "message": "Error message"},
        status=400,
    )


@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceConvex()
    logger_mock = MagicMock()
    assert source.check_connection(
        logger_mock,
        {
            "deployment_url": "https://murky-swan-635.convex.cloud",
            "access_key": "test_api_key",
        },
    ) == (True, None)


@responses.activate
def test_check_bad_connection(mocker):
    setup_responses()
    source = SourceConvex()
    logger_mock = MagicMock()
    assert source.check_connection(
        logger_mock,
        {
            "deployment_url": "https://curious-giraffe-964.convex.cloud",
            "access_key": "test_api_key",
        },
    ) == (False, "Connection to Convex via json_schemas endpoint failed: 400: Error code: Error message")


@responses.activate
def test_streams(mocker):
    setup_responses()
    source = SourceConvex()
    streams = source.streams(
        {
            "deployment_url": "https://murky-swan-635.convex.cloud",
            "access_key": "test_api_key",
        }
    )
    assert len(streams) == 2
    streams.sort(key=lambda stream: stream.table_name)
    assert streams[0].table_name == "posts"
    assert streams[1].table_name == "users"
    assert all(stream.deployment_url == "https://murky-swan-635.convex.cloud" for stream in streams)
    assert all(stream._session.auth.get_auth_header() == {"Authorization": "Convex test_api_key"} for stream in streams)
    shapes = [stream.get_json_schema() for stream in streams]
    assert all(shape["type"] == "object" for shape in shapes)
    properties = [shape["properties"] for shape in shapes]
    assert [
        props["_id"]
        == {
            "type": "object",
            "properties": {
                "$id": {"type": "string"},
            },
        }
        for props in properties
    ]
    assert [props["_ts"] == {"type": "number"} for props in properties]
    assert [props["_creationTime"] == {"type": "number"} for props in properties]
    assert set(properties[0].keys()) == set(
        ["_id", "_ts", "_deleted", "_creationTime", "author", "body", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at"]
    )
    assert set(properties[1].keys()) == set(
        ["_id", "_ts", "_deleted", "_creationTime", "name", "tokenIdentifier", "_ab_cdc_lsn", "_ab_cdc_updated_at", "_ab_cdc_deleted_at"]
    )
