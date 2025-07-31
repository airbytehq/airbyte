#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import pytest
from source_smartsheets_2 import utils


@pytest.mark.parametrize(
    ("name", "expected", "transformations"),
    [
        ("Revenue Recognition %", "Revenue Recognition Percent", ["Make common substitutions"]),
        ("Revenue Recognition %", "revenue recognition %", ["Make all lower case"]),
        ("Revenue Recognition %", "REVENUE RECOGNITION %", ["Make all upper case"]),
        ("Revenue Recognition %", "RevenueRecognition%", ["Strip whitespace"]),
        (" Revenue Recognition % ", "Revenue Recognition %", ["Trim outer whitespace"]),
        ("Revenue Recognition %", "Revenue_Recognition_%", ["Whitespace into underscores"]),
        ("Foo-Bar", "Foo_Bar", ["Hyphens into underscores"]),
        ("1st Responder", "_1st Responder", ["Ensure starts with identifier character"]),
        ("Revenue Recognition %", "RevenueRecognition", ["Strip non-identifier characters"]),
        ("Revenue Recognition %", "Revenue_x20Recognition_x20_x25", ["Replace non-identifier characters with hex encoding"]),
        (
            "Revenue Recognition %",
            "revenue_recognition_percent",
            [
                "Make common substitutions",
                "Make all lower case",
                "Trim outer whitespace",
                "Whitespace into underscores",
                "Ensure starts with identifier character",
                "Strip non-identifier characters",
            ],
        ),
        (
            "R/A/I/D",
            "raid",
            [
                "Make common substitutions",
                "Make all lower case",
                "Trim outer whitespace",
                "Whitespace into underscores",
                "Ensure starts with identifier character",
                "Strip non-identifier characters",
            ],
        ),
    ],
)
def test_column_name_normalization(name, expected, transformations):
    """Tests that the column name normalization logic works as expected."""
    normalized = utils.normalize_column_name(name, transformations)
    assert normalized == expected
