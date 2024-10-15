# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
"""Destination utilities.

For usage examples, see the `airbyte.destinations` module documentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from airbyte_cdk.sql._executors.util import get_connector_executor
from airbyte_cdk.sql.destinations.base import Destination


if TYPE_CHECKING:
    from pathlib import Path


def get_destination(
    name: str,
    config: dict[str, Any] | None = None,
    *,
    version: str | None = None,
    pip_url: str | None = None,
    local_executable: Path | str | None = None,
    docker_image: str | bool | None = None,
    use_host_network: bool = False,
    install_if_missing: bool = True,
) -> Destination:
    """Get a connector by name and version.

    Args:
        name: connector name
        config: connector config - if not provided, you need to set it later via the set_config
            method.
        streams: list of stream names to select for reading. If set to "*", all streams will be
            selected. If not provided, you can set it later via the `select_streams()` or
            `select_all_streams()` method.
        version: connector version - if not provided, the currently installed version will be used.
            If no version is installed, the latest available version will be used. The version can
            also be set to "latest" to force the use of the latest available version.
        pip_url: connector pip URL - if not provided, the pip url will be inferred from the
            connector name.
        local_executable: If set, the connector will be assumed to already be installed and will be
            executed using this path or executable name. Otherwise, the connector will be installed
            automatically in a virtual environment.
        docker_image: If set, the connector will be executed using Docker. You can specify `True`
            to use the default image for the connector, or you can specify a custom image name.
            If `version` is specified and your image name does not already contain a tag
            (e.g. `my-image:latest`), the version will be appended as a tag (e.g. `my-image:0.1.0`).
        use_host_network: If set, along with docker_image, the connector will be executed using
            the host network. This is useful for connectors that need to access resources on
            the host machine, such as a local database. This parameter is ignored when
            `docker_image` is not set.
        install_if_missing: Whether to install the connector if it is not available locally. This
            parameter is ignored when local_executable is set.
    """
    return Destination(
        name=name,
        config=config,
        executor=get_connector_executor(
            name=name,
            version=version,
            pip_url=pip_url,
            local_executable=local_executable,
            docker_image=docker_image,
            use_host_network=use_host_network,
            install_if_missing=install_if_missing,
        ),
    )


def get_noop_destination() -> Destination:
    """Get a devnull (no-op) destination.

    This is useful for performance benchmarking of sources, without
    adding the overhead of writing data to a real destination.
    """
    return get_destination(
        "destination-dev-null",
        config={
            "test_destination": {
                "test_destination_type": "LOGGING",
                "logging_config": {
                    "logging_type": "FirstN",
                    "max_entry_count": 100,
                },
            }
        },
        docker_image=True,
    )


__all__ = [
    "get_destination",
    "get_noop_destination",
]
