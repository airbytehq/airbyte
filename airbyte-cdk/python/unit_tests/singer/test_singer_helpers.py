#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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
