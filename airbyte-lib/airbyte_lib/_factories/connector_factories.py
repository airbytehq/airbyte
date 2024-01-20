# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import Any

from airbyte_lib._executor import Executor, PathExecutor, VenvExecutor
from airbyte_lib.registry import get_connector_metadata
from airbyte_lib.source import Source


def get_connector(
    name: str,
    version: str | None = None,
    pip_url: str | None = None,
    config: dict[str, Any] | None = None,
    *,
    use_local_install: bool = False,
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
        use_local_install: whether to use a virtual environment to run the connector. If True, the
            connector is expected to be available on the path (e.g. installed via pip). If False,
            the connector will be installed automatically in a virtual environment.
        install_if_missing: whether to install the connector if it is not available locally. This
            parameter is ignored if use_local_install is True.
    """
    metadata = get_connector_metadata(name)
    if use_local_install:
        if pip_url:
            raise ValueError("Param 'pip_url' is not supported when 'use_local_install' is True")
        if version:
            raise ValueError("Param 'version' is not supported when 'use_local_install' is True")
        executor: Executor = PathExecutor(
            metadata=metadata,
            target_version=version,
        )

    else:
        executor = VenvExecutor(
            metadata=metadata,
            target_version=version,
            install_if_missing=install_if_missing,
            pip_url=pip_url,
        )
    return Source(
        executor=executor,
        name=name,
        config=config,
    )
