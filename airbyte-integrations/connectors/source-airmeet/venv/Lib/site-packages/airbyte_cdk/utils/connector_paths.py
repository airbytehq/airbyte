# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Resources and utilities for locating Airbyte Connectors."""

from contextlib import suppress
from pathlib import Path

ACCEPTANCE_TEST_CONFIG = "acceptance-test-config.yml"
MANIFEST_YAML = "manifest.yaml"
METADATA_YAML = "metadata.yaml"


def resolve_airbyte_repo_root(
    from_dir: Path,
) -> Path:
    """Resolve the Airbyte repository root directory.

    This function will resolve the Airbyte repository root directory based on the
    current working directory. If the current working directory is not within the
    Airbyte repository, it will look for the 'airbyte' or 'airbyte-enterprise'
    directory in the parent directories.

    Sibling directories are also considered, so if the working directory is '~/repos/airbyte-cdk',
    it will find the 'airbyte' directory in '~/repos/airbyte'. The 'airbyte' directory
    will be preferred over 'airbyte-enterprise' if both are present as sibling directories and
    neither is a parent directory.

    If we reach the root of the filesystem without finding the 'airbyte' directory,
    a FileNotFoundError will be raised.

    Raises:
        FileNotFoundError: If the Airbyte repository root directory cannot be found.
    """

    def _is_airbyte_repo_root(path: Path) -> bool:
        """Check if the given path is the Airbyte repository root."""
        return all(
            [
                (path.name == "airbyte" or path.name == "airbyte-enterprise"),
                (path / "airbyte-integrations").is_dir(),
            ]
        )

    def _find_in_adjacent_dirs(current_dir: Path) -> Path | None:
        """Check if 'airbyte' or 'airbyte-enterprise' exists as a sibling, parent, or child."""
        # Check parents
        parent_dir = current_dir.parent
        if _is_airbyte_repo_root(parent_dir):
            return parent_dir

        # Check siblings
        if _is_airbyte_repo_root(parent_dir / "airbyte"):
            return parent_dir / "airbyte"
        if _is_airbyte_repo_root(parent_dir / "airbyte-enterprise"):
            return parent_dir / "airbyte-enterprise"

        # Check children only if no "airbyte" or "airbyte-enterprise" in parent
        if not any(
            [
                "airbyte" in current_dir.parts,
                "airbyte-enterprise" in current_dir.parts,
            ]
        ):
            if _is_airbyte_repo_root(current_dir / "airbyte"):
                return current_dir / "airbyte"
            if _is_airbyte_repo_root(current_dir / "airbyte-enterprise"):
                return current_dir / "airbyte-enterprise"

        return None

    current_dir = from_dir.resolve().absolute()
    while current_dir != current_dir.parent:  # abort when we reach file system root
        if _is_airbyte_repo_root(current_dir):
            return current_dir

        found_dir = _find_in_adjacent_dirs(current_dir)
        if found_dir:
            return found_dir

        # Move up one directory
        current_dir = current_dir.parent

    raise FileNotFoundError(
        f"Could not find the Airbyte repository root directory. Current directory: {from_dir}"
    )


def resolve_connector_name_and_directory(
    connector_ref: str | Path | None = None,
) -> tuple[str, Path]:
    """Resolve the connector name and directory.

    This function will resolve the connector name and directory based on the provided
    reference. If no input ref is provided, it will look within the
    current working directory. If the current working directory is not a connector
    directory (e.g. starting with 'source-') and no connector name or path is provided,
    the process will fail.
    If ref is sent as a string containing "/" or "\\", it will be treated as a path to the
    connector directory.

    raises:
        ValueError: If the connector name or directory cannot be resolved.
        FileNotFoundError: If the connector directory does not exist or cannot be found.
    """
    connector_name: str | None = None
    connector_directory: Path | None = None

    # Resolve connector_ref to connector_name or connector_directory (if provided)
    if connector_ref:
        if isinstance(connector_ref, str):
            if "/" in connector_ref or "\\" in connector_ref:
                # If the connector name is a path, treat it as a directory
                connector_directory = Path(connector_ref)
            else:
                # Otherwise, treat it as a connector name
                connector_name = connector_ref
        elif isinstance(connector_ref, Path):
            connector_directory = connector_ref
        else:
            raise ValueError(
                "connector_ref must be a string or Path. "
                f"Received type '{type(connector_ref).__name__}': {connector_ref!r}",
            )

    if not connector_directory:
        if connector_name:
            connector_directory = find_connector_root_from_name(connector_name)
        else:
            cwd = Path().resolve().absolute()
            if cwd.name.startswith("source-") or cwd.name.startswith("destination-"):
                connector_directory = cwd
            else:
                raise ValueError(
                    "The 'connector' input must be provided if not "
                    "running from a connector directory. "
                    f"Could not infer connector directory from: {cwd}"
                )

    if not connector_name:
        connector_name = connector_directory.name

    if connector_directory:
        connector_directory = connector_directory.resolve().absolute()
    elif connector_name:
        connector_directory = find_connector_root_from_name(connector_name)
    else:
        raise ValueError(
            f"Could not infer connector_name or connector_directory from input ref: {connector_ref}",
        )

    return connector_name, connector_directory


def resolve_connector_name(
    connector_directory: Path,
) -> str:
    """Resolve the connector name.

    This function will resolve the connector name based on the provided connector directory.
    If the current working directory is not a connector directory
    (e.g. starting with 'source-'), the process will fail.

    Raises:
        FileNotFoundError: If the connector directory does not exist or cannot be found.
    """
    if not connector_directory:
        raise FileNotFoundError(
            "Connector directory does not exist or cannot be found. Please provide a valid "
            "connector directory."
        )
    connector_name = connector_directory.absolute().name
    if not connector_name.startswith("source-") and not connector_name.startswith("destination-"):
        raise ValueError(
            f"Connector directory '{connector_name}' does not look like a valid connector directory. "
            f"Full path: {connector_directory.absolute()}"
        )
    return connector_name


def find_connector_root(from_paths: list[Path]) -> Path:
    """Find the root directory of the connector."""
    for path in from_paths:
        # If we reach here, we didn't find the manifest file in any parent directory
        # Check if the manifest file exists in the current directory
        for parent in [path, *path.parents]:
            if (parent / METADATA_YAML).exists():
                return parent.absolute()
            if (parent / MANIFEST_YAML).exists():
                return parent.absolute()
            if (parent / ACCEPTANCE_TEST_CONFIG).exists():
                return parent.absolute()
            if parent.name == "airbyte_cdk":
                break

    raise FileNotFoundError(
        "Could not find connector root directory relative to the provided directories: "
        f"'{str(from_paths)}'."
    )


def find_connector_root_from_name(connector_name: str) -> Path:
    """Find the root directory of the connector from its name."""
    with suppress(FileNotFoundError):
        return find_connector_root([Path(connector_name)])

    # If the connector name is not found, check if we are in the airbyte monorepo
    # and try to find the connector root from the current directory.

    cwd: Path = Path().absolute()

    try:
        airbyte_repo_root: Path = resolve_airbyte_repo_root(cwd)
    except FileNotFoundError as ex:
        raise FileNotFoundError(
            "Could not find connector root directory relative and we are not in the airbyte repo."
        ) from ex

    expected_connector_dir: Path = (
        airbyte_repo_root / "airbyte-integrations" / "connectors" / connector_name
    )
    if not expected_connector_dir.exists():
        raise FileNotFoundError(
            f"Could not find connector directory '{expected_connector_dir}' relative to the airbyte repo."
        )

    return expected_connector_dir
