# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import pytest
from source_gitlab.utils import parse_url


@pytest.mark.parametrize(
    "url, expected",
    (
        ("http://example.com", (True, "http", "example.com")),
        ("http://example", (True, "http", "example")),
        ("test://example.com", (False, "", "")),
        ("https://example.com/test/test2", (False, "", "")),
    ),
)
def test_parse_url(url, expected):
    assert parse_url(url) == expected
