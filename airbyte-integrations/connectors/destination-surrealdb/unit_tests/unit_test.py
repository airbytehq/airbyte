#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import pytest
from destination_surrealdb.destination import normalize_url


def test_invalid_url():
    invalid_input = "invalid_url"
    with pytest.raises(ValueError):
        _ = normalize_url(invalid_input)

    assert True


@pytest.mark.parametrize(
    "input, expected",
    [
        ("rocksdb:test", "rocksdb://test"),
        ("surrealkv:test", "surrealkv://test"),
        ("file:test", "file://test"),
        ("rocksdb://test", "rocksdb://test"),
        ("surrealkv://test", "surrealkv://test"),
        ("file://test", "file://test"),
        ("wss://test", "wss://test"),
        ("wss:test", "wss://test"),
    ],
)
def test_normalize_url(input, expected):
    if expected is None:
        with pytest.raises(ValueError):
            normalize_url(input)
    else:
        assert normalize_url(input) == expected
