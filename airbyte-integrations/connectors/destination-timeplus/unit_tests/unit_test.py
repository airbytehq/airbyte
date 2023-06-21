#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from destination_timeplus import DestinationTimeplus


def test_type_mapping():
    expected = {
        "float": {"type": "number"},
        "bool": {"type": "boolean"},
        "string": {"type": "string"},
        "integer": {"type": "integer"},
        "array(integer)": {"type": "array", "items": {"type": "integer"}},
    }
    for k, v in expected.items():
        assert k == DestinationTimeplus.type_mapping(v)
