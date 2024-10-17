# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._executors.base import Executor


if TYPE_CHECKING:
    from pathlib import Path


class PathExecutor(Executor):
    def __init__(
        self,
        name: str | None = None,
        *,
        path: Path,
        target_version: str | None = None,
    ) -> None:
        """Initialize a connector executor that runs a connector from a local path.

        If path is simply the name of the connector, it will be expected to exist in the current
        PATH or in the current working directory.
        """
        self.path: Path = path
        name = name or path.name
        super().__init__(name=name, target_version=target_version)

    def ensure_installation(
        self,
        *,
        auto_fix: bool = True,
    ) -> None:
        """Ensure that the connector executable can be found.

        The auto_fix parameter is ignored for this executor type.
        """
        _ = auto_fix
        try:
            self.execute(["spec"])
        except Exception as e:
            raise exc.AirbyteConnectorExecutableNotFoundError(
                connector_name=self.name,
            ) from e

    def install(self) -> NoReturn:
        raise exc.AirbyteConnectorInstallationError(
            message="Connector cannot be installed because it is not managed by Airbyte.",
            connector_name=self.name,
        )

    def uninstall(self) -> NoReturn:
        raise exc.AirbyteConnectorInstallationError(
            message="Connector cannot be uninstalled because it is not managed by Airbyte.",
            connector_name=self.name,
        )

    @property
    def _cli(self) -> list[str]:
        """Get the base args of the CLI executable."""
        return [str(self.path)]
