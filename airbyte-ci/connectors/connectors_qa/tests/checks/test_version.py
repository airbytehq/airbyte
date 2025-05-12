# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock, patch

import pytest
import semver  # type: ignore
from connector_ops.utils import Connector

from connectors_qa.checks.version import VersionIncrementCheck
from connectors_qa.models import CheckStatus


@pytest.fixture
def connector():
    connector = MagicMock(spec=Connector)
    connector.technical_name = "source-test"
    connector.metadata = {"dockerImageTag": "1.0.0"}
    connector.is_released = False
    return connector


@pytest.fixture
def version_increment_check():
    return VersionIncrementCheck()


class TestVersionIncrementCheck:
    def test_is_version_not_incremented(self, version_increment_check):
        assert version_increment_check._is_version_not_incremented(semver.Version.parse("1.0.0"), semver.Version.parse("0.9.0"))

        assert version_increment_check._is_version_not_incremented(semver.Version.parse("1.0.0"), semver.Version.parse("1.0.0"))

        assert not version_increment_check._is_version_not_incremented(semver.Version.parse("0.9.0"), semver.Version.parse("1.0.0"))

    def test_are_both_versions_release_candidates(self, version_increment_check):
        assert version_increment_check._are_both_versions_release_candidates(
            semver.Version.parse("1.0.0-rc.1"), semver.Version.parse("1.0.0-rc.2")
        )

        assert not version_increment_check._are_both_versions_release_candidates(
            semver.Version.parse("1.0.0-rc.1"), semver.Version.parse("1.0.0")
        )

        assert not version_increment_check._are_both_versions_release_candidates(
            semver.Version.parse("1.0.0"), semver.Version.parse("1.0.0-rc.1")
        )

        assert not version_increment_check._are_both_versions_release_candidates(
            semver.Version.parse("1.0.0"), semver.Version.parse("1.1.0")
        )

    def test_have_same_major_minor_patch(self, version_increment_check):
        assert version_increment_check._have_same_major_minor_patch(semver.Version.parse("1.0.0"), semver.Version.parse("1.0.0"))

        assert not version_increment_check._have_same_major_minor_patch(semver.Version.parse("1.0.0"), semver.Version.parse("2.0.0"))

        assert not version_increment_check._have_same_major_minor_patch(semver.Version.parse("1.0.0"), semver.Version.parse("1.1.0"))

        assert not version_increment_check._have_same_major_minor_patch(semver.Version.parse("1.0.0"), semver.Version.parse("1.0.1"))

        assert version_increment_check._have_same_major_minor_patch(semver.Version.parse("1.0.0-rc.1"), semver.Version.parse("1.0.0-rc.2"))

    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_master_connector_version")
    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_current_connector_version")
    def test_run_version_not_incremented(self, mock_current_version, mock_master_version, version_increment_check, connector):
        mock_master_version.return_value = semver.Version.parse("1.0.0")
        mock_current_version.return_value = semver.Version.parse("0.9.0")

        result = version_increment_check._run(connector)

        assert result.status == CheckStatus.FAILED
        assert "was not incremented" in result.message

    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_master_connector_version")
    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_current_connector_version")
    def test_run_version_incremented(self, mock_current_version, mock_master_version, version_increment_check, connector):
        mock_master_version.return_value = semver.Version.parse("0.9.0")
        mock_current_version.return_value = semver.Version.parse("1.0.0")

        result = version_increment_check._run(connector)

        assert result.status == CheckStatus.PASSED
        assert "Version was properly incremented" in result.message

    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_master_connector_version")
    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_current_connector_version")
    def test_run_release_candidates_different_versions(self, mock_current_version, mock_master_version, version_increment_check, connector):
        mock_master_version.return_value = semver.Version.parse("1.0.0-rc.1")
        mock_current_version.return_value = semver.Version.parse("1.1.0-rc.1")

        result = version_increment_check._run(connector)

        assert result.status == CheckStatus.FAILED
        assert "Release candidates should only differ in the prerelease part" in result.message

    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_master_connector_version")
    @patch("connectors_qa.checks.version.VersionIncrementCheck._get_current_connector_version")
    def test_run_release_candidates_same_versions(self, mock_current_version, mock_master_version, version_increment_check, connector):
        mock_master_version.return_value = semver.Version.parse("1.0.0-rc.1")
        mock_current_version.return_value = semver.Version.parse("1.0.0-rc.2")

        result = version_increment_check._run(connector)

        assert result.status == CheckStatus.PASSED
        assert "Version was properly incremented" in result.message

    @patch("connectors_qa.checks.version.VersionIncrementCheck._should_run")
    def test_run_should_not_run(self, mock_should_run, version_increment_check, connector):
        mock_should_run.return_value = False

        result = version_increment_check._run(connector)

        assert result.status == CheckStatus.SKIPPED
        assert "No modified files required a version bump" in result.message
