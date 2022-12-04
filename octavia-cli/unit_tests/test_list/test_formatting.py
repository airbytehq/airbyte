#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from octavia_cli.list import formatting

PADDING = 2


@pytest.mark.parametrize(
    "test_data,expected_columns_width",
    [
        ([["a", "___10chars"], ["e", "f"]], [1 + PADDING, 10 + PADDING]),
        ([["a", "___10chars"], ["e", "____11chars"]], [1 + PADDING, 11 + PADDING]),
        ([[""]], [PADDING]),
    ],
)
def test_compute_columns_width(test_data, expected_columns_width):
    columns_width = formatting.compute_columns_width(test_data, PADDING)
    assert columns_width == expected_columns_width


@pytest.mark.parametrize("input_camelcased,expected_output", [("camelCased", "CAMEL CASED"), ("notcamelcased", "NOTCAMELCASED")])
def test_camelcased_to_uppercased_spaced(input_camelcased, expected_output):
    assert formatting.camelcased_to_uppercased_spaced(input_camelcased) == expected_output


@pytest.mark.parametrize(
    "test_data,columns_width,expected_output",
    [
        ([["a", "___10chars"], ["e", "____11chars"]], [1 + PADDING, 11 + PADDING], "a  ___10chars   \ne  ____11chars  "),
    ],
)
def test_display_as_table(mocker, test_data, columns_width, expected_output):
    mocker.patch.object(formatting, "compute_columns_width", mocker.Mock(return_value=columns_width))
    assert formatting.display_as_table(test_data) == expected_output


def test_format_column_names():
    columns_to_format = ["camelCased"]
    formatted_columns = formatting.format_column_names(columns_to_format)
    assert len(formatted_columns) == 1
    for i, c in enumerate(formatted_columns):
        assert c == formatting.camelcased_to_uppercased_spaced(columns_to_format[i])
