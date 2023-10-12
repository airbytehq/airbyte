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
from pydash.objects import get
from rich.console import Console
from simpleeval import simple_eval

console = Console()

DIFFED_BRANCH = os.environ.get("DIFFED_BRANCH", "origin/master")
OSS_CATALOG_URL = "https://connectors.airbyte.com/files/registries/v0/oss_registry.json"
CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"
SOURCE_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/source-"
DESTINATION_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + "/destination-"

THIRD_PARTY_GLOB = "third-party"
THIRD_PARTY_CONNECTOR_PATH_PREFIX = CONNECTOR_PATH_PREFIX + f"/{THIRD_PARTY_GLOB}/"
SCAFFOLD_CONNECTOR_GLOB = "-scaffold-"


ACCEPTANCE_TEST_CONFIG_FILE_NAME = "acceptance-test-config.yml"
METADATA_FILE_NAME = "metadata.yaml"
AIRBYTE_DOCKER_REPO = "airbyte"
AIRBYTE_REPO_DIRECTORY_NAME = "airbyte"
GRADLE_PROJECT_RE_PATTERN = r"project\((['\"])(.+?)\1\)"
TEST_GRADLE_DEPENDENCIES = [
    "testImplementation",
    "testCompileOnly",
    "integrationTestJavaImplementation",
    "performanceTestJavaImplementation",
    "testFixturesCompileOnly",
    "testFixturesImplementation",
]


def download_catalog(catalog_url):
    response = requests.get(catalog_url)
    return response.json()


OSS_CATALOG = download_catalog(OSS_CATALOG_URL)
METADATA_FILE_NAME = "metadata.yaml"
ICON_FILE_NAME = "icon.svg"

IMPORTANT_CONNECTOR_THRESHOLDS = {
    "sl": 300,
    "ql": 400,
}

ALLOWED_HOST_THRESHOLD = {
    "ql": 300,
}


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
    return get_changed_file(ACCEPTANCE_TEST_CONFIG_FILE_NAME, diff_regex)


def get_changed_metadata(diff_regex: Optional[str] = None) -> Set[str]:
    """Retrieve the set of connectors for which the metadata file was changed in the current branch (compared to master).

    Args:
        diff_regex (str): Find the edited files that contain the following regex in their change.

    Returns:
        Set[Connector]: Set of connectors that were changed
    """
    return get_changed_file(METADATA_FILE_NAME, diff_regex)


