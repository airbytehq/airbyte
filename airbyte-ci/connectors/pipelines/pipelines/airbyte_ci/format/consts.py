#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from enum import Enum

REPO_MOUNT_PATH = "/src"
CACHE_MOUNT_PATH = "/cache"

LICENSE_FILE_NAME = "LICENSE_SHORT"

# TODO create .airbyte_ci_ignore files?
DEFAULT_FORMAT_IGNORE_LIST = [
    "**/__init__.py",  # These files has never been formatted and we don't want to start now (for now) see https://github.com/airbytehq/airbyte/issues/33296
    "**/__pycache__",
    "**/.eggs",
    "**/.git",
    "**/.gradle",
    "**/.mypy_cache",
    "**/.pytest_cache",
    "**/.tox",
    "**/.venv",
    "**/*.egg-info",
    "**/build",
    "**/charts",  # Helm charts often have injected template strings that will fail general linting. Helm linting is done separately.
    "**/dbt_test_config",
    "**/dbt-project-template-clickhouse",
    "**/dbt-project-template-duckdb",
    "**/dbt-project-template-mssql",
    "**/dbt-project-template-mysql",
    "**/dbt-project-template-oracle",
    "**/dbt-project-template-snowflake",
    "**/dbt-project-template-tidb",
    "**/dbt-project-template",
    "**/node_modules",
    "**/pnpm-lock.yaml",  # This file is generated and should not be formatted
    "**/normalization_test_output",
    "**/source-amplitude/unit_tests/api_data/zipped.json",  # Zipped file presents as non-UTF-8 making spotless sad
    "airbyte-cdk/python/airbyte_cdk/sources/declarative/models/**",  # These files are generated and should not be formatted
    "airbyte-ci/connectors/metadata_service/lib/metadata_service/models/generated/**",  # These files are generated and should not be formatted
    "**/airbyte-ci/connectors/metadata_service/lib/tests/fixtures/**/invalid",  # This is a test directory with invalid and sometimes unformatted code
    "airbyte-ci/connectors/pipelines/tests/test_format/non_formatted_code",  # This is a test directory with badly formatted code
]


class Formatter(Enum):
    """An enum for the formatter values which can be ["java", "js", "python", "license"]."""

    JAVA = "java"
    JS = "js"
    PYTHON = "python"
    LICENSE = "license"


# This files are dependencies to be mounted in formatter containers.
# They are used as configuration files for the formatter.
# We mount them to formatter containers because they can be required to install dependencies.
# We use them to  "warmup" containers because they are not likely to change often.
# The mount will be cached and we won't re-install dependencies unless these files change.
WARM_UP_INCLUSIONS = {
    Formatter.JAVA: [
        "spotless-maven-pom.xml",
        "tools/gradle/codestyle/java-google-style.xml",
    ],
    Formatter.PYTHON: ["pyproject.toml", "poetry.lock"],
    Formatter.LICENSE: [LICENSE_FILE_NAME],
}
