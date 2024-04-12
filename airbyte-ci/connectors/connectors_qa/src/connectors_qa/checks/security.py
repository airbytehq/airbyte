# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from pathlib import Path
from typing import Iterable, Optional, Set, Tuple

from connector_ops.utils import Connector, ConnectorLanguage  # type: ignore
from connectors_qa import consts
from connectors_qa.models import Check, CheckCategory, CheckResult
from pydash.objects import get  # type: ignore


class SecurityCheck(Check):
    category = CheckCategory.SECURITY


class CheckConnectorUsesHTTPSOnly(SecurityCheck):
    name = "Connectors must use HTTPS only"
    description = "Connectors must use HTTPS only when making requests to external services."
    requires_metadata = False
    runs_on_released_connectors = False

    ignore_comment = "# ignore-https-check"  # Define the ignore comment pattern

    ignored_directories_for_https_checks = {
        ".venv",
        "tests",
        "unit_tests",
        "integration_tests",
        "build",
        "source-file",
        ".pytest_cache",
        "acceptance_tests_logs",
        ".hypothesis",
        ".ruff_cache",
        "htmlcov",
    }

    ignored_file_name_pattern_for_https_checks = {
        "*Test.java",
        "*.jar",
        "*.pyc",
        "*.gz",
        "*.svg",
        "expected_records.jsonl",
        "expected_records.json",
    }

    ignored_url_prefixes = {
        "http://json-schema.org",
        "http://localhost",
    }

    @staticmethod
    def _read_all_files_in_directory(
        directory: Path,
        ignored_directories: Optional[Set[str]] = None,
        ignored_filename_patterns: Optional[Set[str]] = None,
    ) -> Iterable[Tuple[Path, str]]:
        ignored_directories = ignored_directories if ignored_directories is not None else set()
        ignored_filename_patterns = ignored_filename_patterns if ignored_filename_patterns is not None else set()

        for path in directory.rglob("*"):
            ignore_directory = any([ignored_directory in path.parts for ignored_directory in ignored_directories])
            ignore_filename = any([path.match(ignored_filename_pattern) for ignored_filename_pattern in ignored_filename_patterns])
            ignore = ignore_directory or ignore_filename
            if path.is_file() and not ignore:
                try:
                    for line in open(path, "r"):
                        yield path, line
                except UnicodeDecodeError:
                    continue

    @staticmethod
    def _line_is_comment(line: str, file_path: Path) -> bool:
        language_comments = {
            ".py": "#",
            ".yml": "#",
            ".yaml": "#",
            ".java": "//",
            ".md": "<!--",
        }

        denote_comment = language_comments.get(file_path.suffix)
        if not denote_comment:
            return False

        trimmed_line = line.lstrip()
        return trimmed_line.startswith(denote_comment)

    def _run(self, connector: Connector) -> CheckResult:
        files_with_http_url = set()

        for filename, line in self._read_all_files_in_directory(
            connector.code_directory,
            self.ignored_directories_for_https_checks,
            self.ignored_file_name_pattern_for_https_checks,
        ):
            line = line.lower()
            if self._line_is_comment(line, filename):
                continue
            if self.ignore_comment in line:
                continue
            for prefix in self.ignored_url_prefixes:
                line = line.replace(prefix, "")
            if "http://" in line:
                files_with_http_url.add(str(filename))

        if files_with_http_url:
            files_with_http_url_message = "\n\t- ".join(files_with_http_url)
            return self.fail(
                connector=connector,
                message=f"The following files have http:// URLs:\n\t- {files_with_http_url_message}",
            )
        return self.pass_(connector=connector, message="No file with http:// URLs found")


class CheckConnectorUsesPythonBaseImage(SecurityCheck):
    name = (
        f"Python connectors must not use a {consts.DOCKERFILE_NAME} and must declare their base image in {consts.METADATA_FILE_NAME} file"
    )
    description = f"Connectors must use our Python connector base image (`{consts.AIRBYTE_PYTHON_CONNECTOR_BASE_IMAGE_NAME}`), declared through the `connectorBuildOptions.baseImage` in their `{consts.METADATA_FILE_NAME}`.\nThis is to ensure that all connectors use a base image which is maintained and has security updates."
    applies_to_connector_languages = [
        ConnectorLanguage.PYTHON,
        ConnectorLanguage.LOW_CODE,
    ]

    def _run(self, connector: Connector) -> CheckResult:
        dockerfile_path = connector.code_directory / consts.DOCKERFILE_NAME
        if dockerfile_path.exists():
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"{consts.DOCKERFILE_NAME} file exists. Please remove it and declare the base image in {consts.METADATA_FILE_NAME} file with the `connectorBuildOptions.baseImage` key",
            )

        if not get(connector.metadata, "connectorBuildOptions.baseImage"):
            return self.create_check_result(
                connector=connector,
                passed=False,
                message=f"connectorBuildOptions.baseImage key is missing in {consts.METADATA_FILE_NAME} file",
            )
        return self.create_check_result(
            connector=connector,
            passed=True,
            message="Connector uses the Python connector base image",
        )


ENABLED_CHECKS = [CheckConnectorUsesHTTPSOnly(), CheckConnectorUsesPythonBaseImage()]
