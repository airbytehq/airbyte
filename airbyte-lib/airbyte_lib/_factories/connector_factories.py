# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import shutil
import warnings
from pathlib import Path
from typing import Any

from airbyte_lib import exceptions as exc
from airbyte_lib._executor import PathExecutor, VenvExecutor
from airbyte_lib.registry import ConnectorMetadata, get_connector_metadata
from airbyte_lib.source import Source


def get_connector(
    name: str,
    config: dict[str, Any] | None = None,
    *,
    version: str | None = None,
    pip_url: str | None = None,
    local_executable: Path | str | None = None,
    install_if_missing: bool = True,
) -> Source:
    """Deprecated. Use get_source instead."""
    warnings.warn(
        "The `get_connector()` function is deprecated and will be removed in a future version."
        "Please use `get_source()` instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return get_source(
        name=name,
        config=config,
        version=version,
        pip_url=pip_url,
        local_executable=local_executable,
        install_if_missing=install_if_missing,
    )


def get_source(
    name: str,
    config: dict[str, Any] | None = None,
    *,
    version: str | None = None,
    pip_url: str | None = None,
    local_executable: Path | str | None = None,
    install_if_missing: bool = True,
) -> Source:
    """Get a connector by name and version.

    Args:
        name: connector name
        config: connector config - if not provided, you need to set it later via the set_config
            method.
        version: connector version - if not provided, the currently installed version will be used.
            If no version is installed, the latest available version will be used. The version can
            also be set to "latest" to force the use of the latest available version.
        pip_url: connector pip URL - if not provided, the pip url will be inferred from the
            connector name.
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

        print(f"Using local `{name}` executable: {local_executable!s}")
        return Source(
            name=name,
            config=config,
            executor=PathExecutor(
                name=name,
                path=local_executable,
            ),
        )

    # else: we are installing a connector in a virtual environment:

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
