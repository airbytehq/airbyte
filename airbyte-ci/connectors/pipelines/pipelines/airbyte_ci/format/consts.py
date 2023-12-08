#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from enum import Enum
from pipelines.helpers.git import find_all_git_ignore_rules


REPO_MOUNT_PATH = "/src"
CACHE_MOUNT_PATH = "/cache"

LICENSE_FILE_NAME = "LICENSE_SHORT"


DEFAULT_FORMAT_IGNORE_LIST = [
    "**/.git",
    "**/dbt-project-template",
    "**/dbt-project-template-mssql",
    "**/dbt-project-template-mysql",
    "**/dbt-project-template-oracle",
    "**/dbt-project-template-clickhouse",
    "**/dbt-project-template-snowflake",
    "**/dbt-project-template-tidb",
    "**/dbt-project-template-duckdb",
    "**/dbt_test_config",
    "**/normalization_test_output",
    "**/charts",  # Helm charts often have injected template strings that will fail general linting. Helm linting is done separately.
    "**/source-amplitude/unit_tests/api_data/zipped.json",  # Zipped file presents as non-UTF-8 making spotless sad
    "**/airbyte-ci/connectors/metadata_service/lib/tests/fixtures/**/invalid",  # These are deliberately invalid and unformattable.
    "**/tools/git_hooks/tests/test_spec_linter.py",
    "airbyte-ci/connectors/pipelines/tests/test_format/non_formatted_code",  # This is a test directory with badly formatted code
]

FORMAT_IGNORE_LIST = list(set(find_all_git_ignore_rules() + DEFAULT_FORMAT_IGNORE_LIST))

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
