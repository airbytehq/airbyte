# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import pytest
from connector_ops.utils import METADATA_FILE_NAME
from semver import VersionInfo

from pipelines.airbyte_ci.connectors.test.steps.common import VersionIncrementCheck
from pipelines.models.steps import StepStatus


class TestVersionIncrementCheck:
    @pytest.fixture
    def context(self, mocker, tmp_path):
        context = mocker.Mock()
        context.connector = mocker.Mock(code_directory=str(tmp_path), technical_name="test-connector")
        context.modified_files = ["/path/to/connector/src/main.py", "/path/to/connector/README.md"]
        context.secrets_to_mask = []
        return context

    def _get_version_increment_check(self, mocker, context, master_version="1.0.0", current_version="1.0.1"):
        mocker.patch(
            "pipelines.airbyte_ci.connectors.test.steps.common.VersionIncrementCheck.master_connector_version",
            new_callable=mocker.PropertyMock,
            return_value=VersionInfo.parse(master_version),
        )
        mocker.patch(
            "pipelines.airbyte_ci.connectors.test.steps.common.VersionIncrementCheck.current_connector_version",
            new_callable=mocker.PropertyMock,
            return_value=VersionInfo.parse(current_version),
        )

        return VersionIncrementCheck(context)

    def test_should_run(self, context):
        context.modified_files = ["some_file"]
        assert VersionIncrementCheck(context).should_run

    def test_should_not_run(self, context):
        for bypassed_file in VersionIncrementCheck.BYPASS_CHECK_FOR:
            context.modified_files = [bypassed_file]
            assert not VersionIncrementCheck(context).should_run

    def test_validate_success_no_rc_increment(self, mocker, context):
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.1")
        result = version_increment_check.validate()
        assert result.success

    def test_validate_failure_no_increment(self, context, mocker):
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        # Set up metadata to ensure registryOverrides check doesn't bypass the failure
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0"}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0"}}
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

    def test_validate_skipped_registry_override_oss_added(self, context, mocker):
        """Test that version increment check is skipped when registryOverrides.oss.dockerImageTag is added."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0"}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.0-oss"}}}}
        result = version_increment_check.validate()
        assert result.status == StepStatus.SKIPPED

    def test_validate_skipped_registry_override_oss_removed(self, context, mocker):
        """Test that version increment check is skipped when registryOverrides.oss.dockerImageTag is removed."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.0-oss"}}}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0"}}
        result = version_increment_check.validate()
        assert result.status == StepStatus.SKIPPED

    def test_validate_skipped_registry_override_oss_changed(self, context, mocker):
        """Test that version increment check is skipped when registryOverrides.oss.dockerImageTag is changed."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.0-oss"}}}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.1-oss"}}}}
        result = version_increment_check.validate()
        assert result.status == StepStatus.SKIPPED

    def test_validate_skipped_registry_override_cloud_added(self, context, mocker):
        """Test that version increment check is skipped when registryOverrides.cloud.dockerImageTag is added."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0"}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.0-cloud"}}}}
        result = version_increment_check.validate()
        assert result.status == StepStatus.SKIPPED

    def test_validate_skipped_registry_override_cloud_removed(self, context, mocker):
        """Test that version increment check is skipped when registryOverrides.cloud.dockerImageTag is removed."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.0-cloud"}}}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0"}}
        result = version_increment_check.validate()
        assert result.status == StepStatus.SKIPPED

    def test_validate_skipped_registry_override_cloud_changed(self, context, mocker):
        """Test that version increment check is skipped when registryOverrides.cloud.dockerImageTag is changed."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.0-cloud"}}}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"cloud": {"dockerImageTag": "1.0.1-cloud"}}}}
        result = version_increment_check.validate()
        assert result.status == StepStatus.SKIPPED

    def test_validate_failure_no_increment_registry_override_unchanged(self, context, mocker):
        """Test that version increment check fails when dockerImageTag is not incremented and registryOverrides are unchanged."""
        version_increment_check = self._get_version_increment_check(mocker, context, master_version="1.0.0", current_version="1.0.0")
        mocker.patch.object(
            version_increment_check,
            "master_metadata",
            {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.0-oss"}}}},
        )
        context.metadata = {"data": {"dockerImageTag": "1.0.0", "registryOverrides": {"oss": {"dockerImageTag": "1.0.0-oss"}}}}
        result = version_increment_check.validate()
        assert not result.success
