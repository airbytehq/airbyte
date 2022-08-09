#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json

import pytest
from source_facebook_pages.streams import Post


class MockResponse:
    def __init__(self, value):
        self.value = value

    def json(self):
        return json.loads(self.value)


@pytest.mark.parametrize(
    "data, expected",
    [
        ('{"data":[1, 2, 3],"paging":{"cursors":{"after": "next"}}}', "next"),
        ('{"data":[1, 2, 3]}', None),
        ('{"data": []}', None),
    ],
)
def test_pagination(data, expected):
    stream = Post()
    assert stream.next_page_token(MockResponse(data)).get("after") == expected
