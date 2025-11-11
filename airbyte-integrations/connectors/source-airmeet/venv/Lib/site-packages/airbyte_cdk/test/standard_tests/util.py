# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Utility and factory functions for testing Airbyte connectors."""

from pathlib import Path
from typing import Any, Literal

import yaml

from airbyte_cdk.test.standard_tests.connector_base import ConnectorTestSuiteBase
from airbyte_cdk.test.standard_tests.declarative_sources import (
    DeclarativeSourceTestSuite,
)
from airbyte_cdk.test.standard_tests.destination_base import DestinationTestSuiteBase
from airbyte_cdk.test.standard_tests.docker_base import DockerConnectorTestSuite
from airbyte_cdk.test.standard_tests.source_base import SourceTestSuiteBase
from airbyte_cdk.utils.connector_paths import (
    METADATA_YAML,
    find_connector_root_from_name,
)


def create_connector_test_suite(
    *,
    connector_name: str | None = None,
    connector_directory: Path | None = None,
) -> type[ConnectorTestSuiteBase]:
    """Get the test class for the specified connector name or path."""
    if connector_name and connector_directory:
        raise ValueError("Specify either `connector_name` or `connector_directory`, not both.")
    if not connector_name and not connector_directory:
        raise ValueError("Specify either `connector_name` or `connector_directory`.")

    if connector_name:
        connector_directory = find_connector_root_from_name(
            connector_name,
        )
    else:
        # By here, we know that connector_directory is not None
        # but connector_name is None. Set the connector_name.
        assert connector_directory is not None, "connector_directory should not be None here."
        connector_name = connector_directory.absolute().name

    metadata_yaml_path = connector_directory / METADATA_YAML
    if not metadata_yaml_path.exists():
        raise FileNotFoundError(
            f"Could not find metadata YAML file '{metadata_yaml_path}' relative to the connector directory."
        )
    metadata_dict: dict[str, Any] = yaml.safe_load(metadata_yaml_path.read_text())
    metadata_tags = metadata_dict["data"].get("tags", [])
    language_tags: list[str] = [tag for tag in metadata_tags if tag.startswith("language:")]
    if not language_tags:
        raise ValueError(
            f"Metadata YAML file '{metadata_yaml_path}' does not contain a 'language' tag. "
            "Please ensure the metadata file is correctly configured."
            f"Found tags: {', '.join(metadata_tags)}"
        )
    language = language_tags[0].split(":")[1]

    if language == "java":
        test_suite_class = DockerConnectorTestSuite
    elif language == "manifest-only":
        test_suite_class = DeclarativeSourceTestSuite
    elif language == "python" and connector_name.startswith("source-"):
        test_suite_class = SourceTestSuiteBase
    elif language == "python" and connector_name.startswith("destination-"):
        test_suite_class = DestinationTestSuiteBase
    else:
        raise ValueError(f"Unsupported language for connector '{connector_name}': {language}")

    subclass_overrides: dict[str, Any] = {
        "get_connector_root_dir": classmethod(lambda cls: connector_directory),
    }

    TestSuiteAuto = type(
        "TestSuiteAuto",
        (test_suite_class,),
        subclass_overrides,
    )

    return TestSuiteAuto
