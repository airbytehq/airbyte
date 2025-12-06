# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
import semver

from connectors_qa import consts
from connectors_qa.checks.version import CheckVersionIncrement
from connectors_qa.models import CheckStatus


class TestVersionIncrementCheck:
    @pytest.fixture
    def mock_connector(self, mocker, tmp_path):
        connector = mocker.Mock(code_directory=str(tmp_path), technical_name="mock-connector")
        # Set up default metadata without registryOverrides
        connector.metadata = {"dockerImageTag": "1.0.0"}
        return connector

    def _get_version_increment_check(
        self, mocker, master_version="1.0.0", current_version="1.0.1", master_metadata=None, current_metadata=None
    ):
        # Default master metadata if not provided
        if master_metadata is None:
            master_metadata = {"dockerImageTag": master_version}
        mocker.patch(
            "connectors_qa.checks.version.CheckVersionIncrement._get_master_metadata",
            return_value=master_metadata,
        )
        mocker.patch(
            "connectors_qa.checks.version.CheckVersionIncrement._get_current_connector_version",
            return_value=semver.Version.parse(current_version),
        )

        return CheckVersionIncrement()

    def test_validate_success(self, mocker, mock_connector):
        mock_connector.metadata = {"dockerImageTag": "1.0.1"}
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.0", current_version="1.0.1")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.PASSED

    def test_validate_failure_no_increment(self, mock_connector, mocker):
        mock_connector.metadata = {"dockerImageTag": "1.0.0"}
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.0", current_version="1.0.0")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.FAILED
        assert (
            result.message
            == f"The dockerImageTag in {consts.METADATA_FILE_NAME} was not incremented. Master version is 1.0.0, current version is 1.0.0. Ignore this message if you do not intend to re-release the connector."
        )

    def test_validate_failure_decrement(self, mock_connector, mocker):
        mock_connector.metadata = {"dockerImageTag": "1.0.0"}
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.1.0", current_version="1.0.0")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.FAILED
        assert (
            result.message
            == f"The dockerImageTag in {consts.METADATA_FILE_NAME} appears to be lower than the version on the default branch. Master version is 1.1.0, current version is 1.0.0. Update your PR branch from the default branch to get the latest connector version."
        )

    def test_validate_success_rc_increment(self, mock_connector, mocker):
        mock_connector.metadata = {"dockerImageTag": "1.0.1-rc.2"}
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.1-rc.1", current_version="1.0.1-rc.2")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.PASSED

    def test_validate_failure_rc_with_different_versions(self, mock_connector, mocker):
        mock_connector.metadata = {"dockerImageTag": "1.0.1-rc.1"}
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.0-rc.1", current_version="1.0.1-rc.1")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.FAILED
        assert (
            result.message
            == f"Master and current version are release candidates but they have different major, minor or patch versions. Release candidates should only differ in the prerelease part. Master version is 1.0.0-rc.1, current version is 1.0.1-rc.1"
        )

    def test_validate_skipped_registry_override_cloud_added(self, mock_connector, mocker):
        """Test that validation is skipped when registryOverrides.cloud.dockerImageTag is added."""
        master_metadata = {"dockerImageTag": "1.0.0"}
        mock_connector.metadata = {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.0-cloud"}}}
        version_increment_check = self._get_version_increment_check(
            mocker, master_version="1.0.0", current_version="1.0.0", master_metadata=master_metadata
        )
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.SKIPPED

    def test_validate_skipped_registry_override_oss_changed(self, mock_connector, mocker):
        """Test that validation is skipped when registryOverrides.oss.dockerImageTag is changed."""
        master_metadata = {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.0-oss"}}}
        mock_connector.metadata = {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.1-oss"}}}
        version_increment_check = self._get_version_increment_check(
            mocker, master_version="1.0.0", current_version="1.0.0", master_metadata=master_metadata
        )
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.SKIPPED

    def test_validate_failure_no_increment_registry_override_unchanged(self, mock_connector, mocker):
        """Test that validation fails when version is not incremented and registryOverrides are unchanged."""
        master_metadata = {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.0-cloud"}}}
        mock_connector.metadata = {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.0-cloud"}}}
        version_increment_check = self._get_version_increment_check(
            mocker, master_version="1.0.0", current_version="1.0.0", master_metadata=master_metadata
        )
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.FAILED
