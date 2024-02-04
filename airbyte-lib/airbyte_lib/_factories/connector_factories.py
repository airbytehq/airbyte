# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import difflib
import shutil
from pathlib import Path
from typing import Any

from numpy import short

from airbyte_lib import exceptions as exc
from airbyte_lib._executor import PathExecutor, VenvExecutor
from airbyte_lib.registry import ConnectorMetadata, get_all_source_names, get_connector_metadata
from airbyte_lib.source import Source


def _find_source_by_name(source_name: str) -> tuple[str | None, list[str] | None]:
    """Find a source by name, using fuzzy lookups if necessary.

    Returns a tuple with the following values:
    - The found source name if it exists.
    - A list of similar source names if the source does not exist.

    Usage:
    ```
    source_name, similar_source_names = _find_source("source-google-sheets")
    if source_name:
        print(f"Found source: {source_name}")
    else:
        print(f"Source not found. Did you mean one of these? {similar_source_names}")
    ```
    """
    all_source_names = get_all_source_names()
    short_name = source_name.replace("source-", "")
    if source_name in all_source_names:
        return short_name, None

    all_short_names = [
        connector_name.replace("source-", "")
        for connector_name in all_source_names
    ]
    if short_name in all_short_names:
        return short_name, None

    matches: list[str] = difflib.get_close_matches(
        word=short_name, possibilities=all_short_names, n=5, cutoff=0.6
    )
    return None, matches


def get_connector(
    name: str,
    version: str | None = None,
    pip_url: str | None = None,
    config: dict[str, Any] | None = None,
    *,
    local_executable: Path | str | None = None,
    install_if_missing: bool = True,
) -> Source:
    """Get a connector by name and version.

    Args:
        name: connector name
        version: connector version - if not provided, the currently installed version will be used.
            If no version is installed, the latest available version will be used. The version can
            also be set to "latest" to force the use of the latest available version.
        pip_url: connector pip URL - if not provided, the pip url will be inferred from the
            connector name.
        config: connector config - if not provided, you need to set it later via the set_config
            method.
        local_executable: If set, the connector will be assumed to already be installed and will be
            executed using this path or executable name. Otherwise, the connector will be installed
            automatically in a virtual environment.
        install_if_missing: Whether to install the connector if it is not available locally. This
            parameter is ignored when local_executable is set.
    """
    if local_executable:
        if pip_url:
            raise exc.AirbyteLibInputError(
                message="Param 'pip_url' is not supported when 'local_executable' is set."
            )
        if version:
            raise exc.AirbyteLibInputError(
                message="Param 'version' is not supported when 'local_executable' is set."
            )

        if isinstance(local_executable, str):
            if "/" in local_executable or "\\" in local_executable:
                # Assume this is a path
                local_executable = Path(local_executable).absolute()
            else:
                which_executable = shutil.which(local_executable)
                if which_executable is None:
                    raise FileNotFoundError(local_executable)
                local_executable = Path(which_executable).absolute()

        return Source(
            name=name,
            config=config,
            executor=PathExecutor(
                name=name,
                path=local_executable,
            ),
        )

    metadata: ConnectorMetadata | None = None
    try:
        metadata = get_connector_metadata(name)
    except exc.AirbyteConnectorNotRegisteredError:
        if not pip_url:
            # We don't have a pip url or registry entry, so we can't install the connector
            raise

    executor = VenvExecutor(
        name=name,
        metadata=metadata,
        target_version=version,
        pip_url=pip_url,
    )
    if install_if_missing:
        executor.ensure_installation()

    return Source(
        executor=executor,
        name=name,
        config=config,
    )


def _normalize_source_name(source_name: str) -> str:
    """Normalize a source name.

    All spaces or underscores will be normalized to dashes. For example, "google sheets" and
    "google_sheets" will normalize to "google-sheets". If the source name has the "source-" prefix,
    it will be removed. The source name will also be lower-cased.

    Args:
        source_name: source name

    Returns:
        str: normalized source name
    """
    return source_name.lower() \
        .replace("_", "-").replace(" ", "-") \
        .replace("source-", "")


def get_source(
    source_name: str,
    version: str | None = None,
    pip_url: str | None = None,
    config: dict[str, Any] | None = None,
    *,
    local_executable: Path | str | None = None,
    install_if_missing: bool = True,
) -> Source:
    """Get a source by name.

    All spaces or underscores will be normalized to dashes. For example, "google sheets" and
    "google_sheets" will normalize to "google-sheets". If an exact match is not found, a fuzzy
    lookup will be performed and an error will print that provides the closest-known matches.

    Args:
        source_name: source name. The name may in the format "source-<connector-name>" or just
            "<connector-name>". For example, "source-google-sheets" and "google-sheets" are both
            valid.

    Returns:
        Source: The created source object.

    Raises:
        AirbyteLibInputError: if the source is not found. The error message will include a list of
            similar source names if any are found.
    """
    normalized_short_name = _normalize_source_name(source_name)
    if normalized_short_name != source_name:
        print(f"Normalizing input '{source_name}' to source name '{normalized_short_name}'...")
        source_name = normalized_short_name

    found_source_name, similar_source_names = _find_source_by_name(source_name)
    if found_source_name is None:
        err_msg = f"Source '{source_name}' not found."
        if similar_source_names:
            err_msg += f" Did you mean one of these? {similar_source_names}"
        raise exc.AirbyteLibInputError(message=err_msg)

    return get_connector(
        f"source-{found_source_name}",
        version=version,
        pip_url=pip_url,
        config=config,
        local_executable=local_executable,
        install_if_missing=install_if_missing,
    )
