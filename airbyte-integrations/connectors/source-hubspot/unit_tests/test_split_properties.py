#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from source_hubspot.streams import split_properties

lorem_ipsum = """Lorem ipsum dolor sit amet, consectetur adipiscing elit"""
lorem_ipsum = lorem_ipsum.lower().replace(",", "")

many_properties = lorem_ipsum.split(" ") * 100
few_properties = ["firstname", "lastname", "age", "dob", "id"]


@pytest.mark.parametrize(("properties", "chunks_expected"), ((few_properties, 1), (many_properties, 2)))
def test_split_properties(properties, chunks_expected):
    chunked_properties = set()
    index = 0
    for index, chunk in enumerate(split_properties(properties)):
        chunked_properties |= set(chunk)
    chunks = index + 1
    assert chunked_properties == set(properties)
    assert chunks == chunks_expected
