# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from connectors_qa import consts
from connectors_qa.checks import security
from connectors_qa.models import CheckStatus


class TestCheckConnectorUsesHTTPSOnly:
    def test_fail_when_http_url_is_found(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        file_with_http_url = tmp_path / "file.py"
        file_with_http_url.write_text("http://example.com")

        # Act
        result = security.CheckConnectorUsesHTTPSOnly()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == f"The following files have http:// URLs:\n\t- {file_with_http_url}"

    def test_pass_when_commented_http_url(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        file_with_http_url = tmp_path / "file.py"
        file_with_http_url.write_text(f"http://example.com {security.CheckConnectorUsesHTTPSOnly.ignore_comment}")

        # Act
        result = security.CheckConnectorUsesHTTPSOnly()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "No file with http:// URLs found"

    def test_pass_when_http_url_in_ignored_directories(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        for ignored_directory in security.CheckConnectorUsesHTTPSOnly.ignored_directories_for_https_checks:
            (tmp_path / ignored_directory).mkdir()
            file_with_http_url = tmp_path / ignored_directory / "file.py"
            file_with_http_url.write_text("http://example.com")

        # Act
        result = security.CheckConnectorUsesHTTPSOnly()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "No file with http:// URLs found"

    def test_pass_when_http_url_in_ignored_patterns(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        for ignored_pattern in security.CheckConnectorUsesHTTPSOnly.ignored_file_name_pattern_for_https_checks:
            file_with_http_url = tmp_path / ignored_pattern.replace("*", "test")
            file_with_http_url.write_text("http://example.com")

        # Act
        result = security.CheckConnectorUsesHTTPSOnly()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "No file with http:// URLs found"

    def test_pass_when_http_url_has_ignored_prefix(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        file_with_http_url = tmp_path / "file.py"
        for i, ignored_prefix in enumerate(security.CheckConnectorUsesHTTPSOnly.ignored_url_prefixes):
            file_with_http_url = tmp_path / f"file_{i}.py"
            file_with_http_url.write_text(ignored_prefix)

        # Act
        result = security.CheckConnectorUsesHTTPSOnly()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "No file with http:// URLs found"

    def test_pass_when_https_url(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        file_with_http_url = tmp_path / "file.py"
        file_with_http_url.write_text(f"https://example.com")

        # Act
        result = security.CheckConnectorUsesHTTPSOnly()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "No file with http:// URLs found"


class TestCheckConnectorUsesPythonBaseImage:
    def test_fail_when_dockerfile_exists(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path)
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.touch()

        # Act
        result = security.CheckConnectorUsesPythonBaseImage()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert (
            result.message
            == f"{consts.DOCKERFILE_NAME} file exists. Please remove it and declare the base image in {consts.METADATA_FILE_NAME} file with the `connectorBuildOptions.baseImage` key"
        )

    def test_fail_when_base_image_is_missing(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path, metadata={})

        # Act
        result = security.CheckConnectorUsesPythonBaseImage()._run(connector)

        # Assert
        assert result.status == CheckStatus.FAILED
        assert result.message == f"connectorBuildOptions.baseImage key is missing in {consts.METADATA_FILE_NAME} file"

    def test_pass_when_no_dockerfile_and_base_image(self, mocker, tmp_path):
        # Arrange
        connector = mocker.MagicMock(code_directory=tmp_path, metadata={"connectorBuildOptions": {"baseImage": "test"}})

        # Act
        result = security.CheckConnectorUsesPythonBaseImage()._run(connector)

        # Assert
        assert result.status == CheckStatus.PASSED
        assert result.message == "Connector uses the Python connector base image"
