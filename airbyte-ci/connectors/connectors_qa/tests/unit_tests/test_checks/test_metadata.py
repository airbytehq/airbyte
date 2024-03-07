# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import os

import pytest
from connectors_qa import consts
from connectors_qa.checks import metadata
from connectors_qa.models import CheckStatus


class TestValidateMetadata:
    def test_fail_init_when_required_env_vars_are_not_set(self, random_string, mocker):
        # Arrange
        mocker.patch.object(metadata.ValidateMetadata, "required_env_vars", new={random_string})

        # Act
        with pytest.raises(ValueError):
            metadata.ValidateMetadata()

    def test_init_when_required_env_vars_are_set(self, random_string, mocker):
        # Arrange
        os.environ[random_string] = "test"
        mocker.patch.object(metadata.ValidateMetadata, "required_env_vars", new={random_string})

        # Act
        metadata.ValidateMetadata()

        os.environ.pop(random_string)

    def test_fail_when_documentation_file_path_is_none(self, mocker):
        # Arrange
        connector = mocker.MagicMock(documentation_file_path=None)

        # Act
        result = metadata.ValidateMetadata()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "User facing documentation file is missing. Please create it"

    def test_fail_when_documentation_file_path_does_not_exist(self, mocker, tmp_path):
        # Arrange

        connector = mocker.MagicMock(documentation_file_path=tmp_path / "doc.md")

        # Act
        result = metadata.ValidateMetadata()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "User facing documentation file is missing. Please create it"

    def test_fail_when_deserialization_fails(self, mocker, tmp_path):
        # Arrange
        mocker.patch.object(metadata, "validate_and_load", return_value=(None, "error"))
        documentation_file_path = tmp_path / "doc.md"
        documentation_file_path.touch()
        connector = mocker.MagicMock(documentation_file_path=documentation_file_path)

        # Act
        result = metadata.ValidateMetadata()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Metadata file is invalid: error"

    def test_pass_when_metadata_file_is_valid(self, mocker, tmp_path):
        # Arrange
        mocker.patch.object(metadata, "validate_and_load", return_value=(mocker.Mock(), None))
        documentation_file_path = tmp_path / "doc.md"
        documentation_file_path.touch()
        connector = mocker.MagicMock(documentation_file_path=documentation_file_path)

        # Act
        result = metadata.ValidateMetadata()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Metadata file valid."


class TestCheckConnectorLanguageTag:
    def test_fail_when_no_language_tags(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": []})

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Language tag is missing in the metadata file"

    def test_fail_when_multiple_language_tags(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["language:python", "language:java"]})

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Multiple language tags found in the metadata file: ['language:python', 'language:java']"

    def test_fail_when_java_tag_on_python_connector(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["language:java"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / consts.PYPROJECT_FILE_NAME).touch()

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Expected language tag 'language:python'" in result.message
        assert "but found 'language:java'" in result.message

    def test_fail_when_python_tag_on_java_connector(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["language:python"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / consts.GRADLE_FILE_NAME).touch()

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Expected language tag 'language:java'" in result.message
        assert "but found 'language:python'" in result.message

    def test_pass_when_python(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["language:python"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / consts.PYPROJECT_FILE_NAME).touch()

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Language tag language:python is present in the metadata file"

    def test_pass_when_java(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["language:java"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / consts.GRADLE_FILE_NAME).touch()

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Language tag language:java is present in the metadata file"
