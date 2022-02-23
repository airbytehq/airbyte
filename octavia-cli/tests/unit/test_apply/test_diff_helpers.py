#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import mock_open, patch

import pytest
from octavia_cli.apply import diff_helpers


def test_secret_mask():
    assert diff_helpers.SECRET_MASK == "**********"


def test_compute_checksum(mocker):
    with patch("builtins.open", mock_open(read_data=b"data")) as mock_file:
        digest = diff_helpers.compute_checksum("test_file_path")
        assert digest == "3a6eb0790f39ac87c94f3856b2dd2c5d110e6811602261a9a923d3bb23adc8b7"
    mock_file.assert_called_with("test_file_path", "rb")


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
