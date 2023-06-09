#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import functools
import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from glob import glob
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

import git
import requests
import yaml
from ci_credentials import SecretsManager
from rich.console import Console

console = Console()

DIFFED_BRANCH = os.environ.get("DIFFED_BRANCH", "origin/master")
OSS_CATALOG_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"
CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"
SOURCE_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/source-"
DESTINATION_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/destination-"
THIRD_PARTY_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/third_party/"
SCAFFOLD_CONNECTOR_GLOB = "-scaffold-"


ACCEPTANCE_TEST_CONFIG_FILE_NAME = "acceptance-test-config.yml"
AIRBYTE_DOCKER_REPO = "airbyte"
AIRBYTE_REPO_DIRECTORY_NAME = "airbyte"
GRADLE_PROJECT_RE_PATTERN = r"project\((['\"])(.+?)\1\)"
TEST_GRADLE_DEPENDENCIES = ["testImplementation", "integrationTestJavaImplementation", "performanceTestJavaImplementation"]


def download_catalog(catalog_url):
    response = requests.get(catalog_url)
    return response.json()


OSS_CATALOG = download_catalog(OSS_CATALOG_URL)
METADATA_FILE_NAME = "metadata.yaml"
ICON_FILE_NAME = "icon.svg"


class ConnectorInvalidNameError(Exception):
    pass


class ConnectorVersionNotFound(Exception):
    pass


def get_connector_name_from_path(path):
    return path.split("/")[2]


def get_changed_acceptance_test_config(diff_regex: Optional[str] = None) -> Set[str]:
    """Retrieve the set of connectors for which the acceptance_test_config file was changed in the current branch (compared to master).

    Args:
        diff_regex (str): Find the edited files that contain the following regex in their change.

    Returns:
        Set[Connector]: Set of connectors that were changed
    """
    airbyte_repo = git.Repo(search_parent_directories=True)

    if diff_regex is None:
        diff_command_args = ("--name-only", DIFFED_BRANCH)
    else:
        diff_command_args = ("--name-only", f"-G{diff_regex}", DIFFED_BRANCH)

    changed_acceptance_test_config_paths = {
        file_path
        for file_path in airbyte_repo.git.diff(*diff_command_args).split("\n")
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX) and file_path.endswith(ACCEPTANCE_TEST_CONFIG_FILE_NAME)
    }
    return {Connector(get_connector_name_from_path(changed_file)) for changed_file in changed_acceptance_test_config_paths}


def get_gradle_dependencies_block(build_file: Path) -> str:
    """Get the dependencies block of a Gradle file.

    Args:
        build_file (Path): Path to the build.gradle file of the project.

    Returns:
        str: The dependencies block of the Gradle file.
    """
    contents = build_file.read_text().split("\n")
    dependency_block = []
    in_dependencies_block = False
    for line in contents:
        if line.strip().startswith("dependencies"):
            in_dependencies_block = True
            continue
        if in_dependencies_block:
            if line.startswith("}"):
                in_dependencies_block = False
                break
            else:
                dependency_block.append(line)
    dependencies_block = "\n".join(dependency_block)
    return dependencies_block


def parse_gradle_dependencies(build_file: Path) -> Tuple[List[Path], List[Path]]:
    """Parse the dependencies block of a Gradle file and return the list of project dependencies and test dependencies.

    Args:
        build_file (Path): _description_

    Returns:
        Tuple[List[Tuple[str, Path]], List[Tuple[str, Path]]]: _description_
    """

    dependencies_block = get_gradle_dependencies_block(build_file)

    project_dependencies: List[Tuple[str, Path]] = []
    test_dependencies: List[Tuple[str, Path]] = []

    # Find all matches for test dependencies and regular dependencies
    matches = re.findall(
        r"(testImplementation|integrationTestJavaImplementation|performanceTestJavaImplementation|implementation).*?project\(['\"](.*?)['\"]\)",
        dependencies_block,
    )
    if matches:
        # Iterate through each match
        for match in matches:
            dependency_type, project_path = match
            path_parts = project_path.split(":")
            path = Path(*path_parts)

            if dependency_type in TEST_GRADLE_DEPENDENCIES:
                test_dependencies.append(path)
            else:
                project_dependencies.append(path)
    return project_dependencies, test_dependencies


def get_all_gradle_dependencies(
    build_file: Path, with_test_dependencies: bool = True, found_dependencies: Optional[List[Path]] = None
) -> List[Path]:
    """Recursively retrieve all transitive dependencies of a Gradle project.

    Args:
        build_file (Path): Path to the build.gradle file of the project.
        found_dependencies (List[Path]): List of dependencies that have already been found. Defaults to None.

    Returns:
        List[Path]: All dependencies of the project.
    """
    if found_dependencies is None:
        found_dependencies = []
    project_dependencies, test_dependencies = parse_gradle_dependencies(build_file)
    all_dependencies = project_dependencies + test_dependencies if with_test_dependencies else project_dependencies
    for dependency_path in all_dependencies:
        if dependency_path not in found_dependencies and Path(dependency_path / "build.gradle").exists():
            found_dependencies.append(dependency_path)
            get_all_gradle_dependencies(dependency_path / "build.gradle", with_test_dependencies, found_dependencies)

    return found_dependencies


class ConnectorLanguage(str, Enum):
    PYTHON = "python"
    JAVA = "java"
    LOW_CODE = "low-code"


class ConnectorLanguageError(Exception):
    pass


