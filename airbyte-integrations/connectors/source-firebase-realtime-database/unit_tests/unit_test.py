#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import string

import pytest
from source_firebase_realtime_database.firebase_rtdb import Records
from source_firebase_realtime_database.source import SourceFirebaseRealtimeDatabase


@pytest.mark.parametrize(
    "config, stream_name",
    [
        (
            {"database_name": "my-database", "path": "users"},
            "users",
        ),
        (
            {"database_name": "my-database", "path": "/users"},
            "users",
        ),
        (
            {"database_name": "my-database", "path": "path/to/product-details"},
            "product_details",
        ),
        (
            {"database_name": "my-database", "path": "path/to/product-details/"},
            "product_details",
        ),
        (
            {"database_name": "my-database", "path": ""},
            "my_database",
        ),
    ],
)
def test_stream_name_from(config, stream_name):
    actual = SourceFirebaseRealtimeDatabase.stream_name_from(config)
    expected = stream_name

    assert actual == expected


class PseudoClient:
    """
    Pseudo client producing records which keys and values are ordered ASCII chcaracter
    ex. {"a": "a", "b": "b", "c": "c"}
    """

    def __init__(self, buffer_size):
        self._buffer_size = buffer_size

    def fetch_records(self, start_key=None):
        if start_key:
            start = ord(start_key) - ord("a")
        else:
            start = 0

        end = start + self._buffer_size

        return {c: c for c in string.ascii_lowercase[start:end]}


def test_records():
    buffer_size = 5
    client = PseudoClient(buffer_size)
    records = Records(client)

    expected = [{"key": c, "value": f'"{c}"'} for c in string.ascii_lowercase]
    actual = list(records)

    assert actual == expected
