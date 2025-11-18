#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch

import pytest

from metadata_service.helpers.gcs import is_version_yanked


class TestIsVersionYanked:
    """Tests for is_version_yanked function."""

    def test_is_version_yanked_returns_true_when_marker_exists(self):
        """Test that is_version_yanked returns True when .yanked marker exists."""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_bucket.blob.return_value = mock_blob

        result = is_version_yanked(mock_bucket, "airbyte/source-postgres", "3.7.0")

        assert result is True
        mock_bucket.blob.assert_called_once_with("metadata/airbyte/source-postgres/3.7.0/.yanked")
        mock_blob.exists.assert_called_once()

    def test_is_version_yanked_returns_false_when_marker_does_not_exist(self):
        """Test that is_version_yanked returns False when .yanked marker does not exist."""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob

        result = is_version_yanked(mock_bucket, "airbyte/source-postgres", "3.7.0")

        assert result is False
        mock_bucket.blob.assert_called_once_with("metadata/airbyte/source-postgres/3.7.0/.yanked")
        mock_blob.exists.assert_called_once()

    @pytest.mark.parametrize(
        "docker_repository,version,expected_path",
        [
            ("airbyte/source-postgres", "3.7.0", "metadata/airbyte/source-postgres/3.7.0/.yanked"),
            ("airbyte/destination-bigquery", "1.2.3", "metadata/airbyte/destination-bigquery/1.2.3/.yanked"),
            ("airbyte/source-hubspot", "5.0.0-rc.1", "metadata/airbyte/source-hubspot/5.0.0-rc.1/.yanked"),
        ],
    )
    def test_is_version_yanked_constructs_correct_path(self, docker_repository, version, expected_path):
        """Test that is_version_yanked constructs the correct GCS path for different connectors."""
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        mock_bucket.blob.return_value = mock_blob

        is_version_yanked(mock_bucket, docker_repository, version)

        mock_bucket.blob.assert_called_once_with(expected_path)
