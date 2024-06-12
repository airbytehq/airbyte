# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from connectors_qa import consts
from connectors_qa.checks import packaging
from connectors_qa.models import CheckStatus


class TestCheckConnectorUsesPoetry:
    def test_fail_when_pyproject_toml_file_does_not_exist(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)

        # Act
        result = packaging.CheckConnectorUsesPoetry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == f"{consts.PYPROJECT_FILE_NAME} file is missing"

    def test_fail_when_poetry_lock_file_does_not_exist(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).touch()

        # Act
        result = packaging.CheckConnectorUsesPoetry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == f"{consts.POETRY_LOCK_FILE_NAME} file is missing"

    def test_fail_when_setup_py_file_exists(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).touch()
        (tmp_path / consts.POETRY_LOCK_FILE_NAME).touch()
        (tmp_path / consts.SETUP_PY_FILE_NAME).touch()

        # Act
        result = packaging.CheckConnectorUsesPoetry()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == f"{consts.SETUP_PY_FILE_NAME} file exists. Please remove it and use {consts.PYPROJECT_FILE_NAME} instead"

    def test_pass_when_poetry_is_used(self, tmp_path, mocker):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).touch()
        (tmp_path / consts.POETRY_LOCK_FILE_NAME).touch()

        # Act
        result = packaging.CheckConnectorUsesPoetry()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Poetry is used for dependency management"


class TestCheckPublishToPyPiIsEnabled:
    def test_fail_if_publish_to_pypi_is_not_enabled(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"remoteRegistries": {"pypi": {"enabled": False}}})

        # Act
        result = packaging.CheckPublishToPyPiIsEnabled()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "PyPi publishing is not enabled" in result.message

    def test_pass_if_publish_to_pypi_is_enabled(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"remoteRegistries": {"pypi": {"enabled": True}}})

        # Act
        result = packaging.CheckPublishToPyPiIsEnabled()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert "PyPi publishing is enabled" in result.message


class TestCheckConnectorLicense:
    def test_fail_when_license_is_missing(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={})

        # Act
        result = packaging.CheckConnectorLicense()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "License is missing in the metadata file" in result.message

    def test_fail_when_license_is_not_valid(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"license": "MITO"})

        # Act
        result = packaging.CheckConnectorLicense()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Connector is not using a valid license" in result.message


class TestCheckConnectorLicenseMatchInPyproject:
    def test_fail_when_missing_metadata_license(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={})

        # Act
        result = packaging.CheckConnectorLicenseMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"License is missing in the {consts.METADATA_FILE_NAME} file" in result.message

    def test_fail_when_missing_pyproject_toml_file(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"license": "MIT"}, code_directory=tmp_path)

        # Act
        result = packaging.CheckConnectorLicenseMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"{consts.PYPROJECT_FILE_NAME} file is missing" in result.message

    def test_fail_when_unparseable_toml_file(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"license": "MIT"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text("abc")

        # Act
        result = packaging.CheckConnectorLicenseMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"{consts.PYPROJECT_FILE_NAME} is invalid toml file" in result.message

    def test_fail_when_missing_poetry_license(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"license": "MIT"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text("[tool.poetry]")

        # Act
        result = packaging.CheckConnectorLicenseMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Connector is missing license in {consts.PYPROJECT_FILE_NAME}. Please add it" in result.message

    def test_fail_when_license_mismatch(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"license": "MIT"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text('[tool.poetry]\nlicense = "Elv2"')

        # Act
        result = packaging.CheckConnectorLicenseMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert (
            f"Connector is licensed under Elv2 in {consts.PYPROJECT_FILE_NAME}, but licensed under MIT in {consts.METADATA_FILE_NAME}. These two files have to be consistent"
            in result.message
        )

    def test_pass_when_license_match(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"license": "ELV2"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text('[tool.poetry]\nlicense = "Elv2"')

        # Act
        result = packaging.CheckConnectorLicenseMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert f"License in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file match" in result.message


class TestCheckConnectorVersionMatchInPyproject:
    def test_fail_when_missing_metadata_docker_image_tag(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={})

        # Act
        result = packaging.CheckConnectorVersionMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"dockerImageTag is missing in {consts.METADATA_FILE_NAME}"

    def test_fail_when_missing_pyproject_toml_file(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "0.0.0"}, code_directory=tmp_path)

        # Act
        result = packaging.CheckConnectorVersionMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"{consts.PYPROJECT_FILE_NAME} file is missing" in result.message

    def test_fail_when_unparseable_toml_file(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "0.0.0"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text("abc")

        # Act
        result = packaging.CheckConnectorVersionMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"{consts.PYPROJECT_FILE_NAME} is invalid toml file" in result.message

    def test_fail_when_missing_poetry_version(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "0.0.0"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text("[tool.poetry]")

        # Act
        result = packaging.CheckConnectorVersionMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Version field is missing in the {consts.PYPROJECT_FILE_NAME} file" in result.message

    def test_fail_when_version_mismatch(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "0.0.0"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text('[tool.poetry]\nversion = "1.0.0"')

        # Act
        result = packaging.CheckConnectorVersionMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert (
            f"Version is 0.0.0 in {consts.METADATA_FILE_NAME}, but version is 1.0.0 in {consts.PYPROJECT_FILE_NAME}. These two files have to be consistent"
            in result.message
        )

    def test_pass_when_version_match(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "1.0.0"}, code_directory=tmp_path)
        (tmp_path / consts.PYPROJECT_FILE_NAME).write_text('[tool.poetry]\nversion = "1.0.0"')

        # Act
        result = packaging.CheckConnectorVersionMatchInPyproject()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert f"Version in {consts.METADATA_FILE_NAME} and {consts.PYPROJECT_FILE_NAME} file match" in result.message


class TestCheckVersionFollowsSemver:
    def test_fail_when_missing_metadata_docker_image_tag(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={})

        # Act
        result = packaging.CheckVersionFollowsSemver()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"dockerImageTag is missing in {consts.METADATA_FILE_NAME}"

    def test_fail_when_version_is_not_semver(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "1.1"})

        # Act
        result = packaging.CheckVersionFollowsSemver()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert f"Connector version {connector.metadata['dockerImageTag']} does not follow semantic versioning" in result.message

    def test_pass_when_version_follows_semver(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"dockerImageTag": "1.1.1"})

        # Act
        result = packaging.CheckVersionFollowsSemver()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert "Connector version follows semantic versioning" in result.message
