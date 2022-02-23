#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import copy

from airbyte_cdk.sources.singer import SingerHelper

basic_singer_catalog = {
    "streams": [
        {
            "type": "SCHEMA",
            "stream": "users",
            "schema": {
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "updated_at": {"type": "string", "format": "date-time"},
                }
            },
            "key_properties": ["id"],
            "bookmark_properties": ["updated_at"],
        }
    ]
}


def test_singer_catalog_to_airbyte_catalog():
    airbyte_catalog = SingerHelper.singer_catalog_to_airbyte_catalog(
        singer_catalog=basic_singer_catalog, sync_mode_overrides={}, primary_key_overrides={}
    )

    user_stream = airbyte_catalog.streams[0]
    assert user_stream.source_defined_primary_key == [["id"]]


def test_singer_catalog_to_airbyte_catalog_composite_pk():
    singer_catalog = copy.deepcopy(basic_singer_catalog)
    singer_catalog["streams"][0]["key_properties"] = ["id", "name"]

    airbyte_catalog = SingerHelper.singer_catalog_to_airbyte_catalog(
        singer_catalog=singer_catalog, sync_mode_overrides={}, primary_key_overrides={}
    )

    user_stream = airbyte_catalog.streams[0]
    assert user_stream.source_defined_primary_key == [["id"], ["name"]]


def test_singer_catalog_to_airbyte_catalog_pk_override():
    airbyte_catalog = SingerHelper.singer_catalog_to_airbyte_catalog(
        singer_catalog=basic_singer_catalog, sync_mode_overrides={}, primary_key_overrides={"users": ["name"]}
    )

    user_stream = airbyte_catalog.streams[0]
    assert user_stream.source_defined_primary_key == [["name"]]
