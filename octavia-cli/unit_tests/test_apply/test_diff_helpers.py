#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import pytest
from octavia_cli.apply import diff_helpers


def test_hash_config():
    data_to_hash = {"example": "foo"}
    assert diff_helpers.hash_config(data_to_hash) == "8d621bd700ff9a864bc603f56b4ec73536110b37d814dd4629767e898da70bef"


@pytest.mark.parametrize(
    "obj, expected_output",
    [
        (diff_helpers.SECRET_MASK, True),
        ("not secret", False),
        ({}, False),
    ],
)
def test_exclude_secrets_from_diff(obj, expected_output):
    assert diff_helpers.exclude_secrets_from_diff(obj, "foo") == expected_output


def test_compute_diff(mocker):
    mocker.patch.object(diff_helpers, "DeepDiff")
    diff = diff_helpers.compute_diff("foo", "bar")
    assert diff == diff_helpers.DeepDiff.return_value
    diff_helpers.DeepDiff.assert_called_with("foo", "bar", view="tree", exclude_obj_callback=diff_helpers.exclude_secrets_from_diff)


@pytest.mark.parametrize(
    "diff_line,expected_message,expected_color",
    [
        ("resource changed from", "E - resource changed from", "yellow"),
        ("resource added", "+ - resource added", "green"),
        ("resource removed", "- - resource removed", "red"),
        ("whatever", " - whatever", None),
    ],
)
def test_display_diff_line(mocker, diff_line, expected_message, expected_color):
    mocker.patch.object(diff_helpers, "click")
    diff_helpers.display_diff_line(diff_line)
    diff_helpers.click.style.assert_called_with(f"\t{expected_message}", fg=expected_color)
    diff_helpers.click.echo.assert_called_with(diff_helpers.click.style.return_value)
