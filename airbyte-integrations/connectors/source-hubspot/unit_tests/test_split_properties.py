#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_hubspot.helpers import APIv1Property, APIv3Property

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit"""
lorem_ipsum = lorem_ipsum.lower().replace(",", "")

many_properties = lorem_ipsum.split(" ") * 1000
few_properties = ["firstname", "lastname", "age", "dob", "id"]


@pytest.mark.parametrize(
    ("cls", "properties", "chunks_expected"),
    (
        (APIv1Property, few_properties, 1),
        (APIv3Property, few_properties, 1),
        (APIv1Property, many_properties, 11),
        (APIv3Property, many_properties, 5),
    ),
)
def test_split_properties(cls, properties, chunks_expected):
    chunked_properties = set()
    index = 0
    for index, chunk in enumerate(cls(properties).split()):
        chunked_properties |= set(chunk.properties)
        as_string = next(iter(chunk.as_url_param().values()))
        assert len(as_string) <= cls.PROPERTIES_PARAM_MAX_LENGTH
    chunks = index + 1
    assert chunked_properties == set(properties)
    assert chunks == chunks_expected
