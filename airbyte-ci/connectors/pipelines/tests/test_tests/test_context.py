#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import Path

import pytest

CONNECTOR_CODE_DIRECTORY = Path("/path/to/connector")


@pytest.mark.parametrize(
    "modified_files,expected_result",
    [
        pytest.param(
            frozenset([CONNECTOR_CODE_DIRECTORY / "unit_tests" / "test_source.py"]),
            True,
            id="only_unit_tests_changed",
        ),
        pytest.param(
            frozenset([CONNECTOR_CODE_DIRECTORY / "integration_tests" / "test_integration.py"]),
            True,
            id="only_integration_tests_changed",
        ),
        pytest.param(
            frozenset(
                [
                    CONNECTOR_CODE_DIRECTORY / "unit_tests" / "test_source.py",
                    CONNECTOR_CODE_DIRECTORY / "integration_tests" / "test_integration.py",
                ]
            ),
            True,
            id="both_unit_and_integration_tests_changed",
        ),
        pytest.param(
            frozenset(
                [
                    CONNECTOR_CODE_DIRECTORY / "unit_tests" / "test_source.py",
                    CONNECTOR_CODE_DIRECTORY / "src" / "main.py",
                ]
            ),
            False,
            id="unit_tests_and_source_code_changed",
        ),
        pytest.param(
            frozenset([CONNECTOR_CODE_DIRECTORY / "src" / "main.py"]),
            False,
            id="only_source_code_changed",
        ),
        pytest.param(
            frozenset(),
            True,
            id="no_modified_files",
        ),
    ],
)
def test_test_only_change(mocker, modified_files, expected_result):
    """Test that test_only_change correctly identifies when only test files are modified."""
    from pipelines.airbyte_ci.connectors.test.context import ConnectorTestContext

    mock_connector = mocker.Mock()
    mock_connector.code_directory = CONNECTOR_CODE_DIRECTORY

    mock_context = mocker.Mock(spec=ConnectorTestContext)
    mock_context.modified_files = modified_files
    mock_context.connector = mock_connector

    result = ConnectorTestContext.test_only_change.fget(mock_context)

    assert result == expected_result
