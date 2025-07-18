#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import subprocess
from pathlib import Path
from typing import Any

import dagger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dagger import Container, Platform

from pipelines.airbyte_ci.connectors.build_image.steps.common import BuildConnectorImagesBase
from pipelines.airbyte_ci.connectors.context import ConnectorContext
from pipelines.dagger.actions.python.common import apply_python_development_overrides, with_python_connector_installed
from pipelines.models.steps import StepResult


class BuildConnectorImages(BuildConnectorImagesBase):
    """
    A step to build a Python connector image.
    A spec command is run on the container to validate it was built successfully.
    """

    context: ConnectorContext
    PATH_TO_INTEGRATION_CODE = "/airbyte/integration_code"

    async def _build_connector(self, platform: "Platform", *args: Any) -> "Container":
        if (
            "connectorBuildOptions" in self.context.connector.metadata
            and "baseImage" in self.context.connector.metadata["connectorBuildOptions"]
        ):
            return await self._build_from_base_image(platform)
        else:
            return await self._build_from_dockerfile(platform)

    def _get_base_container(self, platform: "Platform") -> "Container":
        return self.context.connector.base_image_version.get_container(platform)

    async def _create_builder_container(self, platform: "Platform") -> "Container":
        base_container = self._get_base_container(platform)
        user = await self.get_image_user(base_container)
        builder_container = with_python_connector_installed(
            self.context, base_container, str(self.context.connector.code_directory), user
        )
        return builder_container

    async def _build_from_base_image(self, platform: "Platform") -> "Container":
        """Build the connector container using the base image defined in the metadata, in the connectorBuildOptions.baseImage field.

        Returns:
            Container: The connector container built from the base image.
        """
        self.logger.info(f"Building connector from base image in metadata for {platform}")

        base_container = self.dagger_client.container(platform=platform).from_(
            self.context.connector.metadata["connectorBuildOptions"]["baseImage"]
        )
        user = await self.get_image_user(base_container)
        base_container = base_container.with_file(
            f"{self.PATH_TO_INTEGRATION_CODE}/main.py",
            (await self.context.get_connector_dir(include=["main.py"])).file("main.py"),
            owner=user,
        )
        base_container = base_container.with_directory(
            f"{self.PATH_TO_INTEGRATION_CODE}/{self.context.connector.technical_name.replace('-', '_')}",
            (await self.context.get_connector_dir()).directory(self.context.connector.technical_name.replace("-", "_")),
            owner=user,
        )
        connector_container = await apply_python_development_overrides(self.context, base_container, user)
        return connector_container

    async def _build_from_dockerfile(self, platform: "Platform") -> "Container":
        """Build the connector container using the Dockerfile in the connector directory.

        Returns:
            Container: The connector container built from the Dockerfile.
        """
        self.logger.info(f"Building connector from Dockerfile for {platform}")
        
        dockerfile_path = self.context.connector.code_directory / "Dockerfile"
        if not dockerfile_path.exists():
            raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")
        
        context_dir = await self.context.get_connector_dir()
        
        return (
            self.dagger_client.container(platform=platform)
            .build(
                context=context_dir,
                dockerfile="Dockerfile"
            )
        )


async def run_connector_build(context: ConnectorContext) -> StepResult:
    return await BuildConnectorImages(context).run()
