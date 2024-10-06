#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Callable, List

from pipelines.airbyte_ci.format.consts import CACHE_MOUNT_PATH, LICENSE_FILE_NAME, Formatter
from pipelines.airbyte_ci.format.containers import (
    format_java_container,
    format_js_container,
    format_license_container,
    format_python_container,
)


@dataclass
class FormatConfiguration:
    """A class to store the configuration of a formatter."""

    formatter: Formatter
    file_filter: List[str]
    get_format_container_fn: Callable
    format_commands: List[str]


FORMATTERS_CONFIGURATIONS: List[FormatConfiguration] = [
    # Run spotless on all java and gradle files.
    FormatConfiguration(
        Formatter.JAVA,
        ["**/*.java", "**/*.kt", "**/*.gradle"],
        format_java_container,
        ["mvn -f spotless-maven-pom.xml --errors --batch-mode spotless:apply clean"],
    ),
    # Run prettier on all json and yaml files.
    FormatConfiguration(
        Formatter.JS,
        ["**/*.json", "**/*.yaml", "**/*.yml"],
        format_js_container,
        [f"prettier --write . --list-different --cache --cache-location={CACHE_MOUNT_PATH}/.prettier_cache"],
    ),
    # Add license header to java and python files. The license header is stored in LICENSE_SHORT file.
    FormatConfiguration(
        Formatter.LICENSE,
        ["**/*.java", "**/*.kt", "**/*.py"],
        format_license_container,
        [f"addlicense -c 'Airbyte, Inc.' -l apache -v -f {LICENSE_FILE_NAME} ."],
    ),
    # Run isort and black on all python files.
    FormatConfiguration(
        Formatter.PYTHON,
        ["**/*.py"],
        format_python_container,
        ["poetry run poe format"],
    ),
]
