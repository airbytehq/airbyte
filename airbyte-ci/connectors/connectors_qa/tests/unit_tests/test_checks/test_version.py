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
        return connector

    def _get_version_increment_check(self, mocker, master_version="1.0.0", current_version="1.0.1"):
        mocker.patch(
            "connectors_qa.checks.version.CheckVersionIncrement._get_master_connector_version",
            return_value=semver.Version.parse(master_version),
        )
        mocker.patch(
            "connectors_qa.checks.version.CheckVersionIncrement._get_current_connector_version",
            return_value=semver.Version.parse(current_version),
        )

        return CheckVersionIncrement()

    def test_validate_success(self, mocker, mock_connector):
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.0", current_version="1.0.1")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.PASSED

    def test_validate_failure_no_increment(self, mock_connector, mocker):
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.0", current_version="1.0.0")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.FAILED
        assert (
            result.message
            == f"The dockerImageTag in {consts.METADATA_FILE_NAME} was not incremented. Master version is 1.0.0, current version is 1.0.0"
        )

    def test_validate_success_rc_increment(self, mock_connector, mocker):
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.1-rc.1", current_version="1.0.1-rc.2")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.PASSED

    def test_validate_failure_rc_with_different_versions(self, mock_connector, mocker):
        version_increment_check = self._get_version_increment_check(mocker, master_version="1.0.0-rc.1", current_version="1.0.1-rc.1")
        result = version_increment_check._run(mock_connector)
        assert result.status == CheckStatus.FAILED
        assert (
            result.message
            == f"Master and current version are release candidates but they have different major, minor or patch versions. Release candidates should only differ in the prerelease part. Master version is 1.0.0-rc.1, current version is 1.0.1-rc.1"
        )
