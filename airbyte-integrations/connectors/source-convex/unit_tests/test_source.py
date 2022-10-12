#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import responses
from source_convex.source import SourceConvex


def setup_responses():
    sample_shapes_resp = {
        "posts": {
            "numValues": 6,
            "variant": {
                "type": "Object",
                "fields": [
                    {
                        "fieldName": "_creationTime",
                        "shape": {
                            "numValues": 6,
                            "variant": {
                                "type": "Float64",
                                "float64Range": {
                                    "int": {
                                        "minusInfToMinExactF64": 0,
                                        "minExactF64ToZero": 0,
                                        "zeroToMaxExactF64": 0,
                                        "maxExactF64ToPosInf": 0,
                                    },
                                    "fractional": 6,
                                    "negZero": 0,
                                    "nan": 0,
                                    "inf": 0,
                                },
                            },
                        },
                    },
                    {"fieldName": "_id", "shape": {"numValues": 6, "variant": {"type": "Id", "tableName": "posts"}}},
                    {"fieldName": "author", "shape": {"numValues": 6, "variant": {"type": "Id", "tableName": "users"}}},
                    {"fieldName": "body", "shape": {"numValues": 6, "variant": {"type": "String"}}},
                ],
            },
        },
        "users": {
            "numValues": 2,
            "variant": {
                "type": "Object",
                "fields": [
                    {
                        "fieldName": "_creationTime",
                        "shape": {
                            "numValues": 2,
                            "variant": {
                                "type": "Float64",
                                "float64Range": {
                                    "int": {
                                        "minusInfToMinExactF64": 0,
                                        "minExactF64ToZero": 0,
                                        "zeroToMaxExactF64": 0,
                                        "maxExactF64ToPosInf": 0,
                                    },
                                    "fractional": 2,
                                    "negZero": 0,
                                    "nan": 0,
                                    "inf": 0,
                                },
                            },
                        },
                    },
                    {"fieldName": "_id", "shape": {"numValues": 2, "variant": {"type": "Id", "tableName": "users"}}},
                    {"fieldName": "name", "shape": {"numValues": 2, "variant": {"type": "String"}}},
                    {"fieldName": "tokenIdentifier", "shape": {"numValues": 2, "variant": {"type": "String"}}},
                ],
            },
        },
    }
    responses.add(
        responses.GET,
        "https://murky-swan-635.convex.cloud/api/0.2.0/shapes2",
        json=sample_shapes_resp,
    )


@responses.activate
def test_check_connection(mocker):
    setup_responses()
    source = SourceConvex()
    logger_mock = MagicMock()
    assert source.check_connection(
        logger_mock,
        {
            "instance_name": "murky-swan-635",
            "access_key": "test_api_key",
        },
    ) == (True, None)


@responses.activate
def test_streams(mocker):
    setup_responses()
    source = SourceConvex()
    streams = source.streams(
        {
            "instance_name": "murky-swan-635",
            "access_key": "test_api_key",
        }
    )
    assert len(streams) == 2
    streams.sort(key=lambda stream: stream.table_name)
    assert streams[0].table_name == "posts"
    assert streams[1].table_name == "users"
    assert all(stream.instance_name == "murky-swan-635" for stream in streams)
    assert all(stream.authenticator.get_auth_header() == {"Authorization": "Convex test_api_key"} for stream in streams)
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
    assert set(properties[0].keys()) == set(["_id", "_ts", "_creationTime", "author", "body"])
    assert set(properties[1].keys()) == set(["_id", "_ts", "_creationTime", "name", "tokenIdentifier"])