@dataclass(frozen=True)
class Connector:
    """Utility class to gather metadata about a connector."""

    technical_name: str

    def _get_type_and_name_from_technical_name(self) -> Tuple[str, str]:
        if "-" not in self.technical_name:
            raise ConnectorInvalidNameError(f"Connector type and name could not be inferred from {self.technical_name}")
        _type = self.technical_name.split("-")[0]
        name = self.technical_name[len(_type) + 1 :]
        return _type, name

    @property
    def name(self):
        return self._get_type_and_name_from_technical_name()[1]

    @property
    def connector_type(self) -> str:
        return self._get_type_and_name_from_technical_name()[0]

    @property
    def documentation_file_path(self) -> Path:
        return Path(f"./docs/integrations/{self.connector_type}s/{self.name}.md")

    @property
    def icon_path(self) -> Path:
        file_path = self.code_directory / ICON_FILE_NAME
        return file_path

    @property
    def code_directory(self) -> Path:
        return Path(f"./airbyte-integrations/connectors/{self.technical_name}")

    @property
    def metadata_file_path(self) -> Path:
        return self.code_directory / METADATA_FILE_NAME

    @property
    def metadata(self) -> Optional[dict]:
        file_path = self.metadata_file_path
        if not file_path.is_file():
            return None
        return yaml.safe_load((self.code_directory / METADATA_FILE_NAME).read_text())["data"]

    @property
    def language(self) -> ConnectorLanguage:
        if Path(self.code_directory / self.technical_name.replace("-", "_") / "manifest.yaml").is_file():
            return ConnectorLanguage.LOW_CODE
        if Path(self.code_directory / "setup.py").is_file():
            return ConnectorLanguage.PYTHON
        try:
            with open(self.code_directory / "Dockerfile") as dockerfile:
                if "FROM airbyte/integration-base-java" in dockerfile.read():
                    return ConnectorLanguage.JAVA
        except FileNotFoundError:
            pass
        return None
        # raise ConnectorLanguageError(f"We could not infer {self.technical_name} connector language")

    @property
    def version(self) -> str:
        if self.metadata is None:
            return self.version_in_dockerfile_label
        return self.metadata["dockerImageTag"]

    @property
    def version_in_dockerfile_label(self) -> str:
        with open(self.code_directory / "Dockerfile") as f:
            for line in f:
                if "io.airbyte.version" in line:
                    return line.split("=")[1].strip()
        raise ConnectorVersionNotFound(
            """
            Could not find the connector version from its Dockerfile.
            The io.airbyte.version tag is missing.
            """
        )

    @property
    def release_stage(self) -> Optional[str]:
        return self.metadata.get("releaseStage") if self.metadata else None

    @property
    def allowed_hosts(self) -> Optional[List[str]]:
        return self.metadata.get("allowedHosts") if self.metadata else None

    @property
    def suggested_streams(self) -> Optional[List[str]]:
        return self.metadata.get("suggestedStreams") if self.metadata else None

    @property
    def acceptance_test_config_path(self) -> Path:
        return self.code_directory / ACCEPTANCE_TEST_CONFIG_FILE_NAME

    @property
    def acceptance_test_config(self) -> Optional[dict]:
        try:
            with open(self.acceptance_test_config_path) as acceptance_test_config_file:
                return yaml.safe_load(acceptance_test_config_file)
        except FileNotFoundError:
            logging.warning(f"No {ACCEPTANCE_TEST_CONFIG_FILE_NAME} file found for {self.technical_name}")
            return None

    @property
    def supports_normalization(self) -> bool:
        return self.metadata and self.metadata.get("normalizationConfig") is not None

    @property
    def normalization_repository(self) -> Optional[str]:
        if self.supports_normalization:
            return f"{self.metadata['normalizationConfig']['normalizationRepository']}"

    @property
    def normalization_tag(self) -> Optional[str]:
        if self.supports_normalization:
            return f"{self.metadata['normalizationConfig']['normalizationTag']}"

    def get_secret_manager(self, gsm_credentials: str):
        return SecretsManager(connector_name=self.technical_name, gsm_credentials=gsm_credentials)

    def __repr__(self) -> str:
        return self.technical_name

    @functools.lru_cache(maxsize=2)
    def get_local_dependencies_paths(self, with_test_dependencies: bool = True) -> Set[Path]:
        dependencies_paths = [self.code_directory]
        if self.language == ConnectorLanguage.JAVA:
            dependencies_paths += get_all_gradle_dependencies(
                self.code_directory / "build.gradle", with_test_dependencies=with_test_dependencies
            )
        return set(dependencies_paths)


def get_changed_connectors(
    modified_files: Optional[Set[Union[str, Path]]] = None, source: bool = True, destination: bool = True, third_party: bool = True
) -> Set[Connector]:
    """Retrieve a set of Connectors that were changed in the current branch (compared to master)."""
    if modified_files is None:
        airbyte_repo = git.Repo(search_parent_directories=True)
        modified_files = airbyte_repo.git.diff("--name-only", DIFFED_BRANCH).split("\n")

    prefix_to_check = []
    if source:
        prefix_to_check.append(SOURCE_CONNECTOR_PATH_PREFIX)
    if destination:
        prefix_to_check.append(DESTINATION_CONNECTOR_PATH_PREFIX)
    if third_party:
        prefix_to_check.append(THIRD_PARTY_CONNECTOR_PATH_PREFIX)

    changed_source_connector_files = {
        file_path
        for file_path in modified_files
        if any(file_path.startswith(prefix) for prefix in prefix_to_check) and SCAFFOLD_CONNECTOR_GLOB not in file_path
    }
    return {Connector(get_connector_name_from_path(changed_file)) for changed_file in changed_source_connector_files}


def get_all_released_connectors() -> Set:
    return {
        Connector(Path(metadata_file).parent.name)
        for metadata_file in glob("airbyte-integrations/connectors/**/metadata.yaml", recursive=True)
        if SCAFFOLD_CONNECTOR_GLOB not in metadata_file
    }
