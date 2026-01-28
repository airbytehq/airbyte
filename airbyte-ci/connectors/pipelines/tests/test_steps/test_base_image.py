# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import pytest
from connector_ops.utils import ConnectorLanguage

from pipelines.airbyte_ci.steps.base_image import UpdateBaseImageMetadata


class TestUpdateBaseImageMetadata:
    """Test suite for UpdateBaseImageMetadata step, focusing on major version constraint behavior."""

    @pytest.fixture
    def mock_context(self, mocker):
        """Create a mock connector context."""
        context = mocker.Mock()
        context.connector = mocker.Mock()
        context.connector.language = ConnectorLanguage.MANIFEST_ONLY
        context.connector.metadata = {
            "connectorBuildOptions": {"baseImage": "docker.io/airbyte/source-declarative-manifest:6.60.16@sha256:abc123"}
        }
        context.logger = mocker.Mock()
        return context

    @pytest.fixture
    def mock_connector_directory(self, mocker):
        """Create a mock connector directory."""
        return mocker.Mock()

    @pytest.fixture
    def update_step(self, mock_context, mock_connector_directory):
        """Create an UpdateBaseImageMetadata instance."""
        return UpdateBaseImageMetadata(mock_context, mock_connector_directory)

    @pytest.mark.parametrize(
        "tags,max_major_version,expected_result,description",
        [
            # Test without constraint - should return latest stable version
            (
                ["5.0.0", "6.0.0", "6.1.0", "6.60.16", "7.0.0", "7.1.0", "8.0.0-rc.1"],
                None,
                "7.1.0",
                "without constraint returns latest stable",
            ),
            # Test with constraint - should respect major version limit
            (["5.0.0", "6.0.0", "6.1.0", "6.60.16", "7.0.0", "7.1.0"], 6, "6.60.16", "with constraint returns latest within major version"),
            # Test pre-release exclusion
            (["6.0.0", "6.1.0", "6.2.0-rc.1", "6.2.0-beta.1"], 6, "6.1.0", "excludes pre-release versions"),
            # Test no valid versions within constraint
            (["7.0.0", "8.0.0", "9.0.0"], 6, None, "returns None when no versions match constraint"),
            # Test invalid tags are skipped
            (["invalid", "not-a-version", "6.0.0", "6.1.0", "latest", "main"], 6, "6.1.0", "skips invalid semver tags"),
            # Test empty list
            ([], 6, None, "returns None for empty tag list"),
            # Test patch version comparison
            (["6.60.14", "6.60.15", "6.60.16", "6.60.17", "7.0.0"], 6, "6.60.17", "correctly compares patch versions"),
        ],
    )
    def test_parse_latest_stable_tag(self, update_step, tags, max_major_version, expected_result, description):
        """Test _parse_latest_stable_tag with various scenarios."""
        result = update_step._parse_latest_stable_tag(tags, max_major_version=max_major_version)

        assert result == expected_result, f"Failed: {description}"

    @pytest.mark.parametrize(
        "base_image,expected_major",
        [
            ("docker.io/airbyte/source-declarative-manifest:6.60.16@sha256:abc", 6),
            ("docker.io/airbyte/source-declarative-manifest:7.1.0", 7),
            ("docker.io/airbyte/python-connector-base:1.2.3@sha256:def", 1),
            ("airbyte/java-connector-base:2.0.0", 2),
            ("docker.io/repo:10.5.3@sha256:xyz", 10),
            ("registry.example.com:5000/repo:3.14.159@sha256:abc123", 3),
        ],
    )
    def test_extract_major_version_from_base_image_success(self, update_step, base_image, expected_major):
        """Test that major version is correctly extracted from various base image formats."""
        result = update_step._extract_major_version_from_base_image(base_image)

        assert result == expected_major

    @pytest.mark.parametrize(
        "invalid_base_image",
        [
            "docker.io/airbyte/source-declarative-manifest:invalid-version",
            "docker.io/airbyte/source-declarative-manifest:latest",
            "docker.io/airbyte/source-declarative-manifest",  # No version
            "docker.io/airbyte/source-declarative-manifest:",  # Empty version
            "not-a-valid-image-string",
        ],
    )
    def test_extract_major_version_from_base_image_invalid(self, update_step, invalid_base_image):
        """Test that invalid base images return None and log a warning."""
        result = update_step._extract_major_version_from_base_image(invalid_base_image)

        assert result is None
        # Verify warning was logged
        update_step.context.logger.warning.assert_called()