def get_changed_file(file_name: str, diff_regex: Optional[str] = None) -> Set[str]:
    """Retrieve the set of connectors for which the given file was changed in the current branch (compared to master).

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
        if file_path.startswith(SOURCE_CONNECTOR_PATH_PREFIX) and file_path.endswith(file_name)
    }
    return {Connector(get_connector_name_from_path(changed_file)) for changed_file in changed_acceptance_test_config_paths}

def has_local_cdk_ref(build_file: Path) -> bool:
    """Return true if the build file uses the local CDK.

    Args:
        build_file (Path): Path to the build.gradle file of the project.

    Returns:
        bool: True if using local CDK.
    """
    contents = "\n".join(
        [
            # Return contents without inline code comments
            line.split("//")[0]
            for line in build_file.read_text().split("\n")
        ]
    )
    contents = contents.replace(" ", "")
    return "useLocalCdk=true" in contents


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

    project_dependencies: List[Path] = []
    test_dependencies: List[Path] = []

    # Find all matches for test dependencies and regular dependencies
    matches = re.findall(
        r"(compileOnly|testCompileOnly|testFixturesCompileOnly|testFixturesImplementation|testImplementation|integrationTestJavaImplementation|performanceTestJavaImplementation|implementation|api).*?project\(['\"](.*?)['\"]\)",
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

    # Dedupe dependencies:
    project_dependencies = list(set(project_dependencies))
    test_dependencies = list(set(test_dependencies))

    return project_dependencies, test_dependencies


def get_local_cdk_gradle_dependencies(with_test_dependencies: bool) -> List[Path]:
    """Recursively retrieve all transitive dependencies of a Gradle project.

    Args:
        with_test_dependencies: True to include test dependencies.

    Returns:
        List[Path]: All dependencies of the project.
    """
    base_path = Path("airbyte-cdk/java/airbyte-cdk")
    found: List[Path] = [base_path]
    for submodule in ["core", "db-sources", "db-destinations"]:
        found.append(base_path / submodule)
        project_dependencies, test_dependencies = parse_gradle_dependencies(base_path / Path(submodule) / Path("build.gradle"))
        found += project_dependencies
        if with_test_dependencies:
            found += test_dependencies
    return list(set(found))


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

    # Since first party project folders are transitive (compileOnly) in the
    # CDK, we always need to add them as the project dependencies.
    project_dependencies += get_local_cdk_gradle_dependencies(False)
    test_dependencies += get_local_cdk_gradle_dependencies(with_test_dependencies=True)

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
    def documentation_directory(self) -> Path:
        return Path(f"./docs/integrations/{self.connector_type}s")

    @property
    def documentation_file_path(self) -> Path:
        readme_file_name = f"{self.name}.md"
        return self.documentation_directory / readme_file_name

    @property
    def inapp_documentation_file_path(self) -> Path:
        readme_file_name = f"{self.name}.inapp.md"
        return self.documentation_directory / readme_file_name

    @property
    def migration_guide_file_name(self) -> str:
        return f"{self.name}-migrations.md"

    @property
    def migration_guide_file_path(self) -> Path:
        return self.documentation_directory / self.migration_guide_file_name

    @property
    def icon_path(self) -> Path:
        file_path = self.code_directory / ICON_FILE_NAME
        return file_path

    @property
    def code_directory(self) -> Path:
        return Path(f"./airbyte-integrations/connectors/{self.technical_name}")

    @property
    def has_dockerfile(self) -> bool:
        return (self.code_directory / "Dockerfile").is_file()

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
        if Path(self.code_directory / "setup.py").is_file() or Path(self.code_directory / "pyproject.toml").is_file():
            return ConnectorLanguage.PYTHON
        if Path(self.code_directory / "src" / "main" / "java").exists():
            return ConnectorLanguage.JAVA
        return None

    @property
    def version(self) -> Optional[str]:
        if self.metadata is None:
            return self.version_in_dockerfile_label
        return self.metadata["dockerImageTag"]

    @property
    def version_in_dockerfile_label(self) -> Optional[str]:
        if not self.has_dockerfile:
            return None
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
    def name_from_metadata(self) -> Optional[str]:
        return self.metadata.get("name") if self.metadata else None

    @property
    def support_level(self) -> Optional[str]:
        return self.metadata.get("supportLevel") if self.metadata else None

    def metadata_query_match(self, query_string: str) -> bool:
        """Evaluate a query string against the connector metadata.

        Based on the simpleeval library:
        https://github.com/danthedeckie/simpleeval

        Examples
        --------
        >>> connector.metadata_query_match("'s3' in data.name")
        True

        >>> connector.metadata_query_match("data.supportLevel == 'certified'")
        False

        >>> connector.metadata_query_match("data.ab_internal.ql >= 100")
        True

        Args:
            query_string (str): The query string to evaluate.

        Returns:
            bool: True if the query string matches the connector metadata, False otherwise.
        """
        try:
            matches = simple_eval(query_string, names={"data": self.metadata})
            return bool(matches)
        except Exception as e:
            # Skip on error as we not all fields are present in all connectors.
            logging.debug(f"Failed to evaluate query string {query_string} for connector {self.technical_name}, error: {e}")
            return False

    @property
    def ab_internal_sl(self) -> int:
        """Airbyte Internal Field.

        More info can be found here: https://www.notion.so/Internal-Metadata-Fields-32b02037e7b244b7934214019d0b7cc9

        Returns:
            int: The value
        """
        default_value = 100
        sl_value = get(self.metadata, "ab_internal.sl")

        if sl_value is None:
            logging.warning(
                f"Connector {self.technical_name} does not have a `ab_internal.sl` defined in metadata.yaml. Defaulting to {default_value}"
            )
            return default_value

        return sl_value

    @property
    def ab_internal_ql(self) -> int:
        """Airbyte Internal Field.

        More info can be found here: https://www.notion.so/Internal-Metadata-Fields-32b02037e7b244b7934214019d0b7cc9

        Returns:
            int: The value
        """
        default_value = 100
        ql_value = get(self.metadata, "ab_internal.ql")

        if ql_value is None:
            logging.warning(
                f"Connector {self.technical_name} does not have a `ab_internal.ql` defined in metadata.yaml. Defaulting to {default_value}"
            )
            return default_value

        return ql_value

    @property
    def is_important_connector(self) -> bool:
        """Check if a connector qualifies as an important connector.

        Returns:
            bool: True if the connector is a high value connector, False otherwise.
        """
        if self.ab_internal_sl >= IMPORTANT_CONNECTOR_THRESHOLDS["sl"]:
            return True

        if self.ab_internal_ql >= IMPORTANT_CONNECTOR_THRESHOLDS["ql"]:
            return True

        return False

    @property
    def requires_high_test_strictness_level(self) -> bool:
        """Check if a connector requires high strictness CAT tests.

        Returns:
            bool: True if the connector requires high test strictness level, False otherwise.
        """
        return self.ab_internal_ql >= IMPORTANT_CONNECTOR_THRESHOLDS["ql"]

    @property
    def requires_allowed_hosts_check(self) -> bool:
        """Check if a connector requires allowed hosts.

        Returns:
            bool: True if the connector requires allowed hosts, False otherwise.
        """
        return self.ab_internal_ql >= ALLOWED_HOST_THRESHOLD["ql"]

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

    @property
    def is_using_poetry(self) -> bool:
        return Path(self.code_directory / "pyproject.toml").exists()

    def get_secret_manager(self, gsm_credentials: str):
        return SecretsManager(connector_name=self.technical_name, gsm_credentials=gsm_credentials)

    def __repr__(self) -> str:
        return self.technical_name

    @functools.lru_cache(maxsize=2)
    def get_local_dependency_paths(self, with_test_dependencies: bool = True) -> Set[Path]:
        dependencies_paths = []
        if self.language == ConnectorLanguage.JAVA:
            dependencies_paths += get_all_gradle_dependencies(
                self.code_directory / "build.gradle", with_test_dependencies=with_test_dependencies
            )
        return sorted(list(set(dependencies_paths)))


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


def get_all_connectors_in_repo() -> Set[Connector]:
    """Retrieve a set of all Connectors in the repo.
    We globe the connectors folder for metadata.yaml files and construct Connectors from the directory name.

    Returns:
        A set of Connectors.
    """
    repo = git.Repo(search_parent_directories=True)
    repo_path = repo.working_tree_dir

    return {
        Connector(Path(metadata_file).parent.name)
        for metadata_file in glob(f"{repo_path}/airbyte-integrations/connectors/**/metadata.yaml", recursive=True)
        # HACK: The Connector util is not good at fetching metadata for third party connectors.
        # We want to avoid picking a connector that does not have metadata.
        if SCAFFOLD_CONNECTOR_GLOB not in metadata_file and THIRD_PARTY_GLOB not in metadata_file
    }


class ConnectorTypeEnum(str, Enum):
    source = "source"
    destination = "destination"


class SupportLevelEnum(str, Enum):
    certified = "certified"
    community = "community"
