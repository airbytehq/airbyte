# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import shutil
from typing import NoReturn

from airbyte_cdk.sql import exceptions as exc
from airbyte_cdk.sql._executors.base import Executor


class DockerExecutor(Executor):
    def __init__(
        self,
        name: str | None = None,
        *,
        executable: list[str],
        target_version: str | None = None,
    ) -> None:
        self.executable: list[str] = executable
        name = name or executable[0]
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
            assert (
                shutil.which("docker") is not None
            ), "Docker couldn't be found on your system. Please Install it."
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
        return self.executable
