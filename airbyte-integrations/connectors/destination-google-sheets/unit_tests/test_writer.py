#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import pytest
from destination_google_sheets.writer import GoogleSheetsWriter


@pytest.mark.parametrize(
    "row, col, expected",
    [
        (0, 0, "A1"),
        (0, 25, "Z1"),
        (0, 26, "AA1"),
        (99, 18277, "ZZZ100"),
    ],
)
def test_a1_notation(row, col, expected):
    writer = GoogleSheetsWriter(None)
    assert writer._a1_notation(row, col) == expected
