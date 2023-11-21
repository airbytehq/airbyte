#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import FrozenSet, List, Optional, Set, Union

import dagger
import yaml
from anyio import Path
from connector_ops.utils import ConnectorLanguage
from pipelines import main_logger
from pipelines.helpers.utils import ACCEPTANCE_TEST_CONFIG_FILE_NAME, IGNORED_FILE_EXTENSIONS, METADATA_FILE_NAME


# TODO deser yaml metadata to pydantic mod
class RepoConnector:
    def __init__(
        self,
        metadata: dict,
        code_directory: dagger.Directory,
        relative_connector_path: str,
        code_directory_entries: List[str],
        acceptance_test_config: Optional[dict],
    ):
        self.metadata = metadata
        self.code_directory = code_directory
        self.relative_connector_path = relative_connector_path
        self.code_directory_entries = code_directory_entries
        self.acceptance_test_config = acceptance_test_config
        self._modified_files = []

    @classmethod
    async def load_from_directory(cls, relative_connector_path: str, code_directory: dagger.Directory):
        metadata_raw = await code_directory.file(METADATA_FILE_NAME).contents()
        code_directory_entries = await code_directory.entries()
        metadata = yaml.safe_load(metadata_raw)["data"]
        if ACCEPTANCE_TEST_CONFIG_FILE_NAME in code_directory_entries:
            acceptance_test_config_raw = await code_directory.file(ACCEPTANCE_TEST_CONFIG_FILE_NAME).contents()
            acceptance_test_config = yaml.safe_load(acceptance_test_config_raw)
        else:
            acceptance_test_config = None
        return RepoConnector(metadata, code_directory, relative_connector_path, code_directory_entries, acceptance_test_config)

    @property
    def modified_files(self):
        return self._modified_files

    @modified_files.setter
    def modified_files(self, modified_files: List[Path]):
        self._modified_files = modified_files

    @property
    def technical_name(self) -> str:
        return self.metadata["dockerRepository"].split("/")[-1]

    @property
    def tags(self):
        return {tag.split(":")[0]: tag.split(":")[1] for tag in self.metadata["tags"]}

    @property
    def language(self) -> ConnectorLanguage:
        if language := self.tags.get("language"):
            if language == "lowcode":
                return ConnectorLanguage("low-code")
            if language not in ["python", "java", "low-code"]:
                return None
            return ConnectorLanguage(language)

    @property
    def support_level(self) -> str:
        return self.metadata.get("supportLevel")

    @property
    def has_metadata_change(self) -> bool:
        return any(path.name == METADATA_FILE_NAME for path in self.modified_files)

    @property
    def version(self) -> str:
        return self.metadata["dockerImageTag"]

    @property
    def name(self) -> str:
        return self.metadata["name"]

    @property
    def is_using_poetry(self) -> bool:
        return "pyproject.toml" in self.code_directory_entries

    @property
    def icon(self) -> dagger.File:
        if "icon.svg" in self.code_directory_entries:
            return self.code_directory.file("icon.svg")


def get_connector_modified_files(connector: RepoConnector, all_modified_files: Set[Path]) -> FrozenSet[Path]:
    connector_modified_files = set()
    for modified_file in all_modified_files:
        modified_file_path = Path(modified_file)
        if modified_file_path.is_relative_to(connector.relative_connector_path):
            connector_modified_files.add(modified_file)
    return frozenset(connector_modified_files)


def _find_modified_connectors(
    file_path: Union[str, Path], all_connectors: Set[RepoConnector], dependency_scanning: bool = True
) -> Set[RepoConnector]:
    """Find all connectors impacted by the file change."""
    modified_connectors = set()

    for connector in all_connectors:
        if Path(file_path).is_relative_to(Path(connector.relative_connector_path)):
            main_logger.info(f"Adding connector '{connector}' due to connector file modification: {file_path}.")
            modified_connectors.add(connector)

        if dependency_scanning:
            for connector_dependency in connector.get_local_dependency_paths():
                if Path(file_path).is_relative_to(Path(connector_dependency)):
                    # Add the connector to the modified connectors
                    modified_connectors.add(connector)
                    main_logger.info(f"Adding connector '{connector}' due to dependency modification: '{file_path}'.")
    return modified_connectors


def _is_ignored_file(file_path: Union[str, Path]) -> bool:
    """Check if the provided file has an ignored extension."""
    return Path(file_path).suffix in IGNORED_FILE_EXTENSIONS


def get_modified_connectors(modified_files: Set[Path], all_connectors: Set[RepoConnector], dependency_scanning: bool) -> Set[RepoConnector]:
    """Create a mapping of modified connectors (key) and modified files (value).
    If dependency scanning is enabled any modification to a dependency will trigger connector pipeline for all connectors that depend on it.
    It currently works only for Java connectors .
    It's especially useful to trigger tests of strict-encrypt variant when a change is made to the base connector.
    Or to tests all jdbc connectors when a change is made to source-jdbc or base-java.
    We'll consider extending the dependency resolution to Python connectors once we confirm that it's needed and feasible in term of scale.
    """
    # Ignore files with certain extensions
    modified_connectors = set()
    for modified_file in modified_files:
        if not _is_ignored_file(modified_file):
            modified_connectors.update(_find_modified_connectors(modified_file, all_connectors, dependency_scanning))
    return modified_connectors
