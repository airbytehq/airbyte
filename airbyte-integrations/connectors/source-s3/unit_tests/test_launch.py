# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from source_s3.v4.source import SourceS3


@patch("builtins.print")
# @patch("pathlib.Path.read_text")
def test_create_with_valid_catalog(mock_print):
    # Mock a valid catalog configuration
    source = SourceS3.create(
        configured_catalog_path="./unit_tests/sample_files/catalog.json",
    )

    assert isinstance(source, SourceS3)
    assert source.catalog is not None
    assert source.catalog.streams[0].stream.name == "test"
    mock_print.assert_not_called()


@patch("builtins.print")
@patch("pathlib.Path.read_text")
def test_create_with_invalid_catalog(mock_read_text, mock_print):
    # Mock an invalid catalog configuration
    mock_read_text.side_effect = Exception("Invalid catalog")

    with pytest.raises(SystemExit) as cm:
        SourceS3.create(configured_catalog_path="unit_tests/sample_files/catalog.json")

    assert cm.value.code == 1
    mock_print.assert_called_once()
    printed_message = mock_print.call_args[0][0]
    assert "Error starting the sync" in printed_message


# @patch("sys.argv", new_callable=list)
def test_launch_with_args():
    # Set up mock arguments and a valid catalog configuration
    with patch.object(SourceS3, "create", return_value=MagicMock()) as mock_create:
        with patch("source_s3.v4.source.launch") as mock_launch:
            SourceS3.launch(
                args=["check", "--config", "unit_tests/sample_files/v4_config.json"],
            )

            mock_create.assert_called_once()
            mock_launch.assert_called_once()
