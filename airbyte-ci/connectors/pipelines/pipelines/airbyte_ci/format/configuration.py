#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pipelines.airbyte_ci.format.consts import CACHE_MOUNT_PATH, LICENSE_FILE_NAME, Formatter
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)

FORMATTERS_CONFIGURATIONS = {
    # Run spotless on all java and gradle files.
    Formatter.JAVA: {
        "get_format_container_fn": format_java_container,
        "file_filter": ["**/*.java", "**/*.gradle"],
        "format_commands": ["mvn -f spotless-maven-pom.xml spotless:apply clean"],
    },
    # Run prettier on all json and yaml files.
    Formatter.JS: {
        "get_format_container_fn": format_js_container,
        "file_filter": ["**/*.json", "**/*.yaml", "**/*.yml"],
        "format_commands": [f"prettier --write . --list-different --cache --cache-location={CACHE_MOUNT_PATH}/.prettier_cache"],
    },
    # Add license header to java and python files. The license header is stored in LICENSE_SHORT file.
    Formatter.LICENSE: {
        "get_format_container_fn": format_license_container,
        "file_filter": ["**/*.java", "**/*.py"],
        "format_commands": [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {LICENSE_FILE_NAME} ."],
    },
    # Run isort and black on all python files.
    Formatter.PYTHON: {
        "get_format_container_fn": format_python_container,
        "file_filter": ["**/*.py"],
        "format_commands": [
            "poetry run isort --settings-file pyproject.toml .",
            "poetry run black --config pyproject.toml .",
        ],
    },
}
