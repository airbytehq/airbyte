# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import os

import pytest
from connectors_qa import consts
from connectors_qa.checks import metadata
from connectors_qa.models import CheckStatus


class TestValidateMetadata:
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

    def test_checks_apply_to_manifest_only_connectors(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["language:manifest-only"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / consts.MANIFEST_FILE_NAME).touch()

        # Act
        result = metadata.CheckConnectorLanguageTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Language tag language:manifest-only is present in the metadata file"


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


class TestCheckConnectorCDKTag:
    def test_fail_when_no_cdk_tags(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": []})

        # Act
        result = metadata.CheckConnectorCDKTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "CDK tag is missing in the metadata file"

    def test_fail_when_multiple_cdk_tags(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["cdk:low-code", "cdk:python"]})

        # Act
        result = metadata.CheckConnectorCDKTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Multiple CDK tags found in the metadata file: ['cdk:low-code', 'cdk:python']"

    def test_fail_when_low_code_tag_on_python_connector(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(metadata={"tags": ["cdk:low-code"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / consts.PYPROJECT_FILE_NAME).write_text("[tool.poetry.dependencies]\nairbyte-cdk = '^1.0.0'")

        # Act
        result = metadata.CheckConnectorCDKTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Expected CDK tag 'cdk:python'" in result.message
        assert "but found 'cdk:low-code'" in result.message

    def test_fail_when_python_tag_on_low_code_connector(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(technical_name="source-test", metadata={"tags": ["cdk:python"]}, code_directory=tmp_path)
        code_directory = tmp_path
        (code_directory / "source_test").mkdir()
        (code_directory / "source_test" / consts.LOW_CODE_MANIFEST_FILE_NAME).touch()

        # Act
        result = metadata.CheckConnectorCDKTag()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert "Expected CDK tag 'cdk:low-code'" in result.message
        assert "but found 'cdk:python'" in result.message


class TestCheckConnectorMaxSecondsBetweenMessagesValue:
    def test_fail_when_field_missing(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"supportLevel": "certified"})

        # Act
        result = metadata.CheckConnectorMaxSecondsBetweenMessagesValue()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == "Missing required for certified connectors field 'maxSecondsBetweenMessages'"

    def test_pass_when_field_present(self, mocker):
        # Arrange
        connector = mocker.MagicMock(metadata={"supportLevel": "certified", "maxSecondsBetweenMessages": 1})

        # Act
        result = metadata.CheckConnectorMaxSecondsBetweenMessagesValue()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Value for maxSecondsBetweenMessages is set"
