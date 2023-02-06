#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_looker.streams import LookerStream


def test_format_null_in_schema():
    schema = {'type': ['null', 'object'], 'properties': {'field': {'type': 'object', 'properties': {'field': {'type': 'number'}}}}}
    output = LookerStream.format_null_in_schema(schema)
    expected = {'type': ['null', 'object'], 'properties': {'field': {'type': ['null', 'object'], 'properties': {'field': {'type': ['null', 'number']}}}}}
    assert output == expected
