#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass, field
from pathlib import Path
from typing import FrozenSet, Set, Union

from connector_ops.utils import Connector  # type: ignore

from pipelines import main_logger
from pipelines.helpers.utils import IGNORED_FILE_EXTENSIONS, METADATA_FILE_NAME


def get_connector_modified_files(connector: Connector, all_modified_files: Set[Path]) -> FrozenSet[Path]:
    connector_modified_files = set()
    for modified_file in all_modified_files:
        modified_file_path = Path(modified_file)
        if modified_file_path.is_relative_to(connector.code_directory):
            connector_modified_files.add(modified_file)
    return frozenset(connector_modified_files)


def _is_connector_modified_directly(connector: Connector, modified_files: Set[Path]) -> bool:
    """Test if the connector is being impacted by file changes in the connector itself."""
    for file_path in modified_files:
        if _is_ignored_file(file_path):
            continue

        if Path(file_path).is_relative_to(Path(connector.code_directory)) or file_path == connector.documentation_file_path:
            main_logger.info(f"Adding connector '{connector}' due to connector file modification: {file_path}.")
            return True

    return False


def _is_connector_modified_indirectly(connector: Connector, modified_files: Set[Path]) -> bool:
    """Test if the connector is being impacted by file changes in the connector's dependencies."""
    connector_dependencies = connector.get_local_dependency_paths()

    for file_path in modified_files:
        if _is_ignored_file(file_path):
            continue

        for connector_dependency in connector_dependencies:
            if Path(file_path).is_relative_to(Path(connector_dependency)):
                main_logger.info(f"Adding connector '{connector}' due to dependency modification: '{file_path}'.")
                return True

    return False


def _is_ignored_file(file_path: Union[str, Path]) -> bool:
    """Check if the provided file has an ignored extension."""
    return Path(file_path).suffix in IGNORED_FILE_EXTENSIONS


def get_modified_connectors(modified_files: Set[Path], all_connectors: Set[Connector], dependency_scanning: bool) -> Set[Connector]:
    """Create a mapping of modified connectors (key) and modified files (value).
    If dependency scanning is enabled any modification to a dependency will trigger connector pipeline for all connectors that depend on it.
    It currently works only for Java connectors .
    It's especially useful to trigger tests of strict-encrypt variant when a change is made to the base connector.
    Or to tests all jdbc connectors when a change is made to source-jdbc or base-java.
    We'll consider extending the dependency resolution to Python connectors once we confirm that it's needed and feasible in term of scale.
    """
    modified_connectors = set()
    active_connectors = {conn for conn in all_connectors if conn.support_level != "archived"}
    main_logger.info(
        f"Checking for modified files. Skipping {len(all_connectors) - len(active_connectors)} connectors with support level 'archived'."
    )
    # Ignore files with certain extensions
    active_modified_files = {f for f in modified_files if not _is_ignored_file(f)}

    for connector in active_connectors:
        if _is_connector_modified_directly(connector, active_modified_files):
            modified_connectors.add(connector)
        elif dependency_scanning and _is_connector_modified_indirectly(connector, active_modified_files):
            modified_connectors.add(connector)

    return modified_connectors


@dataclass(frozen=True)
class ConnectorWithModifiedFiles(Connector):
    modified_files: FrozenSet[Path] = field(default_factory=frozenset)

    @property
    def has_metadata_change(self) -> bool:
        return any(path.name == METADATA_FILE_NAME for path in self.modified_files)
