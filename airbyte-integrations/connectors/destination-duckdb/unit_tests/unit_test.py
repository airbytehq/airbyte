# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from destination_duckdb.destination import DestinationDuckdb, validated_sql_name


def test_read_invalid_path():
    invalid_input = "/test.duckdb"
    with pytest.raises(ValueError):
        _ = DestinationDuckdb._get_destination_path(invalid_input)

    assert True


@pytest.mark.parametrize(
    "input, expected",
    [
        ("test", "test"),
        ("test_123", "test_123"),
        ("test;123", None),
        ("test123;", None),
        ("test-123", None),
        ("test 123", None),
        ("test.123", None),
        ("test,123", None),
        ("test!123", None),
    ],
)
def test_validated_sql_name(input, expected):
    if expected is None:
        with pytest.raises(ValueError):
            validated_sql_name(input)
    else:
        assert validated_sql_name(input) == expected
