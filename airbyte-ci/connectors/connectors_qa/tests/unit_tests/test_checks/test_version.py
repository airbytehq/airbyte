# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
import semver
from connector_ops.utils import METADATA_FILE_NAME

from connectors_qa.checks.version import CheckVersionIncrement


class TestVersionIncrementCheck:
    @pytest.fixture
    def mock_connector(self, mocker, tmp_path):
        connector = mocker.Mock(code_directory=str(tmp_path), technical_name="mock-connector")
        return connector

    def _get_version_increment_check(self, mocker, connector, master_version="1.0.0", current_version="1.0.1"):
        mocker.patch(
            "pipelines.airbyte_ci.connectors.test.steps.common.VersionIncrementCheck.master_connector_version",
            new_callable=mocker.PropertyMock,
            return_value=semver.Version.parse(master_version),
        )
        mocker.patch(
            "pipelines.airbyte_ci.connectors.test.steps.common.VersionIncrementCheck.current_connector_version",
            new_callable=mocker.PropertyMock,
            return_value=semver.Version.parse(current_version),
        )

        return CheckVersionIncrement(connector)

    def test_should_run(self, connector):
        connector.modified_files = ["some_file"]
        assert CheckVersionIncrement(connector).should_run

    def test_should_not_run(self, context):
        for bypassed_file in CheckVersionIncrement.BYPASS_CHECK_FOR:
            context.modified_files = [bypassed_file]
            assert not CheckVersionIncrement(context).should_run

    def test_validate_success_no_rc_increment(self, mocker, context):
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.1")
        result = version_increment_check.validate()
        assert result.success

    def test_validate_failure_no_increment(self, context, mocker):
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        result = version_increment_check.validate()
        assert not result.success
        assert (
            result.stderr
            == f"The dockerImageTag in {METADATA_FILE_NAME} was not incremented. Master version is {version_increment_check.master_connector_version}, current version is {version_increment_check.current_connector_version}"
        )

    def test_validate_failure_rc_with_different_versions(self, context, mocker):
        version_increment_check = self._get_version_increment_check(
            mocker, context, master_version="1.0.0-rc.1", current_version="1.0.1-rc.1"
        )
        result = version_increment_check.validate()
        assert not result.success
        assert (
            result.stderr
            == f"Master and current version are release candidates but they have different major, minor or patch versions. Release candidates should only differ in the prerelease part. Master version is {version_increment_check.master_connector_version}, current version is {version_increment_check.current_connector_version}"
        )

    def test_validate_success_rc_increment(self, context, mocker):
        version_increment_check = self._get_version_increment_check(
            mocker, context, master_version="1.0.1-rc.1", current_version="1.0.1-rc.2"
        )
        result = version_increment_check.validate()
        assert result.success
