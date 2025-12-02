#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest

from pipelines.airbyte_ci.connectors.test.pipeline import _has_non_metadata_changes


@pytest.mark.parametrize(
    "modified_files,expected_result",
    [
        pytest.param(
            frozenset([Path("/path/to/connector/metadata.yaml")]),
            False,
            id="only_metadata_yaml_changed",
        ),
        pytest.param(
            frozenset(
                [
                    Path("/path/to/connector/metadata.yaml"),
                    Path("/path/to/connector/src/main.py"),
                ]
            ),
            True,
            id="multiple_files_including_metadata_yaml",
        ),
        pytest.param(
            frozenset(
                [
                    Path("/path/to/connector/src/main.py"),
                    Path("/path/to/connector/README.md"),
                ]
            ),
            True,
            id="multiple_files_without_metadata_yaml",
        ),
        pytest.param(
            frozenset(),
            False,
            id="no_modified_files",
        ),
    ],
)
def test_has_non_metadata_changes(mocker, modified_files, expected_result):
    """Test that _has_non_metadata_changes correctly identifies when non-metadata files are modified."""
    context = mocker.Mock()
    context.modified_files = modified_files

    result = _has_non_metadata_changes(context)

    assert result == expected_result
